CREATE TABLE IF NOT EXISTS ideas (
    id INTEGER PRIMARY KEY,
    title TEXT,
    user_id INTEGER REFERENCES log_in_info
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    content TEXT,
    sent_at TEXT,
    user_id INTEGER REFERENCES log_in_info,
    idea_id INTEGER REFERENCES ideas
);
CREATE TABLE IF NOT EXISTS log_in_info (
    id INTEGER PRIMARY KEY,
    usernames varchar(50) UNIQUE,
    passwords varchar(10)
);