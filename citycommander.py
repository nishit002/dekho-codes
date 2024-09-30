import streamlit as st
import pandas as pd
import docx
from io import BytesIO
import re
import base64

# Function to convert text to proper case, ignoring abbreviations
def proper_case_except_abbreviations(text):
    def capitalize_word(word):
        if word.isupper():  # Keep abbreviations in uppercase
            return word
        else:
            return word.capitalize()  # Capitalize only non-abbreviation words
    return ' '.join([capitalize_word(word) for word in re.split(r'(\W+)', text)])

# Function to load the predefined Excel file from a local path or URL
@st.cache_data
def load_predefined_excel():
    file_url = "https://raw.githubusercontent.com/your-github-username/dekho-codes/main/ALL_CCM_ALL_Template.xlsx"
    
    try:
        df = pd.read_excel(file_url, header=0)
        df['College Name'] = df.iloc[:, 0].astype(str)
        df = df.dropna(subset=['College Name'])
        df['Filled Fields Count'] = df.notna().sum(axis=1) - 1  # Exclude the college name column
        return df
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

# Function to create a Word document with a transposed table (with borders)
def create_transposed_word_table(college_data):
    doc = docx.Document()
    doc.add_heading('College Details', 0)
    
    table = doc.add_table(rows=len(college_data.columns), cols=2)  # Transpose: Rows = number of columns in original data
    table.style = 'Table Grid'
    
    for i, col in enumerate(college_data.columns):
        table.rows[i].cells[0].text = col
        table.rows[i].cells[1].text = str(college_data[col].values[0])
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Function to create a transposed HTML table
def create_transposed_html_table(college_data):
    transposed_df = college_data.T
    html_table = transposed_df.to_html(header=False, border=1)
    return html_table

# Streamlit app
st.title('College Information Table Generator')

# Load the predefined Excel file automatically
st.write("Loading predefined Excel file...")
processed_df = load_predefined_excel()

if processed_df is not None:
    processed_df['College Display'] = processed_df['College Name'] + " (Fields Filled: " + processed_df['Filled Fields Count'].astype(str) + ")"
    
    college_list = processed_df['College Display'].tolist()
    selected_college = st.selectbox("Select a college", college_list)

    if selected_college:
        st.write(f"Details for {selected_college}:")
        
        college_data = processed_df[processed_df['College Display'] == selected_college].drop(columns=['College Display', 'Filled Fields Count'])
        college_data = college_data.loc[:, college_data.notna().any()]
        
        st.dataframe(college_data.T)
        
        # Option to download the transposed college data as a Word file
        buffer_word = create_transposed_word_table(college_data)
        st.download_button(label="Download College Data as Word", data=buffer_word, file_name=f"{selected_college}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        
        # Option to download the transposed college data as HTML
        html_table = create_transposed_html_table(college_data)
        b64_html = base64.b64encode(html_table.encode()).decode()
        href_html = f'<a href="data:text/html;base64,{b64_html}" download="{selected_college}.html">Download College Data as HTML</a>'
        st.markdown(href_html, unsafe_allow_html=True)
        
        st.text_area("HTML Table (Copy this):", value=html_table, height=200)

