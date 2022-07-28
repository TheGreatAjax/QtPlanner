DROP TABLE IF EXISTS tasks;

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT (128) NOT NULL,
    notes TEXT (512),
    difficulty INTEGER,
    date REAL, -- Date stored as Julian day
    completed INTEGER DEFAULT 0 -- Boolean
);
