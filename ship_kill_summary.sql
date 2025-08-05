SELECT
    it.typeName,
    COUNT(*) AS total_kills
FROM
    killmails km
JOIN
    solar_systems s ON km.solarSystemID = s.solarSystemID
JOIN
    invTypes it ON km.ship_type_id = it.typeID
WHERE
    1
GROUP BY
    it.typeName
ORDER BY
    total_kills DESC
