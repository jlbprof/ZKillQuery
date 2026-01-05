CREATE TABLE invCategories (
    categoryID INTEGER PRIMARY KEY,
    categoryName TEXT,
    iconID TEXT,
    published INTEGER
);
CREATE INDEX idx_invCategories_categoryName ON invCategories (categoryName);
CREATE INDEX idx_invCategories_iconID ON invCategories (iconID);
