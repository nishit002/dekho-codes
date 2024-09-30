import streamlit as st
import pandas as pd
import docx
from io import BytesIO
import re

# Function to convert text to proper case, ignoring abbreviations
def proper_case_except_abbreviations(text):
    def capitalize_word(word):
        if word.isupper():  # Keep abbreviations in uppercase
            return word
        else:
            return word.capitalize()  # Capitalize only non-abbreviation words
    return ' '.join([capitalize_word(word) for word in re.split(r'(\W+)', text)])

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
    
    # Apply proper casing to the data (except abbreviations)
    df = df.applymap(lambda x: proper_case_except_abbreviations(x) if isinstance(x, str) else x)
    
    return df

# Function to download college data in Word format
def download_word(college_data):
    doc = docx.Document()
    doc.add_heading('College Details', 0)
    
    for col in college_data.columns:
        doc.add_heading(f'{col} ({college_data[col].dtype})', level=1)
        doc.add_paragraph(str(college_data[col].values[0]))
    
    # Create a BytesIO object and save the document into it
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    return buffer

# Streamlit app
st.title('College Information Table Generator with Download')

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
        
        # Display column names, types, and proper case details
        for col in college_data.columns:
            st.write(f"**{col}** (Type: {college_data[col].dtype})")
            st.write(college_data[col].values[0])
        
        # Transpose the DataFrame for display
        st.dataframe(college_data.T)  # Display in transposed format for readability
        
        # Option to download the college data as a Word file
        buffer = download_word(college_data)
        st.download_button(label="Download College Data as Word", data=buffer, file_name=f"{selected_college}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
