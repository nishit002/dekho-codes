import streamlit as st
import pandas as pd

# Function to load the Excel file and process College Name and College ID
def load_and_process_excel(file):
    # Load the Excel file with the first row as header
    df = pd.read_excel(file, header=0)
    
    # Extract College ID (Column C) and College Name (Column E)
    df = df.iloc[:, [2, 4]]  # Column C is index 2, Column E is index 4
    
    # Drop rows where College Name is NaN
    df = df.dropna(subset=[df.columns[1]])  # Drop rows with NaN in the College Name (Column E)
    
    # Convert College ID and College Name to strings and format as "College Name - ID - College ID"
    df['College Display'] = df[df.columns[1]] + " - ID - " + df[df.columns[0]].astype(str)
    
    return df

# Streamlit app
st.title('College Information Table Generator')

# Upload the Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type="xlsx")

if uploaded_file:
    # Load and process the Excel file
    processed_df = load_and_process_excel(uploaded_file)
    
    # Let the user manually select the college from the formatted "College Display" column
    college_list = processed_df['College Display'].tolist()
    selected_college = st.selectbox("Select a college", college_list)
    
    # Filter the data for the selected college
    if selected_college:
        st.write(f"Details for {selected_college}:")
        # Displaying the corresponding row with college details
        college_data = processed_df[processed_df['College Display'] == selected_college]
        st.dataframe(college_data.T)  # Transpose for better readability
