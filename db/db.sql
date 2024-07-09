CREATE TABLE Papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id TEXT NOT NULL UNIQUE,
    corpus_id TEXT,
    title TEXT NOT NULL,
    author TEXT,
    publication_date TEXT,
    abstract TEXT NOT NULL,
    search_term TEXT,
    num_hops INTEGER,
    url TEXT 
);

CREATE TABLE References (
    paper_id TEXT NOT NULL,
    reference_id TEXT NOT NULL,
    constraint fk_paper_id foreign key (paper_id) references Papers(paper_id),
    constraint fk_reference_id foreign key (reference_id) references Papers(paper_id),
    PRIMARY KEY (paper_id, reference_id)
);