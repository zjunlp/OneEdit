from neo4j import GraphDatabase


"""
目前kg的构建，实体都是只有name，没有label。关系的名称统一为relationship，type不一样
"""

class KG:
    def __init__(self,url,name,password):
        # try:
        self.driver = GraphDatabase.driver(f"{url}", auth=(f"{name}", f"{password}"))
        # except ServiceUnavailable as e:
        #     print(f"Failed to connect to Neo4j at {url}, error: {e}")
            
    def close(self):
        self.driver.close()
        
    def clear(self):
        with self.driver.session() as session:
            session.write_transaction(self._clear)
        
    def triple_exists(self, triple)->bool:
        with self.driver.session() as session:
            result = session.read_transaction(self._check_triple, triple)
            return result
        
    def head_and_relationship_exists(self, triple)->bool:
        with self.driver.session() as session:
            result = session.read_transaction(self._check_head_and_relationship, triple)
            return result     
            
    def add_triple(self, triple):
        with self.driver.session() as session:
            session.write_transaction(self._add_triple, triple)
            
    def delete_relationship(self, triple):
        with self.driver.session() as session:
            result = session.write_transaction(self._delete_relationship, triple)
    
    def find_tail_entities_by_head_and_relation(self, head_name, relationship_type):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_tails_by_head_and_relation, head_name, relationship_type)
            return result   
            
    def load_csv(self, csv_file_url):
            with self.driver.session() as session:
                session.write_transaction(self._load_csv, csv_file_url)
                
    def export_kg_to_csv(self, export_file_path):
        with self.driver.session() as session:
            session.write_transaction(self._export_csv, export_file_path)


    @staticmethod
    def _clear(tx):
        query = "MATCH (n) DETACH DELETE n"
        tx.run(query)
        print("Knowledge Graph has been cleared.")
                  
    @staticmethod
    def _add_triple(tx, triple):
        query = (
            "MERGE (h {name: $h_name}) "
            "MERGE (t {name: $t_name}) "
            "MERGE (h)-[r:relationship{type: $relationship}]->(t) "
        )
        tx.run(query, h_name=triple[0], t_name=triple[2], relationship=triple[1])

    @staticmethod
    def _check_triple(tx, triple):
        query = (
            "MATCH (h)-[r:relationship]->(t) "
            "WHERE h.name = $h_name AND t.name = $t_name AND r.type = $relationship "
            "RETURN count(r) > 0 AS exists"
        )
        result = tx.run(query, h_name=triple[0], t_name=triple[2], relationship=triple[1])
        return result.single()[0]
    
    @staticmethod
    def _check_head_and_relationship(tx, triple):
        query = (
            "MATCH (h)-[r:relationship]->() "
            "WHERE h.name = $h_name AND r.type = $relationship "
            "RETURN count(r) > 0 AS exists"
        )
        result = tx.run(query, h_name=triple[0], relationship=triple[1])
        return result.single()[0]
    
    @staticmethod
    def _delete_relationship(tx, triple):
        query = (
            "MATCH (h)-[r]->(t) "
            "WHERE h.name = $h_name AND t.name = $t_name AND r.type = $relationship "
            "DELETE r"
        )
        tx.run(query, h_name=triple[0], t_name=triple[2], relationship=triple[1])

    @staticmethod
    def _find_tails_by_head_and_relation(tx, head_name, relationship_type):
        query = (
            "MATCH (h)-[r:relationship]->(t) "
            "WHERE h.name = $head_name AND r.type = $relationship_type "
            "RETURN t.name AS tailName"
        )
        result = tx.run(query, head_name=head_name, relationship_type=relationship_type)
        return [record["tailName"] for record in result]
  
    
    @staticmethod
    def _load_csv(tx, csv_file_path):
        query = (
            "LOAD CSV WITH HEADERS FROM $file_path AS row "
            "MERGE (h {name: row.Head}) "
            "MERGE (t {name: row.Tail}) "
            "MERGE (h)-[r:relationship {type: row.Relationship}]->(t) "
        )
        tx.run(query, file_path=f'{csv_file_path}')
        
    @staticmethod
    def _export_csv(tx, export_file_path):
        # Execute the Cypher command to export data
        query = (
            "CALL apoc.export.csv.query("
            "'MATCH (n)-[r]->(m) RETURN n AS Node1, type(r) AS Relationship, m AS Node2', "
            f"'{export_file_path}', "
            "{headers:true})"
        )
        tx.run(query)
        print(f"Knowledge graph exported to {export_file_path}.")