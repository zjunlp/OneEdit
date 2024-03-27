import json

from .utils import *
from .kg import KG
from .editor import EDITOR
from .library import RELATIONSHIP_LIBRARY

class CONTROLLER:
    def __init__(self,url,name,password,param_path):
        self.editor = EDITOR(param_path)
        self.kg = KG(url,name,password)
        self.cache = []
        self.relationship_library= RELATIONSHIP_LIBRARY('./data/relationship_library.json')
    
    def judge_knowledge_in_kg(self,triple):
        return self.kg.triple_exists(triple)
    
    def judeg_knowledge_conflict_in_kg(self,triple):
        if self.kg.head_and_relationship_exists(triple) and not self.judge_knowledge_in_kg(triple):
            return True
        return False
        
    def edit_knowledge(self,triple):
        if self.judge_knowledge_in_kg(triple):
            print("This knowledge has been edited into the model.")
            return
        
        relationship_item = self.relationship_library.find_relationship(triple[1])
        if relationship_item == None:
            print("not find  relationship,but you can define it")
            print("please input the type")
            type = input()
            print("please input the type")
            reverse = input()
            newitem = {"name":triple[1],"type":type,"reverse":reverse}
            print(newitem)
            self.relationship_library.updata_relationship_library(newitem)
        relationship_item = self.relationship_library.find_relationship(triple[1])

        if relationship_item["type"] == "one2one":
            self.edit_one2one(triple)
                    
        elif relationship_item["type"] == "one2many":
            self.edit_one2many(triple)

        return 0   
    
    
    def recover_knowledge(self,triple,triple_old):
    #取消已经编辑的知识，用于回滚知识
        if not self.judge_knowledge_in_kg(triple):
            print("This knowledge do not has been edited into the model.so connot recover")
            return
        relationship_item = self.relationship_library.find_relationship(triple[1])
        
        if relationship_item == None:
            print("not find reverse relationship,but you can define it")
            #我们没有在库里面搜索到这个关系让用户来决定这个关系是什么样子的
            type = input()
            reverse = input()
            newitem = {"name":{triple[1]},"type":{type},"reverse":{reverse}}
            self.relationship_library.updata_relationship_library(newitem)
        
        relationship_item = self.relationship_library.find_relationship(triple[1])
        
        self.kg.delete_relationship(triple)
        self.kg.add_triple(triple_old)
        self.editor.rollback(triple,triple_old)

    
    def edit_one2one(self,triple):  
        if self.judeg_knowledge_conflict_in_kg(triple):
            print("This knowledge conflicts with KG")
            old_tail = self.kg.find_tail_entities_by_head_and_relation(triple[0],triple[1])
            if isinstance(old_tail,list):
                old_tail = old_tail[0]
            #one2one 的关系只会有一个tail
            
            old_triple = (triple[0],triple[1],old_tail)
            self.kg.delete_relationship(old_triple)
            self.kg.add_triple(triple)
            self.editor.edit([triple])
        else:
            self.kg.add_triple(triple)
            self.editor.edit([triple])    
     
               
    def edit_one2many(self,triple):    
        print("one2many relationship,you can modify it.")
        self.kg.add_triple(triple)
        self.editor.edit([triple])

            
"""
3月10日
目前是用了一个关系库，存储各个关系的类型，这个关系初步分类为 一对一的关系和一对多的关系
一对一的关系在进行编辑的时候，先判断这个关系是否冲突，如果不冲突就直接添加到知识图谱上面，然后进行编辑。如果冲突，判断用户权限，权限不足就返回，权限足够就删除这个关系，重新添加一个新的三元组。
一对多的关系在编辑的时候,就不用判断是否冲突了。
"""