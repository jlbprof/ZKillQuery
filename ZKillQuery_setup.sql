--
-- File generated with SQLiteStudio v3.4.17 on Sat Aug 2 17:45:25 2025
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: droppedItems
CREATE TABLE IF NOT EXISTS droppedItems (
    droppedID   INTEGER PRIMARY KEY AUTOINCREMENT
                        NOT NULL,
    typeID      INTEGER REFERENCES invTypes (typeID),
    flagID      INTEGER REFERENCES invFlags (flagID) 
                        NOT NULL,
    quantity    INTEGER NOT NULL,
    killmail_id INTEGER REFERENCES killmails (killmail_id) 
);


-- Table: invFlags
CREATE TABLE IF NOT EXISTS invFlags (
    flagID   INTEGER PRIMARY KEY,
    flagName TEXT    NOT NULL,
    flagText TEXT
);


-- Table: invTypes
CREATE TABLE IF NOT EXISTS invTypes (
    typeID      INTEGER PRIMARY KEY,
    typeName    TEXT    NOT NULL,
    description TEXT
);


-- Table: killmails
CREATE TABLE IF NOT EXISTS killmails (
    killmail_id   INTEGER PRIMARY KEY,
    time          TEXT,
    solarSystemID INTEGER REFERENCES solar_systems (solarSystemID),
    ship_type_id  INTEGER REFERENCES invTypes (typeID) 
);


-- Table: regions
CREATE TABLE IF NOT EXISTS regions (
    regionID   INTEGER PRIMARY KEY,
    regionName TEXT    NOT NULL
)
STRICT;


-- Table: solar_systems
CREATE TABLE IF NOT EXISTS solar_systems (
    solarSystemID   INTEGER PRIMARY KEY,
    regionID        INTEGER REFERENCES regions (regionID),
    solarSystemName TEXT    NOT NULL
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
