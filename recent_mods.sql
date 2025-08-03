SELECT 
    its.typeName,
    s.solarSystemName,
    km.time,
    itt.typeName,
    di.quantity
FROM 
    droppedItems di
JOIN 
    killmails km ON di.killmail_id = km.killmail_id
JOIN 
    invTypes its ON its.typeID = km.ship_type_id
JOIN
    invTypes itt ON itt.typeID = di.typeID
JOIN
    solar_systems s ON s.solarSystemID = km.solarSystemID
WHERE 
    1
ORDER BY 
    km.time DESC
LIMIT
    100;
