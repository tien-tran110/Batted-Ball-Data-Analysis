from matplotlib import pyplot as plt
import pandas as pd
import streamlit as st
import seaborn as sns
import plotly.graph_objects as go
import altair as alt

st.set_page_config(page_title="ATL Brave Baseball Data Dashboard",
                   page_icon=":baseball:",
                   layout="wide")
df = pd.read_csv("cleaned_baseball_data.csv")

with st.expander("Data Preview"):
    st.dataframe(df)
    st.write(df.describe())  


st.title("Baseball Data Analysis")
# Give an overview of the data
st.markdown("### Overview of the data that affect the outcome of a hit")

@st.cache_data
def get_correlation(use_container_width: bool):

    source = df[["LAUNCH_ANGLE", "EXIT_SPEED", "HIT_DISTANCE", "HANG_TIME", "HIT_SPIN_RATE", "PLAY_OUTCOME"]]

    # Create the chart with repeated row/column for multiple variables
    chart = alt.Chart(source).mark_circle().encode(
        alt.X(alt.repeat("column"), type="quantitative"),
        alt.Y(alt.repeat("row"), type="quantitative"),
        color="PLAY_OUTCOME:N"
    ).properties(
        width=150,
        height=150
    ).repeat(
        row=["LAUNCH_ANGLE", "EXIT_SPEED", "HIT_DISTANCE", "HANG_TIME", "HIT_SPIN_RATE"],
        column=["HIT_SPIN_RATE", "HANG_TIME", "HIT_DISTANCE", "EXIT_SPEED", "LAUNCH_ANGLE"]
    ).interactive()

    # Display the chart in Streamlit
    st.altair_chart(chart, use_container_width=use_container_width)

# Call the function
get_correlation(use_container_width=True)
st.write("**Summary:** Looking at the relationship between these important features that have an effect to the play outcomes, we can "
         "generate initial assumptions such that with the appropriate launch angle and exit speed, we can target the result of a hit. "
         "The launch angle and exit speed seem to be the two strongest features that affect the outcome since the hit distance, hang "
         "time, and hit spin rate are depend upon the value of launch angle and exit velocity. However, we can still see the correlation "
         "of these features to the play outcome (e.g home runs are often associated with longer hit distance, higher hit spin rate, and "
         "longer hang time).")

st.write("### A zoom in into the correlation of launch angle and exit speed to the outcomes")
@st.cache_data
def scatter_plot(use_container_width: bool):
    chart = alt.Chart(df).mark_circle(size=60).encode(
            x="LAUNCH_ANGLE",
            y="EXIT_SPEED",
            color="PLAY_OUTCOME",
            tooltip=["BATTER", "PITCHER", "LAUNCH_ANGLE", "EXIT_SPEED", "PLAY_OUTCOME"]
        ).interactive()
    
    # Display the chart
    st.altair_chart(chart, theme="streamlit", use_container_width=use_container_width)

scatter_plot(use_container_width=True)
st.markdown("""
#### Analysis:
**Outcomes**: The scatter plot shows a strong relationship between launch angle and exit speed for different play outcomes in baseball.
We can see that the desired outcomes are often clustered around the 0-35 degree launch angle with approximately 70-110 mph exit 
speed. Homeruns are almost always hit with an angle from 25 to 35 launch degrees associated with a velocity of 100-110 mph.
""")
"---"

st.write("### Differences in outcomes percentage by choosing the right launch angle")

# Allow filter to further investigate the range of launch angle
launch_angle_filter = st.slider("Select launch angle range", min_value=-50, max_value=50, value=(-50, 50))

# Filter the dataframe by the selected range
filtered_df = df[(df["LAUNCH_ANGLE"] >= launch_angle_filter[0]) & (df["LAUNCH_ANGLE"] <= launch_angle_filter[1])]

# Calculate the percentage of each outcome
outcome_counts = filtered_df["PLAY_OUTCOME"].value_counts().reset_index()
outcome_counts.columns = ["PLAY_OUTCOME", "COUNT"]
outcome_counts["PERCENTAGE"] = (outcome_counts["COUNT"] / outcome_counts["COUNT"].sum()) * 100  # Calculate percentage
# Format to two decimal places
outcome_counts["PERCENTAGE"] = outcome_counts["PERCENTAGE"].round(2)

@st.cache_data
def donut_chart(use_container_width: bool):
    # Create a chart using Altair
    chart = alt.Chart(outcome_counts).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="PERCENTAGE", type="quantitative"),  # Size of the slice
        color=alt.Color(field="PLAY_OUTCOME", type="nominal"),  # Color based on outcome
        tooltip=["PLAY_OUTCOME", "PERCENTAGE"]  # Show play outcome and count on hover
    ).properties(
        title="Percentage of Play Outcomes within Selected Launch Angle Range"
    )

    # Display the chart
    st.altair_chart(chart, theme=None, use_container_width=use_container_width)

