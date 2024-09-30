import streamlit as st
import pandas as pd
import requests
from github import Github
import base64

# Google API credentials (already provided)
API_KEY = 'e95bf84d54ed60c1a0a67972df2ed85f608a33b3'
SEARCH_ENGINE_ID = 'e5ff9bd23eba146d2'

# GitHub credentials (replace with your own GitHub token and repo details)
GITHUB_TOKEN = "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"  # Replace with your GitHub personal access token
REPO_NAME = "nishit002/dekho-codes"  # Replace with your GitHub repo name (username/repo)

# Initialize GitHub object using your token
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# Function to search Google Custom Search API
def search_google(query):
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to save the file to GitHub
def save_file_to_github(file_name, file_content):
    try:
        # Encode file content to base64
        file_content_encoded = base64.b64encode(file_content).decode('utf-8')

        # Commit the file to the GitHub repository
        repo.create_file(
            path=f"results/{file_name}",  # Save the file in the 'results' directory
            message=f"Add {file_name}",
            content=file_content_encoded,
            branch="main"
        )
        st.success(f"File {file_name} successfully saved to GitHub!")
    except Exception as e:
        st.error(f"Error saving file to GitHub: {str(e)}")

# Streamlit app interface
st.title("File Upload, Google Search, and Save to GitHub")

# Upload file
uploaded_file = st.file_uploader("Upload Excel or CSV File", type=["xlsx", "csv"])

if uploaded_file is not None:
    # Read the file into a DataFrame
    if uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    st.write("File uploaded successfully!")
    st.dataframe(df.head())  # Display first few rows of the uploaded file

    # Example: Run a Google search based on each college's name and city
    st.write("Processing file...")

    results = []
    for idx, row in df.iterrows():
        if 'college_name' in row and 'city_name' in row:
            query = f"{row['college_name']} {row['city_name']} GetMyUni"
            search_result = search_google(query)

            # Extract the first result if available
            if search_result and 'items' in search_result:
                first_result = search_result['items'][0]
                results.append({
                    'College Name': row['college_name'],
                    'City': row['city_name'],
                    'Search Title': first_result.get('title'),
                    'Search Link': first_result.get('link')
                })
            else:
                results.append({
                    'College Name': row['college_name'],
                    'City': row['city_name'],
                    'Search Title': 'No result found',
                    'Search Link': ''
                })

    # Convert the results to a DataFrame
    result_df = pd.DataFrame(results)
    
    # Show the search results
    st.write("Google Search Results:")
    st.dataframe(result_df)

    # Save results to an Excel file
    output_file_name = "google_search_results.xlsx"
    result_df.to_excel(output_file_name, index=False)

    # Save the processed file to GitHub
    with open(output_file_name, 'rb') as f:
        file_content = f.read()
        save_file_to_github(output_file_name, file_content)
