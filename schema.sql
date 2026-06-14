CREATE TABLE IF NOT EXISTS log_in_info (
    id INTEGER PRIMARY KEY,
    usernames varchar(50) UNIQUE,
    passwords TEXT
);

CREATE TABLE IF NOT EXISTS ideas (
    id INTEGER PRIMARY KEY,
    title TEXT,
    content TEXT,
    user_id INTEGER REFERENCES log_in_info(id)
);

CREATE TABLE IF NOT EXISTS threads (
    id INTEGER PRIMARY KEY,
    title TEXT,
    user_id INTEGER REFERENCES log_in_info(id)
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    content TEXT,
    sent_at TEXT,
    username TEXT REFERENCES log_in_info(usernames),
    user_id INTEGER REFERENCES log_in_info(id),
    thread_id INTEGER REFERENCES threads(id)
);