-- alexandria database 1.0

-- PRAGMA foreign_keys = ON;

-- users 

CREATE TABLE Users (
    id INTEGER PRIMARY KEY,
    link_id TEXT UNIQUE NOT NULL,
    user_name TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    user_password TEXT NOT NULL
);

-- books 

CREATE TABLE Books (
    id INTEGER PRIMARY KEY,
    link_id TEXT UNIQUE NOT NULL,  -- added_at + random part
    title TEXT NOT NULL,
    added_at TEXT NOT NULL DEFAULT (STRFTIME('%Y-%m-%d %H:%M', 'NOW', 'localtime')),        -- change ?
    release_year INTEGER,
    completed INTEGER NOT NULL CHECK (completed IN (0,1)) DEFAULT 0,
    bookmarked INTEGER NOT NULL CHECK (bookmarked IN (0,1)) DEFAULT 0,
    active INTEGER NOT NULL CHECK (active IN (0,1)) DEFAULT 0,
    file_url TEXT DEFAULT '',
    mime_type TEXT
);


-- tags 

CREATE TABLE Tags (
    id INTEGER PRIMARY KEY,
    link_id TEXT UNIQUE NOT NULL, 
    tag TEXT NOT NULL UNIQUE
);


-- composite index assuming there will be more books for a given tag than vise versa
-- internal difference compound primary key vs composite index

CREATE TABLE Booktags (
    book_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY(book_id) REFERENCES Books(id),
    FOREIGN KEY(tag_id) REFERENCES Tag(id),
    PRIMARY KEY(tag_id, book_id)
);


-- authors 

/*
CREATE TABLE AUTHORS (
    id INTEGER PRIMARY KEY,
    name TEXT
)
*/


