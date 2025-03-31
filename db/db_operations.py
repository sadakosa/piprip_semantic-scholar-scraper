# ====================================================================================================
# CREATE TABLE Queries
# ====================================================================================================

def create_paper_table(db_client):
    create_table_query = """
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
    """
    db_client.execute(create_table_query)
    db_client.commit()

# only for curate_db.py to port over to curated papers table
def create_paper_curated_table(db_client):
    print("Creating papers_curated table")
    create_table_query = """
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


# Add is 
# ====================================================================================================
# Insert Functions
# ====================================================================================================



# async def insert_paper(db_client, ss_id, title, abstract, url, search_term=None, num_hops=None):
#     if ss_id is None or title is None:
#         return
    
#     if abstract is None:
#         abstract = "No abstract available"
    
#     insert_query = """
#     INSERT INTO papers (ss_id, title, abstract, url, search_term, num_hops)
#         VALUES ($1, $2, $3, $4, $5, $6)
#         ON CONFLICT (ss_id) DO NOTHING;
#     """
#     try:
#         await db_client.execute(insert_query, (ss_id, title, abstract, url, search_term, num_hops))
#     except Exception as e:
#         print(f"Failed to insert paper {ss_id}: {e}")


def insert_paper(db_client, ss_id, title, abstract, url, search_term=None, num_hops=None):
    if ss_id is None or title is None:
        return
    
    if abstract is None:
        abstract = "No abstract available"
    
    insert_query = """
    INSERT INTO papers (ss_id, title, abstract, url, search_term, num_hops)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (ss_id) DO NOTHING;
    """
    try:
        db_client.execute(insert_query, (ss_id, title, abstract, url, search_term, num_hops))
        db_client.commit()
    except Exception as e:
        db_client.rollback()
        print(f"Failed to insert paper {ss_id}: {e}")


# async def insert_reference(db_client, ss_id, reference_id):
#     insert_reference_query = """
#     INSERT INTO "references" (ss_id, reference_id)
#         VALUES ($1, $2)
#         ON CONFLICT DO NOTHING;
#     """
#     try:
#         await db_client.execute(insert_reference_query, (ss_id, reference_id))
#     except Exception as e:
#         print(f"Failed to insert reference from {ss_id} to {reference_id}: {e}")


def insert_reference(db_client, ss_id, reference_id):
    # print(f"Inserting reference: {ss_id} -> {reference_id}")
    insert_query = """
    INSERT INTO "references" (ss_id, reference_id)
        VALUES (%s, %s)
        ON CONFLICT (ss_id, reference_id) DO NOTHING;
    """
    db_client.execute(insert_query, (ss_id, reference_id))
    db_client.commit()

def update_is_processed(db_client, ss_id):
    update_query = """
    UPDATE papers
    SET is_processed = TRUE
    WHERE ss_id = %s;
    """
    db_client.execute(update_query, (ss_id,))
    db_client.commit()

# only for curate_db.py to port over to curated papers table
def batch_insert_papers(db_client, papers):
    # if ss_id is None or title is None:
    #     return
    
    # if abstract is None:
    #     abstract = "No abstract available"
    
    insert_query = """
    INSERT INTO papers_curated (ss_id, title, abstract, url, search_term, num_hops)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (ss_id) DO NOTHING;
    """
    try:
        with db_client.cursor() as cursor:
            cursor.executemany(insert_query, papers)
        db_client.commit()
    except Exception as e:
        db_client.rollback()
        print(f"Failed to insert papers: {e}, search term: {papers[0][4]}")


# papers = [
#     ('ss_id_1', 'Cleaned Title 1', 'Cleaned Abstract 1', True),
#     ('ss_id_2', 'Cleaned Title 2', 'Cleaned Abstract 2', True),
#     ('ss_id_3', 'Cleaned Title 3', 'Cleaned Abstract 3', True),
#     # More records
# ]








# ====================================================================================================
# Select Functions
# ====================================================================================================


def get_all_paper_ids(db_client):
    select_query = """
    SELECT id, ss_id, is_processed FROM papers
    ORDER BY id;
    """
    cursor = db_client.execute(select_query)
    return cursor.fetchall()

def get_all_paper_ids_with_params(db_client, search_term, num_hops):
    select_query = """
    SELECT id, ss_id, is_processed 
    FROM papers
    WHERE search_term = %s AND num_hops = %s
    ORDER BY id;
    """
    try:
        with db_client.cursor() as cursor:
            cursor = db_client.execute(select_query, (search_term, num_hops))
            return cursor.fetchall()
    except Exception as e:
        db_client.rollback()
        print(f"Failed to get papers: {e}")
    


# only for curate_db.py to port over to curated papers table
def get_papers_for_search_term(db_client, search_term, num_papers):
    select_query = """
    SELECT ss_id, title, abstract, url, search_term, num_hops
    FROM papers
    WHERE search_term = %s AND num_hops = 0
    ORDER BY id ASC
    LIMIT %s;
    """
    try:
        with db_client.cursor() as cursor:
            cursor.execute(select_query, (search_term, num_papers))
            return cursor.fetchall()
    except Exception as e:
        print(f"Failed to get papers for search term {search_term}: {e}")
        return []

# [
#     (1, "Paper Title 1", "Abstract of Paper 1", "http://url1.com"),
#     (2, "Paper Title 2", "Abstract of Paper 2", "http://url2.com"),
#     (3, "Paper Title 3", "Abstract of Paper 3", "http://url3.com")
# ]

