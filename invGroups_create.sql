CREATE TABLE invGroups (
    groupID INTEGER PRIMARY KEY,
    categoryID INTEGER,
    groupName TEXT
);
CREATE INDEX idx_invGroups_categoryID ON invGroups (categoryID);
CREATE INDEX idx_invGroups_groupName ON invGroups (groupName);

