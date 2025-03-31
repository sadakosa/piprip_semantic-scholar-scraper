# used to copy from 1 rds db to another
# completely separate from rest of document

from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.orm import sessionmaker
from global_methods import load_yaml_config

config = load_yaml_config('config/config.yaml')
rds_db = config['RDS_DB']

# Define source and target database URIs
source_db_uri = config['SOURCE_DB_URI']
target_db_uri = config['TARGET_DB_URI']

# Set up engines and sessions
source_engine = create_engine(source_db_uri)
target_engine = create_engine(target_db_uri)

SourceSession = sessionmaker(bind=source_engine)
TargetSession = sessionmaker(bind=target_engine)

source_session = SourceSession()
target_session = TargetSession()

# Reflect tables from source database
source_metadata = MetaData()
source_metadata.reflect(bind=source_engine)

papers_source = Table('papers', source_metadata, autoload_with=source_engine)
references_source = Table('references', source_metadata, autoload_with=source_engine)

# Reflect tables from target database
target_metadata = MetaData()
target_metadata.reflect(bind=target_engine)

papers_target = Table('papers', target_metadata, autoload_with=target_engine)
references_target = Table('references', target_metadata, autoload_with=target_engine)

# Copy papers table data where num_hops = 0
papers_data = source_session.execute(select(papers_source).where(papers_source.c.num_hops == 0)).fetchall()
target_session.execute(papers_target.insert(), papers_data)
target_session.commit()

# Get ss_id values of copied papers to filter references
ss_ids = [row['ss_id'] for row in papers_data]

# Copy references table data for the copied papers
references_data = source_session.execute(select(references_source).where(references_source.c.ss_id.in_(ss_ids))).fetchall()
target_session.execute(references_target.insert(), references_data)
target_session.commit()

# Close sessions
source_session.close()
target_session.close()
