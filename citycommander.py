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
    df = df.rename(columns=lambda x: x if df.columns.tolist().count(x) == 1 else f"{x}_{df.columns.tolist().index(x)}")
    
    # Extract columns C, D, and E (which correspond to index 2, 3, and 4)
    df = df.iloc[:, [2, 3, 4]]  # Extract College ID (C), College Name (E), and relevant columns
    
    # Rename the columns based on the field mapping if applicable
    df.columns = ['College ID', 'College Name', 'Additional Info']
    
    return df

# Streamlit app
st.title('Flexible College Information Table Generator (Select College)')

# Upload the Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type="xlsx")

if uploaded_file:
    # Load and process the Excel file
    processed_df = load_and_process_excel(uploaded_file)
    
    # Let the user manually select the college from the College Name column (Column E)
    college_names = processed_df['College Name'].dropna().unique()
    selected_college = st.selectbox("Select a college", college_names)
    
    # Filter the data for the selected college
    if selected_college:
        college_data = processed_df[processed_df['College Name'] == selected_college]
        
        # Append the College ID with College Name
        college_data['College Display'] = college_data['College Name'] + " (ID: " + college_data['College ID'] + ")"
        
        # Transpose the DataFrame for better display
        college_data = college_data.set_index('College Display').T
        
        # Display the transposed college data
        st.write(f"Details for {selected_college}:")
        st.dataframe(college_data)

