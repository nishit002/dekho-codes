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

# Function to load the Excel file, handle NaN and duplicate columns
def load_and_process_excel(file):
    # Load the Excel file with the first row as header
    df = pd.read_excel(file, header=0)
    
    # Handle NaN or unnamed column names by replacing them with 'Unnamed: X'
    df.columns = [f'Unnamed: {i}' if pd.isna(col) else col for i, col in enumerate(df.columns)]
    
    # Handle duplicate column names by appending a suffix to each duplicate
    df.columns = pd.io.parsers.ParserBase({'names': df.columns})._maybe_dedup_names(df.columns)
    
    # Extract columns D to L (which correspond to index 3 to 11)
    df = df.iloc[:, 3:12]  # Index is 0-based, so columns D to L are 3 to 11
    
    # Rename the columns based on the field mapping if applicable
    df.columns = [field_mapping.get(col, col) for col in df.columns]
    
    # Convert all columns to string to avoid pyarrow conversion issues
    df = df.astype(str)
    
    return df

# Streamlit app
st.title('Flexible College Information Table Generator (Handle Duplicates)')

# Upload the Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type="xlsx")

if uploaded_file:
    # Load and process the Excel file
    processed_df = load_and_process_excel(uploaded_file)
    
    # Display the processed dataframe
    st.write("Processed College Data (Columns D to L):")
    st.dataframe(processed_df)
    
    # Let the user manually select the column that contains the college name
    st.write("Columns found in the dataset:")
    columns = processed_df.columns.tolist()
    st.write(columns)  # Display the column names
    
    name_column = st.selectbox("Select the column for college names", columns)
    
    # Optionally, allow the user to select a specific college for detailed view
    if name_column in processed_df.columns:
        college_names = processed_df[name_column].dropna().unique()
        selected_college = st.selectbox("Select a college", college_names)
        
        if selected_college:
            college_data = processed_df[processed_df[name_column] == selected_college]
            st.write(f"Details for {selected_college}:")
            st.dataframe(college_data)

