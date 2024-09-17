
### Key Features and Usage of the Updated Code:
1. **User Interaction**: Users can specify the years for the files they are uploading, choose specific colleges, and optionally select a course to focus on. They can further filter the data by Quota, Gender, and Seat Type.
2. **Dynamic Charting**: Uses Plotly to create interactive and visually appealing line charts that display the opening and closing rank changes for the selected parameters.
3. **Word Document Generation**: The application generates a Word document that includes both the data table and the Plotly chart. This is accomplished by saving the Plotly chart as an image directly into the Word file.
4. **Downloadable Content**: Users can download the generated Word document directly from the Streamlit application.

### Additional Notes:
- Make sure that the necessary libraries (`pandas`, `streamlit`, `plotly`, and `python-docx`) are installed in your environment.
- You may need to install additional packages for Plotly to export charts as images. This often requires the `kaleido` package:
  ```bash
  pip install kaleido
