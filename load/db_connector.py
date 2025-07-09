from neo4j import GraphDatabase

def connect_test(url: str, user: str, password: str):
    try:
        with GraphDatabase.driver(url, auth=(user, password)) as driver:
            if driver.verify_connectivity:
                return True
            else:
                return False
    except Exception as e:
         print(f"Failed to connect to Neo4j: {e}")
            