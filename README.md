# HGCAL IHEP MAC Webpages

Please use the ***For deployment*** branch if customizing this to your MAC. ***Main*** branch has some customization which is TTU specific.
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
   Make sure to configure the file in `dbase_info/conn.yaml` to match the Postgres configruation at your MAC! The host machine *must* have read access to your database.

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

This webpage has been deployed to Streamlit Cloud. You can visit the following link to access the live webpage:

[HGCAL IHEP MAC Webpage on Streamlit Cloud](https://hgcalwebihep-tgpbgf9zcivmoknet5wva5.streamlit.app/)

## CERN Webserver Deployment

For the official production, the system is deployed on the CERN Webserver using the Platform-as-a-Service (PAAS) solution, managed through OKD (OpenShift Kubernetes Distribution).
[HGCAL IHEP MAC CERN Webpage](https://hgcal-hgcal-ihep-website.app.cern.ch/)
The CERN deployment runs as a containerized application, utilizing the Docker image available at:
[Docker Hub Repository](https://hub.docker.com/repository/docker/ziruiality/hgcal_web_ihep/general)


## Additional features

a. ***Weather station*** 

The cleanroom at TTU is configured to monitor pressure, temperature, humidity, and particle count in real time. Displays of this can be activated by changing the following flag to `True` in `IHEP_Bookkeeping/website.py`. This currently requires local storage of readout information, and is managed by the functions defined in `IHEP_Bookkeeping/plot_weather.py`. 

```
doWeather=False
```
Once active, a ****Weather Report**** tab will be available on the webpage.

b. ***Parts inventory***

Parts information by type can be found both on the main banner, as well as under the ****Module Status Summary**** tab on the webpage. This can be customized to suit the needs of any and all MACs, so feel free to reach out with requests.

c. ***Electrical QC summary***

Within the ****Module Status Summary**** tab, electrical QC summary plots can be made used the most recent test information, and filtered by assembly date. The current default is in early March. Summary IV curves and ADC mean and noise plots are currently generated. Expect updates to this section!

d. ***Grading***

Under the ****Module Assembly Check List**** tab, a drop down menu to view summarized information about any assembled (proto)module is available. Each module selection will return relevant grading information, provided the information is within the local database. IV grading is currently available using up to date criteria: electrical and assembly grading will soon follow.
