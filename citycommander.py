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

# Function to load and process the Excel file
def load_and_process_excel(file):
    df = pd.read_excel(file)  # Read the uploaded file
    
    # Assume the first row is the header
    df.columns = df.iloc[0]  # Set the first row as the header
    df = df.drop(0)  # Drop the first row, which is now the header
    
    # Rename the columns based on the field mapping
    df.columns = [field_mapping.get(col, col) for col in df.columns]
    
    # Convert all columns to string to avoid pyarrow conversion issues
    df = df.astype(str)
    
    return df

# Streamlit app
st.title('Flexible College Information Table Generator')

# Upload the Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type="xlsx")

if uploaded_file:
    # Load and process the Excel file
    processed_df = load_and_process_excel(uploaded_file)
    
    # Display the processed dataframe
    st.write("Processed College Data:")
    st.dataframe(processed_df)
    
    # Optionally, allow the user to select a specific college for detailed view
    if "Name" in processed_df.columns:
        college_names = processed_df["Name"].dropna().unique()
        selected_college = st.selectbox("Select a college", college_names)
        
        if selected_college:
            college_data = processed_df[processed_df["Name"] == selected_college]
            st.write(f"Details for {selected_college}:")
            st.dataframe(college_data)
