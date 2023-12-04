-- alexandria test database 1.0

-- test_user: testname / testpassword

--- test_admin: testname / password 

--- test_tag (for book-tag relation)

------------------------------------------------------------------------------------------

-- alexandria database 1.0


-- users 

------------------------------------------------------------------------------------------


--------- TABLE CREATION --------- 

CREATE TABLE Users (
    id INTEGER PRIMARY KEY,
    link_id TEXT UNIQUE NOT NULL,
    user_name TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    user_password TEXT NOT NULL,
    is_admin BOOLEAN NOT NULL,
    verified_email BOOLEAN NOT NULL
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
    mime_type TEXT NOT NULL
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


CREATE TABLE Access_codes (
    id INTEGER PRIMARY KEY,
    link_id TEXT UNIQUE NOT NULL, 
    created_at TEXT NOT NULL DEFAULT (STRFTIME('%Y-%m-%d %H:%M', 'NOW', 'localtime')),
    deactivated_at TEXT NOT NULL DEFAULT (STRFTIME('%Y-%m-%d %H:%M', 'NOW', 'localtime')),
    access_code TEXT UNIQUE NOT NULL,
    active INTEGER NOT NULL CHECK (active IN (0,1)) DEFAULT 0
);


--------- TABLE INSERTION --------- 


INSERT INTO Users (id, link_id, user_name, email, user_password, is_admin, verified_email)
VALUES (1, "60V38CHK6MWKGE1S6XJG", "testUser", "testUser@mail.com", "$pbkdf2-sha256$29000$grD2vjdG6B2jtLZ2DuE8xw$zyB/LXTOoix7Mp2zaSZQKKocpGelQqCQlqISs0qs9Ik", 0, 1);


INSERT INTO Users (id, link_id, user_name, email, user_password, is_admin, verified_email)
VALUES (2, "60R68DB46XH68RHRCGT0", "testUserAdmin", "testUserAdmin@mail.com", "$pbkdf2-sha256$29000$wjjHOMeYM.Zc6/1fSwnBmA$MWqfG9C0zNz/YFlz9WSXg9YXpsIWDR3yYS50eUYLnzQ", 1, 1);

INSERT INTO Tags (id, link_id, tag)
VALUES (1, "6SJKGD9J61K3AEB5CSJG", "test_tag");

INSERT INTO Books (id, link_id, title, release_year, completed, bookmarked, active, mime_type)
VALUES (1, "CHK32R9P70WK6EB160W0", "test_book", 1972, 0, 0, 0, "application/pdf");

INSERT INTO Booktags (book_id, tag_id)
VALUES (1, 1);