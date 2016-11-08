ALTER TABLE channel add session_id INTEGER NOT NULL;
ALTER TABLE channel add sample_rate INTEGER NOT NULL;


INSERT INTO channel(name, units, min_value, max_value, smoothing, session_id, sample_rate) 
SELECT c.name, c.units, c.min_value, c.max_value, c.smoothing, s.id, 25 FROM channel c, session s;

DELETE FROM channel WHERE session_id IS NULL;


