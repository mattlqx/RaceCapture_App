CREATE TABLE IF NOT EXISTS session
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        notes TEXT NULL,
        date INTEGER NOT NULL);
        
CREATE TABLE IF NOT EXISTS datapoint
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        sample_id INTEGER NOT NULL);
        
CREATE INDEX IF NOT EXISTS datapoint_sample_id_index_id on datapoint(sample_id);

CREATE TABLE IF NOT EXISTS sample
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL);

CREATE INDEX IF NOT EXISTS sample_id_index_id on sample(id);
CREATE INDEX IF NOT EXISTS sample_session_id_index_id on sample(session_id);


CREATE TABLE channel
        (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
        units TEXT NOT NULL, min_value REAL NOT NULL, max_value REAL NOT NULL,
         smoothing INTEGER NOT NULL)
         
