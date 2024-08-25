from neo4j import GraphDatabase
import pandas as pd

"""
目前kg的构建，实体都是只有name，没有label。关系的名称统一为relationship，type不一样
"""

class KG:
    def __init__(self,url,name,password):
        self.driver = GraphDatabase.driver(f"{url}", auth=(f"{name}", f"{password}"))
        
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
        
    def get_nearest_n_triples(self, head_entity_name, n):
        with self.driver.session() as session:
            results = session.read_transaction(self.find_nearest_n_triples, head_entity_name, n)
        return results
            
    def load_csv(self, csv_file_path):
        data = pd.read_csv(csv_file_path)
        with self.driver.session() as session:
            for index, row in data.iterrows():
                session.write_transaction(self._add_triple,row)
    
    def export_csv(self, csv_file_path):
        with self.driver.session() as session:
            result = session.read_transaction(self._export_csv)
            head,relation,tail = [],[],[]
            for record in result:
                head.append(record['head'])
                relation.append(record['relation'])
                tail.append(record['tail'])
            data = {'head':head,'relation':relation,'tail':tail}
            df = pd.DataFrame(data)
            df.to_csv(csv_file_path, index=False)
   
                

    @staticmethod
    def _clear(tx):
        query = "MATCH (n) DETACH DELETE n"
        tx.run(query)
        print("Knowledge Graph has been cleared.")
                  
    @staticmethod
    def _add_triple(tx, triple):
        query = (
            "MERGE (h:node {name: $h_name}) "
            "MERGE (t:node {name: $t_name}) "
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
    def find_nearest_n_triples(tx, head_entity_name, n):
        query = (
            "MATCH (head {name: $head_entity_name})-[r]->(tail) "
            "RETURN tail.name AS tailName, r.type AS relationship_type "
            "LIMIT $n"
        )
        result = tx.run(query, head_entity_name=head_entity_name, n=n)
        return [(head_entity_name,record["relationship_type"],record["tailName"]) for record in result]
    
    @staticmethod
    def _export_csv(tx):
        query = (
            "MATCH (n)-[r]->(t) "
            "RETURN n.name AS head, r.type AS relation, t.name AS tail"
        )
        result = tx.run(query)
        return [record.data() for record in result]
        
        
