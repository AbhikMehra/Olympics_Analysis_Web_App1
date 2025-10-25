import streamlit as st
import pandas as pd
import preprocessor, helper
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff
import scipy  # Required by plotly's distplot

# ------------------ DATA LOADING ------------------
df = pd.read_csv('athlete_events.csv')
region_df = pd.read_csv('noc_regions.csv')
df = preprocessor.preprocess(df, region_df)

# ------------------ SIDEBAR ------------------
st.sidebar.title("🏅 Olympics Analysis")
st.sidebar.image(
    "https://e7.pngegg.com/pngimages/1020/402/png-clipart-2024-summer-olympics-brand-circle-area-olympic-rings-olympics-logo-text-sport.png",
    use_container_width=True
)

user_menu = st.sidebar.radio(
    "Select an Option",
    ("Medal Tally", "Overall Analysis", "Country-wise Analysis", "Athlete wise Analysis")
)

# ============================================================
#                    MEDAL TALLY
# ============================================================
if user_menu == "Medal Tally":
    st.sidebar.header("Medal Tally")
    years, country = helper.country_year_list(df)

    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", country)

    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)

    if selected_year == "Overall" and selected_country == "Overall":
        st.title("Overall Medal Tally")
    elif selected_year != "Overall" and selected_country == "Overall":
        st.title(f"Medal Tally in {selected_year} Olympics")
    elif selected_year == "Overall" and selected_country != "Overall":
        st.title(f"{selected_country} Overall Performance")
    else:
        st.title(f"{selected_country} Performance in {selected_year} Olympics")

    st.table(medal_tally)

# ============================================================
#                    OVERALL ANALYSIS
# ============================================================
if user_menu == "Overall Analysis":
    editions = df["Year"].nunique() - 1
    cities = df["City"].nunique()
    sports = df["Sport"].nunique()
    events = df["Event"].nunique()
    athletes = df["Name"].nunique()
    nations = df["region"].nunique()

    st.title("Top Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Editions")
        st.title(editions)
    with col2:
        st.header("Hosts")
        st.title(cities)
    with col3:
        st.header("Sports")
        st.title(sports)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Events")
        st.title(events)
    with col2:
        st.header("Nations")
        st.title(nations)
    with col3:
        st.header("Athletes")
        st.title(athletes)

    # Nations over time
    nations_over_time = helper.data_over_time(df, "region")
    if not nations_over_time.empty:
        nations_over_time = nations_over_time.rename(columns={"Year": "Edition"})
        fig = px.line(
            nations_over_time,
            x="Edition",
            y="region",
            title="Participating Nations over the Years"
        )
        st.plotly_chart(fig)

    # Events over time
    events_over_time = helper.data_over_time(df, "Event")
    if not events_over_time.empty:
        events_over_time = events_over_time.rename(columns={"Year": "Edition"})
        fig = px.line(
            events_over_time,
            x="Edition",
            y="Event",
            title="Events over the Years"
        )
        st.plotly_chart(fig)

    # Athletes over time
    athlete_over_time = helper.data_over_time(df, "Name")
    if not athlete_over_time.empty:
        athlete_over_time = athlete_over_time.rename(columns={"Year": "Edition"})
        fig = px.line(
            athlete_over_time,
            x="Edition",
            y="Name",
            title="Athletes over the Years"
        )
        st.plotly_chart(fig)

    # Heatmap of Sports vs Year
    st.title("Number of Events over Time (for Each Sport)")
    pt = df.drop_duplicates(["Year", "Sport", "Event"]).pivot_table(
        index="Sport", columns="Year", values="Event", aggfunc="count"
    )
    if pt.empty:
        st.warning("No data available to display heatmap.")
    else:
        fig, ax = plt.subplots(figsize=(20, 20))
        ax = sns.heatmap(pt.fillna(0).astype(int), annot=True)
        st.pyplot(fig)

    # Most Successful Athletes
    st.title("Most Successful Athletes")
    sport_list = df["Sport"].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, "Overall")
    selected_sport = st.selectbox("Select a Sport", sport_list)
    x = helper.most_successful(df, selected_sport)
    st.table(x)

