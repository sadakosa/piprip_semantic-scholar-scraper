# semantic-scholar-scraper

## Purpose
1. scrapes from search and references
2. Used to port over db

## Setup and Running Instructions

**1. Setup EC2 Instance Environment**
```
Based on SearchAndScrapeFinal image in ap-southeast-2, launch instance. Then on ssh, run the following.

1. GIT CLONE
git clone https://github.com/sadakosa/semantic-scholar-scraper.git
cd semantic-scholar-scraper


2. TO INSTALL PYTHON AND PIP
sudo yum install -y python3-pip python3


3. TO INSTALL CHROME AND CHROME DRIVER
wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
sudo yum localinstall google-chrome-stable_current_x86_64.rpm

wget https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.126/linux64/chromedriver-linux64.zip
unzip chromedriver-linux64.zip
sudo mv chromedriver-linux64/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver


4. PIP INSTALLATIONS
pip install -r requirements.txt
pip install selenium bs4 psycopg2-binary


5. Node js and NPM
sudo yum update -y
curl -sL https://rpm.nodesource.com/setup_21.x | sudo bash -
sudo yum install -y nodejs
sudo npm install -g pm2


6. SETUP CONFIG FILE AND YAML
PSQL_USER: postgres
PSQL_PASSWORD: postgres
PSQL_HOST: database-2.c5esewkagze1.ap-southeast-2.rds.amazonaws.com
PSQL_PORT: 5432

LOCAL_PSQL_USER: postgres
LOCAL_PSQL_PASSWORD: postgres
LOCAL_PSQL_HOST: localhost
LOCAL_PSQL_PORT: 5432

RDS_DB: TRUE


7. SETUP LOGGER AND LOGS
- In logger folder, create a logs folder

8. CONFIGURE THE START AND END SEARCH TERMS + PREVIOUS_HOP IN MAIN.PY

9. CONFIGURE WHETHER IT IS SCRAPING FROM THE SEARCH BAR OR VIA API

10. START PM2
pm2 start "python3 main.py"
pm2 save # so that the programs will start when the instance reboots

```


**2. Maintenance of Servers**
```
ssh -
# List and kill all Python processes
ps aux | grep python | grep -v grep | awk '{print $2}' | xargs -r kill -9

pm2 status
pm2 restart 1

git fetch
git reset --hard origin/main



# to find which search_terms have been processed
SELECT search_term, COUNT(*) AS count
FROM papers
WHERE is_processed = TRUE
GROUP BY search_term;



```

## Miscellaneous
```

On Postgres
--> On command line: psql -h database-2.c5esewkagze1.ap-southeast-2.rds.amazonaws.com -p 5432 -d postgres -U postgres
--> In python code: connection = psycopg2.connect(database="dbname", user="postgres", password="postgres", host="hostname", port=5432), host is database-2.c5esewkagze1.ap-southeast-2.rds.amazonaws.com



Connecting to ec2 ssh
- go to same folder as .pem key file
- chmod 400 semantic-scholar-key.pem
- ssh -i semantic-scholar-key.pem ec2-user@ec2-13-211-253-218.ap-southeast-2.compute.amazonaws.com
- sudo su - (to change to root user)
- exit
- logout

1: ec2-13-211-253-218.ap-southeast-2.compute.amazonaws.com
2: ec2-54-206-182-117.ap-southeast-2.compute.amazonaws.com
3: ec2-13-236-146-213.ap-southeast-2.compute.amazonaws.com
4: ec2-3-107-10-148.ap-southeast-2.compute.amazonaws.com
5: ec2-13-210-93-105.ap-southeast-2.compute.amazonaws.com
6: ec2-13-239-10-18.ap-southeast-2.compute.amazonaws.com
7: ec2-13-210-89-116.ap-southeast-2.compute.amazonaws.com
8: ec2-3-27-18-173.ap-southeast-2.compute.amazonaws.com
9: ec2-3-27-74-167.ap-southeast-2.compute.amazonaws.com
10: ec2-3-27-134-43.ap-southeast-2.compute.amazonaws.com


```


## Old
```
REMOVE EXISTING CHROMEDRIVER - sudo rm -f /usr/local/bin/chromedriver

Create a file api_key.yaml in persona/config and enter yosur api key as follows:
- OPENAI_API_KEY: your_api_key
- MONGODB_CONNECTION_STRING: connection_string

Create a folder called logs under conversation_logging
```