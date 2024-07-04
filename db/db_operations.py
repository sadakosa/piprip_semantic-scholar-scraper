
def create_paper_table(db_client):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS papers (
        id SERIAL PRIMARY KEY,
        ss_id TEXT NOT NULL UNIQUE,
        title TEXT NOT NULL,
        abstract TEXT NOT NULL,
        url TEXT
    );
    """
    db_client.execute(create_table_query)
    db_client.commit()

def create_references_table(db_client):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS "references" (
        ss_id TEXT NOT NULL,
        reference_id TEXT NOT NULL,
        constraint fk_ss_id foreign key (ss_id) references papers(ss_id),
        constraint fk_reference_id foreign key (reference_id) references papers(ss_id),
        PRIMARY KEY (ss_id, reference_id)
    );
    """
    db_client.execute(create_table_query)
    db_client.commit()


def insert_paper(db_client, ss_id, title, abstract, url):
    if ss_id is None or title is None:
        # print("Invalid paper data")
        # print(ss_id, title, abstract, url)
        return
    
    if abstract is None:
        abstract = "No abstract available"
    
    # print(f"Inserting paper: {ss_id}")
    
    insert_query = """
    INSERT INTO papers (ss_id, title, abstract, url)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (ss_id) DO NOTHING;
    """
    db_client.execute(insert_query, (ss_id, title, abstract, url))
    db_client.commit()

def insert_reference(db_client, ss_id, reference_id):
    print(f"Inserting reference: {ss_id} -> {reference_id}")
    insert_query = """
    INSERT INTO "references" (ss_id, reference_id)
        VALUES (%s, %s)
        ON CONFLICT (ss_id, reference_id) DO NOTHING;
    """
    db_client.execute(insert_query, (ss_id, reference_id))
    db_client.commit()

def get_all_paper_ids(db_client):
    select_query = """
    SELECT id, ss_id, is_processed FROM papers
    ORDER BY id;
    """
    cursor = db_client.execute(select_query)
    return cursor.fetchall()

def checked_for_references_and_citations(db_client):
    insert_query = """
    ALTER TABLE papers ADD COLUMN is_processed BOOLEAN DEFAULT FALSE;
    """
    db_client.execute(insert_query)
    db_client.commit()

def update_is_processed(db_client, ss_id):
    update_query = """
    UPDATE papers
    SET is_processed = TRUE
    WHERE ss_id = %s;
    """
    db_client.execute(update_query, (ss_id,))
    db_client.commit()


