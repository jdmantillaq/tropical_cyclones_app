
# Tropical Cyclones Visualization App

## Overview

This application provides visualization and analysis tools for tropical cyclones data. It utilizes data from the International Best Track Archive for Climate Stewardship (IBTrACS) and allows users to explore various aspects of tropical cyclones, including their paths, intensities, and other related information.

## Getting Started

To use this application, follow these steps:

1.  **Dependencies Installation**: Ensure you have the necessary Python libraries installed. You can install the required libraries using pip:
    
    Copy code
    
    `pip install pandas plotly dash dash-bootstrap-components requests dash-bootstrap-templates` 
    
2.  **Clone the Repository**: Clone this repository to your local machine:
    
    bashCopy code
    
    `git clone <repository_url>` 
    
3.  **Run the Application**: Navigate to the directory containing the application files and run the Python script:
    
    Copy code
    
    `python trop_app.py` 
    
4.  **Access the Application**: Open a web browser and go to `http://localhost:8335` to access the application.
    

## Features

-   **Global Map**: View tropical cyclones plotted on a map, color-coded by intensity category.
-   **Filtering**: Filter cyclones by basin, season, date range, and specific disturbances.
-   **Interactive Visualization**: Hover over cyclone markers to view detailed information including name, latitude, longitude, intensity, wind speed, pressure, and time.

## File Structure

-   `app.py`: Main Python script containing the Dash application.
-   `README.md`: Documentation file providing information about the application.
-   `data/ibtracs.since1980.list.v04r00.csv`: CSV file containing tropical cyclone data.
-   `requirements.txt`: Text file listing the required Python libraries and their versions.

## Data Source

The tropical cyclone data used in this application is sourced from the International Best Track Archive for Climate Stewardship (IBTrACS), available at [https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/](https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/).

----------

Feel free to adjust the content as needed, adding more details or sections as required.