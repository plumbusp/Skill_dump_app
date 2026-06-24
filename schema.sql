CREATE TABLE IF NOT EXISTS log_in_info (
    id INTEGER PRIMARY KEY,
    usernames varchar(50) UNIQUE,
    passwords TEXT,
    image BLOB
);

CREATE TABLE IF NOT EXISTS ideas (
    id INTEGER PRIMARY KEY,
    title TEXT,
    content TEXT,
    type_of_skill TEXT,
    user_id INTEGER REFERENCES log_in_info(id)
);

CREATE TABLE IF NOT EXISTS skill_types (
    id INTEGER PRIMARY KEY,
    names TEXT,
    user_id INTEGER REFERENCES log_in_info(id),
    UNIQUE (user_id, names)
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
    user_id INTEGER REFERENCES log_in_info(id),
    thread_id INTEGER REFERENCES threads(id)
);