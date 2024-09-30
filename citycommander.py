import streamlit as st
import pandas as pd

# Function to load the Excel file and process College Name with filled field count
def load_and_process_excel(file):
    # Load the Excel file with the first row as header
    df = pd.read_excel(file, header=0)
    
    # College Name is in the first column (Column 0)
    df['College Name'] = df.iloc[:, 0].astype(str)
    
    # Drop rows where College Name is NaN
    df = df.dropna(subset=['College Name'])
    
    # Count the number of filled (non-empty) fields for each college
    df['Filled Fields Count'] = df.notna().sum(axis=1) - 1  # Subtract 1 to exclude the college name column
    
    return df

# Streamlit app
st.title('College Information Table Generator')

# Upload the Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type="xlsx")

if uploaded_file:
    # Load and process the Excel file
    processed_df = load_and_process_excel(uploaded_file)
    
    # Create a display list combining college name and the filled field count
    processed_df['College Display'] = processed_df['College Name'] + " (Fields Filled: " + processed_df['Filled Fields Count'].astype(str) + ")"
    
    # Let the user manually select the college from the formatted "College Display" column
    college_list = processed_df['College Display'].tolist()
    selected_college = st.selectbox("Select a college", college_list)
    
    # Filter the data for the selected college
    if selected_college:
        st.write(f"Details for {selected_college}:")
        
        # Get the college row for the selected college name
        college_data = processed_df[processed_df['College Display'] == selected_college].drop(columns=['College Display', 'Filled Fields Count'])
        
        # Filter out empty columns (only show columns where data is available)
        college_data = college_data.loc[:, college_data.notna().any()]
        
        # Display the filtered college data (show only rows where data is available)
        st.dataframe(college_data.T)  # Transpose for better readability
