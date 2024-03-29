"""
This is a script to pull data from 100 unstructured pdfs to create two tables. 

Data = Schedule for Electricity Service 
Statement of Market Supply Charge – Capacity (MSC CAP)

https://lite.coned.com/_external/cerates/elec_MSCCAPstatementPSC10.asp
"""

import re
import pandas as pd
import pdfplumber
import requests
import io

# Create empty final tables
final_table1 = pd.DataFrame()
final_table2 = pd.DataFrame()

# Create function to extract the Initial Effective Date
def extract_initial_effective_date(text):
    initial_effective_date_pattern = r"Initial\s+Effective\s+Date:\s*(\d{2}/\d{2}/\d{4})"
    initial_effective_date_match = re.search(initial_effective_date_pattern, text)
    if initial_effective_date_match:
        return initial_effective_date_match.group(1)
    return None

# Specify the desired SC values for table 2 
# because table 2 has blank column name for SC 
desired_sc_values = ['5 - Rates I and III', '5 - Rates II and IV **', '8 - Rates I and IV', '8 - Rates II and V **', '8 - Rate III **', '9 - Rates I and IV', '9 - Rates II and V **', '9 - Rate III **', '12 - Rates I and IV', '12 - Rates II and V **', '12 - Rate III **', '13 - Rates I and II **']

# Iterate over the PDFs
for i in range(1, 99):
    # Construct the PDF URL
    pdf_url = f"https://lite.coned.com/_external/cerates/documents/elecPSC10/StatMSCCAP-{i}.pdf"

    # Download the PDF content
    response = requests.get(pdf_url)
    pdf_content = response.content

    # Open the PDF content using pdfplumber
    with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()

    # Find the start and end positions of table 1 and table 2
    start1 = text.find("1 - Rate I")
    end1 = text.find("Charges assessed in dollars per kilowatt:")
    start2 = text.find("5 - Rates I and III")
    end2 = text.find("Charges assessed to Rider M customers based on ICAP tag per kilowatt:")

    # Extract table 1
    table1_text = text[start1:end1]

    # Split the table 1 text into rows
    rows1 = table1_text.strip().split("\n")

    # Find column names for table 1
    columns1 = ["SC", "NYC", "Westchester"]

    # Extract values for table 1
    data1 = []
    for row in rows1:
        values = re.split(r"\s+\$?\s+", row)
        data1.append(values)

    # Create the data frame for table 1
    df1 = pd.DataFrame(data1, columns=columns1)

    # Extract the Initial Effective Date for table 1
    initial_effective_date1 = extract_initial_effective_date(text)

    # Add Initial Effective Date as a separate column in table 1
    df1["Initial Effective Date"] = initial_effective_date1

    # Extract table 2
    table2_text = text[start2:end2]

    # Split the table 2 text into rows
    rows2 = table2_text.strip().split("\n")

    # Find column names for table 2
    columns2 = ["SC", "NYC", "Westchester"]

    # Extract values for table 2
    data2 = []
    for row in rows2:
        values = re.split(r"\s+\$?\s+", row)
        data2.append(values)

    # Create the data frame for table 2
    df2 = pd.DataFrame(data2, columns=columns2)

    # Extract the Initial Effective Date for table 2
    initial_effective_date2 = extract_initial_effective_date(text)

    # Add Initial Effective Date as a separate column in table 2
    df2["Initial Effective Date"] = initial_effective_date2

    # Filter rows in table 2 based on SC values
    df2 = df2[df2['SC'].isin(desired_sc_values)]

    # Append the tables to the final tables
    final_table1 = final_table1.append(df1, ignore_index=True)
    final_table2 = final_table2.append(df2, ignore_index=True)

# Save the final tables to separate Excel files
final_table1.to_excel("table1_final.xlsx", index=False)
final_table2.to_excel("table2_final.xlsx", index=False)
