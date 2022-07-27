DROP TABLE IF EXISTS tasks;

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT,
    date REAL -- Date stored as Juliad day
);

INSERT INTO tasks (description, date) VALUES ('Task1', 2459788);
INSERT INTO tasks (description, date) VALUES ('Task2', 2459789);
INSERT INTO tasks (description, date) VALUES ('Task3', 2459790);
