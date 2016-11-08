DROP TABLE IF EXISTS channel_migrate;

CREATE TABLE IF NOT EXISTS channel_migrate
        (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
        units TEXT NOT NULL, min_value REAL NOT NULL, max_value REAL NOT NULL,
         smoothing INTEGER NOT NULL,
         session_id INTEGER NOT NULL,
         sample_rate INTEGER NOT NULL);

INSERT INTO channel_migrate(name, units, min_value, max_value, smoothing, session_id, sample_rate) 
SELECT c.name, c.units, c.min_value, c.max_value, c.smoothing, s.id, 25 FROM channel c, session s;

DROP TABLE channel;

ALTER TABLE channel_migrate RENAME TO channel;



