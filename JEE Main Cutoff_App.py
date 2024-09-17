import streamlit as st
import pandas as pd

def merge_dataframes(df1, df2, key_columns):
    # Merge the two dataframes based on the keys
    return pd.merge(df1, df2, on=key_columns, suffixes=('_Year1', '_Year2'))

def preprocess_dataframe(df):
    # Standardize column names to match between the two files if necessary
    df.rename(columns={
        'Institute': 'College Name',
        'Academic Program Name': 'Course Name',
        'Quota': 'Quota',
        'Seat Type': 'Seat Type',
        'Gender': 'Gender',
        'Opening Rank': 'Opening Rank',
        'Closing Rank': 'Closing Rank'
    }, inplace=True)
    return df

st.title('College Rank Comparison Tool')

# Upload the Excel files
file1 = st.file_uploader("Upload the first Excel file (Year 1)", type=["xlsx"])
file2 = st.file_uploader("Upload the second Excel file (Year 2)", type=["xlsx"])

if file1 and file2:
    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)

    # Preprocess dataframes (e.g., rename columns to standard names if needed)
    df1 = preprocess_dataframe(df1)
    df2 = preprocess_dataframe(df2)

    # Combine college names from both files for selection
    college_names = pd.concat([df1['College Name'], df2['College Name']]).unique()
    selected_college = st.selectbox('Select a College', college_names)

    # Optional course name selection
    if selected_college:
        course_names = pd.concat([
            df1[df1['College Name'] == selected_college]['Course Name'],
            df2[df2['College Name'] == selected_college]['Course Name']
        ]).unique()
        selected_course = st.selectbox('Select a Course (optional)', ['Any'] + list(course_names))

        # Filter data based on selections
        if selected_course and selected_course != 'Any':
            df1 = df1[(df1['College Name'] == selected_college) & (df1['Course Name'] == selected_course)]
            df2 =
