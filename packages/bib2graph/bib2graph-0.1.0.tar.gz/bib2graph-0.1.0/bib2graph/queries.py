RANGO_AÑOS_PAPERS = """
MATCH (p:Paper)
WHERE p.year IS NOT NULL
RETURN MIN(toInteger(p.year)) AS min_year, 
        MAX(toInteger(p.year)) AS max_year,
        COUNT(DISTINCT p.year) AS unique_years
"""
