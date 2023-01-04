SET TIME ZONE 'utc';

CREATE OR REPLACE function utc_now() returns timestamp as $$
    select now() at time zone 'utc';
$$ language sql;


CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,

    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE,
    name TEXT NOT NULL,
    hashed_password TEXT NOT NULL,
    permission_level INT NOT NULL DEFAULT 0,

    created_at TIMESTAMP DEFAULT utc_now()
);


CREATE TABLE IF NOT EXISTS user_settings (
    user_id TEXT PRIMARY KEY REFERENCES users ON DELETE CASCADE,
    theme TEXT DEFAULT 'light' NOT NULL,
    locale TEXT DEFAULT 'en-US' NOT NULL
);


CREATE TABLE IF NOT EXISTS rooms (
    id TEXT PRIMARY KEY,

    name TEXT NOT NULL,
    description TEXT,
    owner_id TEXT REFERENCES users ON DELETE NO ACTION ON UPDATE NO ACTION,
    type INT DEFAULT 0 NOT NULL,

    created_at TIMESTAMP DEFAULT utc_now()
);


CREATE TABLE IF NOT EXISTS room_members (
    user_id TEXT NOT NULL REFERENCES users ON DELETE CASCADE,
    room_id TEXT NOT NULL REFERENCES rooms ON DELETE CASCADE,
    permission_level INT NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, room_id),

    joined_at TIMESTAMP DEFAULT utc_now()
);


CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,

    content TEXT,
    room_id TEXT NOT NULL REFERENCES rooms ON DELETE CASCADE,
    author_id TEXT NOT NULL REFERENCES users ON DELETE NO ACTION ON UPDATE NO ACTION,
    type INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT utc_now()
);


CREATE TABLE IF NOT EXISTS links (
    id TEXT PRIMARY KEY,

    -- meta info (applies to all links)
    type INT DEFAULT 0 NOT NULL,  -- 0: room | 1: user
    entity_id TEXT NOT NULL,
    uses INT DEFAULT 0 NOT NULL,
    public BOOLEAN DEFAULT FALSE NOT NULL,

    -- room invite info (applies to only room links)
    user_id TEXT REFERENCES users ON DELETE NO ACTION ON UPDATE NO ACTION,
    max_uses INT DEFAULT 0 NOT NULL,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT utc_now()
);


CREATE TABLE IF NOT EXISTS relationships (
    type INT NOT NULL,  -- 0: friend | 1: block
    user_id TEXT NOT NULL REFERENCES users ON DELETE CASCADE,
    recipient_id TEXT NOT NULL REFERENCES users ON DELETE CASCADE,

    PRIMARY KEY (user_id, recipient_id),

    created_at TIMESTAMP DEFAULT utc_now()
);
