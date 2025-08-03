SELECT 
    itt.typeID,
    itt.typeName,
    SUM(di.quantity) as total_quantity
FROM 
    droppedItems di
JOIN
    invTypes itt ON itt.typeID = di.typeID
WHERE 
    1
GROUP BY
    itt.typeID,
    itt.typeName
ORDER BY 
    total_quantity DESC