donut_chart(use_container_width=True)

play_outcomes = df["PLAY_OUTCOME"].unique()
st.subheader("Investigate By Play Outcomes")
selected_outcome = st.selectbox("Select Play Outcome to Analyze", play_outcomes)

# Filter data by the selected play outcome
filtered_data = df[df["PLAY_OUTCOME"] == selected_outcome]

# Calculate average exit speed
avg_exit_speed = filtered_data["EXIT_SPEED"].mean() if not filtered_data.empty else 0

# Create a base chart with the filtered data
base = alt.Chart(filtered_data)

# Create a histogram for exit speed distribution
bar = base.mark_bar().encode(
    x=alt.X("EXIT_SPEED:Q", bin=True, axis=alt.Axis(title="Exit Speed (mph)")),
    y="count():Q",
    tooltip=["count()"]
)

# Add a rule to indicate the average exit speed
rule = base.mark_rule(color="red").encode(
    x=alt.X("mean(EXIT_SPEED):Q", title="Average Exit Speed"),
    size=alt.value(5)
)

# Combine bar chart and rule
chart = bar + rule

# Display the chart and average exit speed in Streamlit
st.metric(label="Average Exit Speed", value=f"{avg_exit_speed:.2f} mph")
st.subheader(f"Exit Speed Distribution of {selected_outcome}")
st.altair_chart(chart, use_container_width=True)

# Create tabs for chart and data
tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data"])

# Group by batter and count occurrences of the selected outcome
outcome_by_batter = filtered_data["BATTER"].value_counts().reset_index()
outcome_by_batter.columns = ["BATTER", "COUNT"]

# Group by pitcher and count occurrences of the selected outcome
outcome_by_pitcher = filtered_data["PITCHER"].value_counts().reset_index()
outcome_by_pitcher.columns = ["PITCHER", "COUNT"]

# Chart tab
with tab1:
    col1, col2 = st.columns(2)
    
    # Batter analysis
    with col1:
        if not filtered_data.empty:
            
            st.subheader(f"Top Batters with the Most {selected_outcome}s")
            fig, ax = plt.subplots()
            sns.barplot(data=outcome_by_batter.head(10), x="COUNT", y="BATTER", ax=ax)  # Show top 10 batters
            ax.set_xlabel("Count")
            ax.set_ylabel("Batter")
            ax.set_title(f"Top 10 Batters with the Most {selected_outcome}s")
            st.pyplot(fig)
        else:
            st.write(f"No records found for {selected_outcome}.")

    # Pitcher analysis
    with col2:
        if not filtered_data.empty:
            
            st.subheader(f"Top Pitchers with the Most {selected_outcome}s") 
            fig, ax = plt.subplots()  # Set figure size
            sns.barplot(data=outcome_by_pitcher.head(10), x="COUNT", y="PITCHER", ax=ax)  # Show top 10 pitchers
            ax.set_xlabel("Count")
            ax.set_ylabel("Pitcher")
            ax.set_title(f"Top 10 Pitchers with the Most {selected_outcome}s") 
            st.pyplot(fig)
        else:
            st.write(f"No records found for {selected_outcome}.")

# Data tab
with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"Data for {selected_outcome} occurrences by Batter")
        st.dataframe(outcome_by_batter)
    with col2:
        st.subheader(f"Data for {selected_outcome} occurrences by Pitcher")
        st.dataframe(outcome_by_pitcher)


st.text_area("Comment:", "Since the pitcher has some effect to the performance of the batter and "
             "vice versa. It is ideally to visualize the correlation between the duo to deprive more "
             "insight into the performance of a specific player against specific pitcher. However, as "
             "there is not enough data that pairs a specific batter to a coresponding pitcher, I "
             "decided to visualize the performce of top 10 batters and pitchers belong to a particular "
             "play outcomes. From the chart, we can also predict the likelihood of an outcome that might "
             "occur if the duo of batter and pitcher are matched in the future.")

st.divider()

# Function to draw to gauge metric
@st.cache_data
def plot_gauge(
    indicator_number, indicator_color, indicator_suffix, indicator_title, max_bound
):
    fig = go.Figure(
        go.Indicator(
            value=indicator_number,
            mode="gauge+number",
            domain={"x": [0, 1], "y": [0, 1]},
            number={
                "suffix": indicator_suffix,
                "font.size": 26,
            },
            gauge={
                "axis": {"range": [0, max_bound], "tickwidth": 1},
                "bar": {"color": indicator_color},
            },
            title={
                "text": indicator_title,
                "font": {"size": 28},
            },
        )
    )
    fig.update_layout(
        # paper_bgcolor="lightgrey",
        height=200,
        margin=dict(l=10, r=10, t=50, b=10, pad=8),
    )
    st.plotly_chart(fig, use_container_width=True)

