CREATE TABLE pictures (
    id SERIAL,
    file_id TEXT,
    by_user INTEGER,
    file_url TEXT
);

CREATE INDEX on pictures(by_user);
