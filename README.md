This repository contains a proof-of-concept Django web application. The application demonstrates the following:

- Data Upload: Users can upload a CSV file containing people data. The data is validated and then stored in the database.
- Data View: Users can view the uploaded data in a paginated table.
- Data Visualization: Users can view charts that aggregate the data (e.g., by gender and region). Chart data is cached using Redis to improve performance.

## Features
- Dependencies are managed using a virtual environment
- CSV file upload with data validation and bulk insertion.
- Paginated data display.
- Chart generation with caching via Redis.
- Logging of errors and warnings during data processing.
- Built with Django.
- 
## Components


- csv_utils.py: Contains logic for csv processing, validation, and bulk inserts. ALso contains logic for chart data aggregation 
- views.py: handles incomming requests and returning appropriate responses
- tests.py: Unit testing of csv data validation and upload. 

## Requirements

- Python
- Django (tested with Django 3.2)
- Redis (for caching chart data)
- Other dependencies are listed in `requirements.txt`

