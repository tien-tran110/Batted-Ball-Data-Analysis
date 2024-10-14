from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Data Preprocessing",
                   page_icon=":gear:",
                   layout="wide")

df = pd.read_excel(
    io="BattedBallData.xlsx",
    engine="openpyxl",
)

# Data Overview
st.write("### Data Overview")
st.write(df.head())  # Show the first few rows of data

# Check for missing values
st.write("### Missing Values")
st.write(df.isnull().sum())  # Check if there are missing values in each column

# Check for duplicates
st.write("### Duplicate Rows")
st.write(df.duplicated().sum())  # Check for duplicate rows

duplicates = df[df.duplicated(keep=False)]  # Display all duplicate rows
st.write("Duplicate Rows:")
st.write(duplicates)
# Remove duplicates, keeping the first occurrence
df = df.drop_duplicates(keep='first')
# Check for duplicates
st.write("### Duplicate Rows")
st.write(df.duplicated().sum())  # Check for duplicate rows


# Data type information
st.write("### Data Types")
st.write(df.dtypes)  # Display the data types of each column

df['GAME_DATE'] = df['GAME_DATE'].dt.date

# Detect outliers using simple statistical methods
st.write("### Outlier Detection")
st.write(df.describe())  # Provide a statistical summary of the data


unusual_launch_angles = df[(df['LAUNCH_ANGLE'] < -90) | (df['LAUNCH_ANGLE'] > 90)]
st.write("Unusual Launch Angles:")
st.write(unusual_launch_angles)

# Replace missing values with mean
df['HANG_TIME'] = df['HANG_TIME'].fillna(df['HANG_TIME'].mean())
df['HIT_SPIN_RATE'] = df['HIT_SPIN_RATE'].fillna(df['HIT_SPIN_RATE'].mean())

with st.expander("Data Preview"):
    st.dataframe(df)
    st.write(df.describe())  

st.write(df.isna().sum())  # Check missing values for all columns


def detect_outliers_iqr(data):
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return np.where((data < lower_bound) | (data > upper_bound))[0]

def visualize_outliers(data, column_name):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    ax1.boxplot(data)
    ax1.set_title(f'Box Plot of {column_name}')
    ax2.scatter(range(len(data)), data)
    ax2.set_title(f'Scatter Plot of {column_name}')
    st.pyplot(fig)


important_columns = ['EXIT_SPEED', 'LAUNCH_ANGLE', 'HIT_DISTANCE', 'HANG_TIME', 'HIT_SPIN_RATE']

for column in important_columns:

     # Detect IQR Outliers
    outliers_iqr = detect_outliers_iqr(df[column])
    st.write("Outliers detected using IQR:", df.iloc[outliers_iqr])

    # Visualize Outliers
    visualize_outliers(df[column], column)

# Export cleaned DataFrame
df.to_csv('cleaned_baseball_data.csv', index=False)
