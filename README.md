# semantic-scholar-scraper


## Setup and Running Instructions

**1. Setup Environment**
```
To setup local environment:
- python -m venv env
- .\env\Scripts\activate
- pip install -r requirements.txt
- deactivate << to exit and enter another environment (e.g., if I have multiple python projects)

- set up config file and yaml
- set up logger and logs


AWS RDS
username: postgres
pw: postgres
port: 5432

To run it
1. Create an EC2 instance from the image
2. Open the cmd of the EC2 instance using connect
3. Git clone the public repo  
4. pm2 start "python main.py"
--> pm2 list
--> pm2 delete 0

On Postgres
--> On command line: psql -h database-2.c5esewkagze1.ap-southeast-2.rds.amazonaws.com -p 5432 -d postgres -U postgres
--> In python code: connection = psycopg2.connect(database="dbname", user="postgres", password="postgres", host="hostname", port=5432), host is database-2.c5esewkagze1.ap-southeast-2.rds.amazonaws.com


```


## Old
```
Create a file api_key.yaml in persona/config and enter yosur api key as follows:
- OPENAI_API_KEY: your_api_key
- MONGODB_CONNECTION_STRING: connection_string

Create a folder called logs under conversation_logging
```