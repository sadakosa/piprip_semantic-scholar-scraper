# semantic-scholar-scraper


## Setup and Running Instructions

**1. Setup Environment**
```
https://github.com/sadakosa/semantic-scholar-scraper.git

install python 
- sudo yum install -y python3-pip
- sudo yum install -y python3

To setup local environment:
- python -m venv env
- .\env\Scripts\activate
- pip install -r requirements.txt
- deactivate << to exit and enter another environment (e.g., if I have multiple python projects)

- set up config file and yaml
- set up logger and logs

- Install chrome on EC2: 

wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
sudo yum localinstall google-chrome-stable_current_x86_64.rpm

wget https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.126/linux64/chromedriver-linux64.zip
unzip chromedriver-linux64.zip
sudo mv chromedriver-linux64/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver



<!-- sudo mv chromedriver-linux64 /usr/local/bin/ -->
sudo chmod +x chromedriver-linux64

pip install selenium bs4 psycopg2-binary


# List and kill all Python processes
ps aux | grep python | grep -v grep | awk '{print $2}' | xargs -r kill -9


maybe 20million data points, 
30 mins, 100 data points, 1 server
so 20 million is 100k hours
100k hours divided by 100 servers

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