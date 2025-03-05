DROP TABLE IF EXISTS images;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT,
    google_id TEXT UNIQUE,
    email TEXT,
    avatar_url TEXT
);

CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    uploaded_at timestamp NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);