# ============================================================
#                    COUNTRY-WISE ANALYSIS
# ============================================================
if user_menu == "Country-wise Analysis":
    st.sidebar.title("Country-wise Analysis")
    country_list = df["region"].dropna().unique().tolist()
    country_list.sort()
    selected_country = st.sidebar.selectbox("Select a Country", country_list)

    # Medal Tally over years
    country_df = helper.yearwise_medal_tally(df, selected_country)
    if not country_df.empty:
        fig = px.line(
            country_df,
            x="Year",
            y="Medal",
            title=f"{selected_country} Medal Tally over the Years"
        )
        st.plotly_chart(fig)

    # Heatmap: Country vs Sports
    st.title(f"{selected_country} Excels in the Following Sports")
    pt = helper.country_event_heatmap(df, selected_country)
    if pt.empty:
        st.warning("No data available to display heatmap.")
    else:
        fig, ax = plt.subplots(figsize=(20, 20))
        ax = sns.heatmap(pt, annot=True)
        st.pyplot(fig)

    # Top 10 Athletes
    st.title(f"Top 10 Athletes of {selected_country}")
    top10_df = helper.most_successful_countrywise(df, selected_country)
    st.table(top10_df)

# ============================================================
#                    ATHLETE-WISE ANALYSIS
# ============================================================
if user_menu == "Athlete wise Analysis":
    athlete_df = df.drop_duplicates(subset=["Name", "region"])

    # Age Distribution
    x1 = athlete_df["Age"].dropna()
    x2 = athlete_df[athlete_df["Medal"] == "Gold"]["Age"].dropna()
    x3 = athlete_df[athlete_df["Medal"] == "Silver"]["Age"].dropna()
    x4 = athlete_df[athlete_df["Medal"] == "Bronze"]["Age"].dropna()

    fig = ff.create_distplot(
        [x1, x2, x3, x4],
        ["Overall Age", "Gold Medalist", "Silver Medalist", "Bronze Medalist"],
        show_hist=False,
        show_rug=False
    )
    fig.update_layout(autosize=False, width=1000, height=600)
    st.title("Distribution of Age")
    st.plotly_chart(fig)

    # Distribution of Age for Gold Medalists by Sport
    x = []
    name = []
    famous_sports = [
        "Basketball", "Judo", "Football", "Tug-Of-War", "Athletics", "Swimming",
        "Badminton", "Sailing", "Gymnastics", "Art Competitions", "Handball",
        "Weightlifting", "Wrestling", "Water Polo", "Hockey", "Rowing", "Fencing",
        "Shooting", "Boxing", "Taekwondo", "Cycling", "Diving", "Canoeing", "Tennis",
        "Golf", "Softball", "Archery", "Volleyball", "Synchronized Swimming",
        "Table Tennis", "Baseball", "Rhythmic Gymnastics", "Rugby Sevens",
        "Beach Volleyball", "Triathlon", "Rugby", "Polo", "Ice Hockey"
    ]

    for sport in famous_sports:
        temp_df = athlete_df[athlete_df["Sport"] == sport]
        x.append(temp_df[temp_df["Medal"] == "Gold"]["Age"].dropna())
        name.append(sport)

    fig = ff.create_distplot(x, name, show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=1000, height=600)
    st.title("Distribution of Age wrt Sports (Gold Medalists)")
    st.plotly_chart(fig)

    # Height vs Weight
    st.title("Height vs Weight")
    sport_list = df["Sport"].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, "Overall")
    selected_sport = st.selectbox("Select a Sport", sport_list)
    temp_df = helper.weight_v_height(df, selected_sport)
    if not temp_df.empty:
        fig, ax = plt.subplots()
        ax = sns.scatterplot(
            data=temp_df,
            x="Weight",
            y="Height",
            hue="Medal",
            style="Sex",
            s=60
        )
        st.pyplot(fig)

    # Men vs Women Participation
    st.title("Men vs Women Participation Over the Years")
    final = helper.men_vs_women(df)
    if not final.empty:
        fig = px.line(final, x="Year", y=["Male", "Female"], title="Men vs Women Participation")
        fig.update_layout(autosize=False, width=1000, height=600)
        st.plotly_chart(fig)
