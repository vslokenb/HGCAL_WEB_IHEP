# HGCAL IHEP MAC Webpages

This repository contains the code for the CMS HGCAL IHEP MAC Webpages. 

## Local Running
Follow the instructions below to set up and run the webpage locally.

### Prerequisites

- Python 3.6 or higher
- `pip` (Python package installer)

### Steps to Run the Webpage locally

1. **Clone the Repository**  
   
   ```bash
   git clone https://github.com/Ziruiality/HGCAL_WEB_IHEP.git
   ```
3. **Navigate to the Project Directory and Set Up a Virtual Environment**

   ```bash
    cd HGCAL_WEB_IHEP
    python3 -m venv venv
    source venv/bin/activate
   ```
4. **Install Required Dependencies**

   ```bash
   pip install -r requirements.txt
   ```
5. **Run the Webpage**
   This will start a local server, and the webpage should be accessible at http://localhost:8501 in your browser.
   ```bash
   streamlit run IHEP_MAC_Bookkeeping/website.py
   ```
## Streamlit Cloud Deployment

This webpage has also been deployed to Streamlit Cloud. You can visit the following link to access the live webpage:

[HGCAL IHEP MAC Webpage](https://hgcalwebihep-tgpbgf9zcivmoknet5wva5.streamlit.app/)
