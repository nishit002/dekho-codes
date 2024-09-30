import streamlit as st
import pandas as pd

# Define the field mapping based on the provided image (second column names)
field_mapping = {
    "Write the admission criteria for different courses": "Admission Criteria",
    "Attendance policy of the college": "Attendance Policy",
    "Relaxation of attendance %, if you are part of any society/club": "Attendance Relaxation",
    "Campus Area (Administrative Buildings)": "Campus Area",
    "Culture of Campus": "Campus Culture",
    "Number of canteens inside campus": "Canteens",
    "Types of Clubs & Societies": "Clubs & Societies",
    "Extra Curricular Activities": "Extra Curricular",
    "Faculty Pedigree (Department Wise)": "Faculty Profile",
    "Course-wise highest packages": "Highest Package",
    "Does low attendance affect eligibility for semester examinations?": "Impact of Low Attendance",
    "Upload the college/Institute brochure here": "Brochure",
    "Any exposure to international events?": "International Events",
    "Job roles offered for all the courses": "Job Roles",
    "Course-wise average package": "Average Package",
    "Course wise-lowest package": "Lowest Package",
    "Write the college name and location (Also please mention the local name)": "Name",
    "Best faculty names, their professional qualifications, experience and achievements": "Popular Faculty",
    "Scholarship offered": "Scholarship",
    "Top Companies for different courses": "Top Companies"
}

# Function to load and preview the Excel file
def load_and_preview_excel(file):
    # Read the Excel file without assuming any headers
    df = pd.read_excel(file, header=None)
    
    # Display the first few rows to understand the structure
    return df

# Streamlit app
st.title('Flexible College Information Table Generator')

# Upload the Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type="xlsx")

if uploaded_file:
    # Load and preview the Excel file
    raw_df = load_and_preview_excel(uploaded_file)
    
    # Display the first 5 rows of the data to preview
    st.write("Preview of the uploaded file:")
    st.dataframe(raw_df.head(10))  # Show the first 10 rows for context
    
    # Let the user select which row contains the headers (e.g., first, second row, etc.)
    header_row = st.number_input("Select the row number to use as headers (0-based index)", min_value=0, max_value=len(raw_df)-1, value=0)
    
    # Reload the dataframe with the selected header row
    df = pd.read_excel(uploaded_file, header=header_row)
    
    # Let the user manually select the column that contains the college name
    st.write("Columns found in the dataset:")
    columns = df.columns.tolist()
    st.write(columns)  # Display the column names
    
    name_column = st.selectbox("Select the column for college names", columns)
    
    # Rename the columns based on the field mapping if applicable
    df.columns = [field_mapping.get(col, col) for col in df.columns]
    
    # Convert all columns to string to avoid pyarrow conversion issues
    df = df.astype(str)
    
    # Display the processed dataframe
    st.write("Processed College Data:")
    st.dataframe(df)
    
    # Optionally, allow the user to select a specific college for detailed view
    if name_column in df.columns:
        college_names = df[name_column].dropna().unique()
        selected_college = st.selectbox("Select a college", college_names)
        
        if selected_college:
            college_data = df[df[name_column] == selected_college]
            st.write(f"Details for {selected_college}:")
            st.dataframe(college_data)

