SELECT 
    km.time, 
    s.solarSystemName, 
    it.typeName 
FROM 
    killmails km 
JOIN 
    solar_systems s ON km.solarSystemID = s.solarSystemID 
JOIN 
    invTypes it ON km.ship_type_id = it.typeID 
WHERE 
    1
ORDER BY 
    km.time DESC
LIMIT 
    5;
