CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE IF NOT EXISTS threads (
    id INTEGER PRIMARY KEY,
    title TEXT,
    user_id INTEGER REFERENCES users
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    content TEXT,
    sent_at TEXT,
    user_id INTEGER REFERENCES users,
    thread_id INTEGER REFERENCES threads
);
CREATE TABLE IF NOT EXISTS log_in_info (
    usernames varchar(50) PRIMARY KEY,
    passwords varchar(10)
);