import streamlit as st
import pandas as pd
from io import BytesIO

# Function to read and extract the selected sheet from an Excel file, skipping the first row (header starts from second row)
def read_selected_sheet(file, sheet_name):
    try:
        # Read the selected sheet, skip the first row if header starts from second row
        df = pd.read_excel(file, sheet_name=sheet_name, header=1)
        st.success(f"Extracted '{sheet_name}' sheet from {file.name}")
        return df
    except Exception as e:
        st.error(f"Error processing file: {file.name} - {e}")
        return None

# Function to merge multiple DataFrames, including the file name as a column, and remove blank rows
def merge_files(files, selected_sheets, selected_headers):
    merged_df = pd.DataFrame()

    for i, file in enumerate(files):
        sheet_name = selected_sheets[i]
        df = read_selected_sheet(file, sheet_name)
        if df is not None:
            # Normalize headers
            df.columns = df.columns.str.strip().str.lower()

            # Debug: Check headers in each file
            st.write(f"Headers in {file.name}: {df.columns.tolist()}")

            # Get the selected headers (make sure they exist in the current file's sheet)
            available_headers = [col for col in df.columns if col in [header.lower() for header in selected_headers]]
            if not available_headers:
                st.warning(f"No matching columns found in {file.name} for selected headers.")
                continue

            # Filter the DataFrame to include only the selected headers
            df_filtered = df[available_headers]

            # Remove rows where all selected columns are blank
            df_filtered = df_filtered.dropna(how='all', subset=available_headers)

            # Add a column for the file name
            df_filtered['source_file'] = file.name

            # Add the filtered data to the merged DataFrame
            merged_df = pd.concat([merged_df, df_filtered], ignore_index=True)

    return merged_df

# Streamlit app interface
st.title('Custom Sheet Merger with Source File')

st.write("Upload multiple Excel files, select the sheet to merge for each file, and specify the columns to include. The file name from which the data is sourced will be included as an additional column.")

# Upload multiple files
uploaded_files = st.file_uploader("Choose Excel files", accept_multiple_files=True, type="xlsx")

if uploaded_files:
    # Collect all available sheet names for each uploaded file
    file_sheets = {}
    for file in uploaded_files:
        try:
            sheet_names = pd.ExcelFile(file).sheet_names
            file_sheets[file.name] = sheet_names
        except Exception as e:
            st.error(f"Error reading file {file.name}: {e}")

    # Dictionary to store user selections of sheets for each file
    selected_sheets = []

    # Display available sheets for each file and allow user to select one with radio buttons
    for file_name, sheets in file_sheets.items():
        st.write(f"**Select a sheet for file: {file_name}**")
        selected_sheet = st.radio(f"Available sheets in {file_name}", sheets, key=file_name)
        selected_sheets.append(selected_sheet)

    if selected_sheets:
        # If sheets have been selected, show the example of the first file's selected sheet
        df_example = pd.read_excel(uploaded_files[0], sheet_name=selected_sheets[0], header=1)
        # Normalize column names in the preview DataFrame
        df_example.columns = df_example.columns.str.strip().str.lower()
        st.write(f"Preview of the first file's '{selected_sheets[0]}' sheet (normalized column names):")
        st.dataframe(df_example)

        # Let the user select the headers they want to include in the final merged output
        selected_headers = st.multiselect("Select the columns to include", df_example.columns.tolist())

        if selected_headers:
            # Merge the files based on the selected sheet and headers
            merged_data = merge_files(uploaded_files, selected_sheets, selected_headers)

            if not merged_data.empty:
                st.write("Merged Data Preview:")
                st.dataframe(merged_data)

                # Save merged file
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    merged_data.to_excel(writer, index=False, sheet_name='Merged Data')

                output.seek(0)

                # Provide download link for the merged file
                st.download_button(
                    label="Download Merged Excel File",
                    data=output,
                    file_name="merged_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.warning("Please select at least one column to merge.")