# Define statistics
@st.cache_data
def calculate_stats(df):
    total_at_bats = len(df[df["PLAY_OUTCOME"] != "Sacrifice"])
    total_hits = len(df[df["PLAY_OUTCOME"].isin(["Single", "Double", "Triple", "HomeRun"])])
    singles = len(df[df["PLAY_OUTCOME"] == "Single"])
    doubles = len(df[df["PLAY_OUTCOME"] == "Double"])
    triples = len(df[df["PLAY_OUTCOME"] == "Triple"])
    home_runs = len(df[df["PLAY_OUTCOME"] == "HomeRun"])
    
    batting_average = total_hits / total_at_bats if total_at_bats > 0 else 0

    return {
        "At Bats": total_at_bats,
        "Hits": total_hits,
        "Singles": singles,
        "Doubles": doubles,
        "Triples": triples,
        "Home Runs": home_runs,
        "Batting Average": batting_average
    }

# Batter Stats 
col1, col2 = st.columns(2)
# Stats table
with col1:

    st.header("Batter Stats")
    
    # Group data by batter
    batter_groups = df.groupby("BATTER")
    batter_stats = []
    # Display stats for each batter
    for batter, group in batter_groups:
        stats = calculate_stats(group)
        stats["Batter"] = batter  # Add batter name to stats
        batter_stats.append(stats)

    # Convert to DataFrame and display as a table
    batter_stats_df = pd.DataFrame(batter_stats)
    # Display with column configuration
    st.dataframe(
        batter_stats_df,
        column_config={
            "Batting Average": st.column_config.NumberColumn(
                "Batting Average",
                format="%.3f"
            )
        },
        hide_index=True,
    )

# Metrics column
with col2:
    st.subheader("Overall Metrics")

    stat = calculate_stats(df)
    batting_avg = stat["Batting Average"]
    total_hit = stat["Hits"]
    total_homerun = stat["Home Runs"]
    singles = stat["Singles"]
    doubles = stat["Doubles"]
    triples = stat["Triples"]
    total_ab = stat["At Bats"]
    slugging_pc = (singles + doubles * 2 + triples * 3 + total_homerun * 4)/total_ab
    
    # Calculate average hitting distance
    avg_distance = df["HIT_DISTANCE"].mean()    
    max_distance = df["HIT_DISTANCE"].max()  

    # Calutate total batter
    total_batter = df["BATTER"].nunique()
    total_pitcher = df["PITCHER"].nunique()

    row1 = st.columns(3)
    row2 = st.columns(3)
    with row1[0]:
        plot_gauge(batting_avg, "#0068C9", "%", "Batting Average", 1)
    with row1[1]:
        plot_gauge(total_hit, "#FF8700", " H", "Total Hits", total_ab)
    with row1[2]:
        plot_gauge(total_homerun, "#FF2B2B", " HR", "Total Home Runs", total_hit)

    with row2[0]:
        plot_gauge(avg_distance, "#CF27F8", " feet", "Average Distance", max_distance)
    with row2[1]:
        plot_gauge(total_batter, "#29B09D", " players", "Total batter", total_batter + total_pitcher)
    with row2[2]:
        plot_gauge(slugging_pc, "#F8F227", " %", "SLP", 1)

@st.cache_data
def get_chart_batters(use_container_width: bool):

    # Sort by batting average and select the top 50 batters
    top_batters_df = batter_stats_df.sort_values(by="Batting Average", ascending=False).head(100)

    # Reshape the dataframe for stacked bar plot (melt)
    chart_data = top_batters_df.melt(id_vars=["Batter"], 
                                     value_vars=["Home Runs", "Singles", "Doubles", "Triples"], 
                                     var_name="Hit Type", value_name="Count")

    # Create the stacked bar chart
    chart = alt.Chart(chart_data).mark_bar().encode(
        x=alt.X("Batter:N", sort="-y", title="Batter"),  # Sort by y value for better visualization
        y=alt.Y("sum(Count):Q", title="Hit Count"),  # Sum of hit types
        color=alt.Color("Hit Type:N", title="Hit Type"),  # Different hit types
        tooltip=["Batter", "sum(Count)", "Hit Type"]  # Tooltip to display more information
    ).properties(
        width=800,
        height=500,
        title="Top 100 Batters by Batting Average"
    ).interactive()  # Enable chart interactivity

    # Display the chart
    st.altair_chart(chart, use_container_width=use_container_width)

# Call the function to display the chart
get_chart_batters(use_container_width=True)


