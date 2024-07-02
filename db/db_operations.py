
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
    insert_query = """
    CREATE TABLE IF NOT EXISTS papers (
        INSERT INTO papers (ss_id, title, abstract, url)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (ss_id) DO NOTHING;
    );
    """
    db_client.execute(insert_query, (ss_id, title, abstract, url))
    db_client.commit()

def insert_reference(db_client, ss_id, reference_id):
    insert_query = """
    INSERT INTO "references" (ss_id, reference_id)
        VALUES (%s, %s)
        ON CONFLICT (ss_id, reference_id) DO NOTHING;
    """
    db_client.execute(insert_query, (ss_id, reference_id))
    db_client.commit()