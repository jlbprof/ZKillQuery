--
-- File generated with SQLiteStudio v3.4.17 on Sat Aug 2 19:32:06 2025
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
    flagText TEXT,
    orderID  INTEGER
);


-- Table: invTypes
CREATE TABLE IF NOT EXISTS invTypes (
    typeID       INTEGER PRIMARY KEY,
    groupID      INTEGER,
    typeName     TEXT    NOT NULL,
    description  TEXT,
    mass         REAL,
    volume       REAL,
    capacity     REAL,
    portionSize  INTEGER,
    raceID       TEXT,
    basePrice    REAL,
    published    INTEGER,
    marketGroupID TEXT,
    iconID       TEXT,
    soundID      TEXT,
    graphicID    INTEGER
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
    regionName TEXT    NOT NULL,
    x          REAL,
    y          REAL,
    z          REAL,
    xMin       REAL,
    xMax       REAL,
    yMin       REAL,
    yMax       REAL,
    zMin       REAL,
    zMax       REAL,
    factionID  INTEGER,
    nebula     INTEGER,
    radius     REAL
)
STRICT;


-- Table: solar_systems
CREATE TABLE IF NOT EXISTS solar_systems (
    solarSystemID   INTEGER PRIMARY KEY,
    regionID        INTEGER REFERENCES regions (regionID),
    constellationID INTEGER,
    solarSystemName TEXT    NOT NULL,
    x               REAL,
    y               REAL,
    z               REAL,
    xMin            REAL,
    xMax            REAL,
    yMin            REAL,
    yMax            REAL,
    zMin            REAL,
    zMax            REAL,
    luminosity      REAL,
    border          INTEGER,
    fringe          INTEGER,
    corridor        INTEGER,
    hub             INTEGER,
    international   INTEGER,
    regional        INTEGER,
    constellation  INTEGER,
    security        REAL,
    factionID       INTEGER,
    radius          REAL,
    sunTypeID       INTEGER,
    securityClass   TEXT
);


-- Index: time_based
CREATE INDEX IF NOT EXISTS time_based ON killmails (
    time ASC,
    killmail_id ASC
);

CREATE TABLE invGroups (
    groupID INTEGER PRIMARY KEY,
    categoryID INTEGER,
    groupName TEXT,
    iconID TEXT,
    useBasePrice INTEGER,
    anchored INTEGER,
    anchorable INTEGER,
    fittableNonSingleton INTEGER,
    published INTEGER
);
CREATE INDEX idx_invGroups_categoryID ON invGroups (categoryID);
CREATE INDEX idx_invGroups_groupName ON invGroups (groupName);

CREATE TABLE invCategories (
    categoryID INTEGER PRIMARY KEY,
    categoryName TEXT,
    iconID TEXT,
    published INTEGER
);
CREATE INDEX idx_invCategories_categoryName ON invCategories (categoryName);
CREATE INDEX idx_invCategories_iconID ON invCategories (iconID);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;



