# ID Sampling Tool

This interactive Streamlit web application supports data scientists and researchers in generating randomized selections of unique numeric IDs from a master dataset — with **real-time exclusion and retention control**.

Unlike static sampling tools, this app enables **on-the-fly randomization** even as the researcher actively filters out IDs for exclusion. It’s ideal for workflows where selection criteria evolve during exploratory analysis, data cleaning, or operational constraints. 

Still have to keep refreshing the files manually though :/ but if anyone wants improve it feel free to do so.

*App created using Replit's Ai Agent


## Features

- **Upload Data Files**: Import your full ID pool, current selections, and excluded IDs
- **Control Your Sampling**: Specify sample size, set a random seed for reproducibility, and apply ID range filters
- **Validate Your Data**: Automatic checks for duplicates and conflicts between datasets
- **Export Results**: Download your final dataset in CSV or Excel format

## How to Use

1. Upload your Full ID Pool file (required)
2. Optionally upload Current Selections and Excluded IDs files
3. Set the number of new IDs to sample
4. Optionally set a random seed for reproducible results
5. Optionally apply ID range filters
6. Click "Run Sampling"
7. Review the results and download the final dataset

## File Formats

- Upload CSV or Excel files
- The first column of each file should contain the numeric IDs
- Other columns will be ignored

## Running the App

To run the application, execute the following command:

```bash
streamlit run app.py
```

The app will open in your default web browser at http://localhost:5000.