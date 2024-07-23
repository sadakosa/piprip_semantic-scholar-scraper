# semantic-scholar-scraper

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

```


**2. Maintenance of Servers**
```
# List and kill all Python processes
ps aux | grep python | grep -v grep | awk '{print $2}' | xargs -r kill -9

pm2 status
pm2 restart 1

git fetch
git reset --hard origin/main

```

## Miscellaneous
```

On Postgres
--> On command line: psql -h database-1.c5esewkagze1.ap-southeast-2.rds.amazonaws.com -p 5432 -d postgres -U postgres
--> In python code: connection = psycopg2.connect(database="dbname", user="postgres", password="postgres", host="hostname", port=5432), host is database-2.c5esewkagze1.ap-southeast-2.rds.amazonaws.com

```

## To port to curated papers table
```
CREATE TABLE IF NOT EXISTS papers (
        id SERIAL PRIMARY KEY,
        ss_id TEXT NOT NULL UNIQUE,
        title TEXT NOT NULL,
        abstract TEXT NOT NULL,
        search_term TEXT,
        num_hops INTEGER,
        url TEXT, 
        is_processed BOOLEAN DEFAULT FALSE
    );
CREATE TABLE IF NOT EXISTS papers_curated (
        id SERIAL PRIMARY KEY,
        ss_id TEXT NOT NULL UNIQUE,
        title TEXT NOT NULL,
        abstract TEXT NOT NULL,
        search_term TEXT,
        num_hops INTEGER,
        url TEXT, 
        is_processed BOOLEAN DEFAULT FALSE
    );
CREATE TABLE IF NOT EXISTS "references" (
        ss_id TEXT NOT NULL,
        reference_id TEXT NOT NULL,
        constraint fk_ss_id foreign key (ss_id) references papers(ss_id),
        constraint fk_reference_id foreign key (reference_id) references papers(ss_id),
        PRIMARY KEY (ss_id, reference_id)
    );

# add is_cleaned BOOLEAN DEFAULT FALSE
# change the name of the papers table to papers_uncurated
# change the name of the papers_curated table to papers

# change the name of the "references" table to references_uncurated
# create new references table that is connected to papers_curated table


```

## Old
```
REMOVE EXISTING CHROMEDRIVER - sudo rm -f /usr/local/bin/chromedriver

Create a file api_key.yaml in persona/config and enter yosur api key as follows:
- OPENAI_API_KEY: your_api_key
- MONGODB_CONNECTION_STRING: connection_string

Create a folder called logs under conversation_logging
```