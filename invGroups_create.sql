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
