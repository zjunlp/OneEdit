import json

from .utils import *
from .kg import KG
from .editor import Editor
from .library import RELATIONSHIP_LIBRARY
from .interpreter import Interpreter

class Controller:
    def __init__(self,hparam):
        self.hparams = hparam
        self.kg = KG(self.hparams['neo4j_uri'],self.hparams['neo4j_name'],self.hparams['neo4j_password'])
        self.relationship_library= RELATIONSHIP_LIBRARY(self.hparams['relation_library_path'])
        if self.hparams['load_kg']:
            self.clear_kg()
            self.load_kg(self.hparams['kg_csv_path'])    
    
    def load_kg(self,path=''):
        if path == '':
            path = self.hparams['kg_csv_path']
        self.kg.load_csv(path)
    
    def save_kg(self,path=''):
        if path == '':
            path = self.hparams['kg_csv_path']
        self.kg.export_csv(path)
    
    def clear_kg(self):
        self.kg.clear()
    
    def resolve(self,triple):
        edit_triples = [] 
        rollback_triples = []  
        print(f"begin edit {triple}")
        relationship_item = self.relationship_library.find_relationship(triple)
        edit_triples, rollback_triples = self.conflict_resoluation(triple,relationship_item)
        augmentation_triples = self.kg_augmentation(triple)
        edit_triples += augmentation_triples
        edit_triples = list(set(edit_triples))
        rollback_triples = list(set(rollback_triples))
        return edit_triples, rollback_triples
        
    def conflict_resoluation(self,triple,relationship_item):
        edit_triples = []
        rollback_triples = []
        new_edit_list, new_rollback_list = self.detact_single_conflict(triple,relationship_item)
        edit_triples = edit_triples + new_edit_list
        rollback_triples = rollback_triples + new_rollback_list
        return edit_triples, rollback_triples
    
    def kg_augmentation(self,triple):
        
        n = self.hparams["kg_augment_num"]
        kg_augmentation_list = [triple]
        
        ntriples = self.kg.get_nearest_n_triples(triple[2],n)
        kg_augmentation_list += ntriples
        if self.hparams["symbolic_rule"]:
            pairwise_triples = find_pairwise_connected_triples(kg_augmentation_list)
            for item in pairwise_triples:
                head,tail,relations = extract_relations_with_heads_and_tails(item)
                mutihop_relation = self.relationship_library.find_mutihop_relation(relations)
                if mutihop_relation != False:
                    kg_augmentation_list.append((head,mutihop_relation,tail))  
        return kg_augmentation_list
        
    def detact_single_conflict(self,triple,relationship_item):
        edit_triples = []
        rollback_triples = []
        if self.judeg_knowledge_conflict_in_kg(triple):
            if relationship_item['type'] != 'one2many':
                print("there is a conflict")
                old_triple = self.from_head_and_relation_get_triples(triple[0],triple[1])
                if isinstance(old_triple,list):
                    old_triple = old_triple[0]

                self.kg.delete_relationship(old_triple)
                rollback_triples.append(old_triple)
                delete_reversed_triple = self.delete_reverse_triple(old_triple)
                if delete_reversed_triple !=None:
                    rollback_triples.append(delete_reversed_triple)
                
                self.kg.add_triple(triple)
                edit_triples.append(triple)
                reverse_triple = self.add_reverse_triple(triple)
                if reverse_triple != None:
                    edit_triples.append(reverse_triple)
                return edit_triples,rollback_triples

        self.kg.add_triple(triple)
        edit_triples.append(triple)
        reverse_triple = self.add_reverse_triple(triple)
        if reverse_triple != None:
            edit_triples.append(reverse_triple)
        print("finish edit kg")
        return edit_triples,rollback_triples
    
    def judge_knowledge_in_kg(self,triple):
        return self.kg.triple_exists(triple)
    
    def judeg_knowledge_conflict_in_kg(self,triple):
        if self.kg.head_and_relationship_exists(triple) and not self.judge_knowledge_in_kg(triple):
            return True
        return False
    
    def from_head_and_relation_get_triples(self,head,relation)->list:
        triples = []
        tails = self.kg.find_tail_entities_by_head_and_relation(head,relation)
        for tail in tails:
            triple = (head,relation,tail)
            triples.append(triple)
        return triples
    
    def delete_reverse_triple(self,triple):
        relationship = self.relationship_library.find_relationship(triple)
        if relationship !="" and relationship['reverse']!="":
            reverse_triple = (triple[2],relationship['reverse'],triple[0])
            self.kg.delete_relationship(reverse_triple)
            return reverse_triple
        return None
        
    def add_reverse_triple(self,triple):
        relationship = self.relationship_library.find_relationship(triple)
        print(relationship)
        if relationship !="" and relationship['reverse']!="":
            reverse_triple = (triple[2],relationship['reverse'],triple[0])
            print(reverse_triple)
            self.kg.add_triple(reverse_triple)
            return reverse_triple
        return None
        
        
