import json
class RELATIONSHIP_LIBRARY:
    def __init__(self,path):
        self.path = path
        with open(path, 'r') as file:
            self.items = json.load(file)
    
    def save(self):
        with open(self.path, 'w') as file:
            json.dump(self.items, file, indent=4)
            
    def find_relationship(self, triple):
        for item in self.items:
            if item["name"] == triple[1]:
                if item["multihop"] !="":
                    item["multihop"] = eval(item["multihop"]) if type(item["multihop"])==str else item["multihop"] 
                return item
            
        print("not find  relationship,but you can define it")
        print("please input the type")
        Type = input()
        print("please input the reverse")
        Reverse = input()
        print("please type multihop")
        Multihop = input()
        if Multihop =='':
            newitem = {"name":triple[1],"type":Type,"reverse":Reverse,"multihop":""}
        else:
            newitem = {"name":triple[1],"type":Type,"reverse":Reverse,"multihop":eval(Multihop)}      
        print(newitem)
        self.updata_relationship_library(newitem)
        return newitem
    
    def updata_relationship_library(self,newitem):
        for item in self.items:
            if item["name"] == newitem["name"]:
                if newitem["type"] != "":
                    item["type"] = newitem["type"]
                if newitem["reverse"] != "":
                    item["reverse"] = newitem["reverse"]
                if newitem["multihop"] !="":
                    item["multihop"] = eval(newitem["multihop"]) if type(newitem)==str else newitem["multihop"]
                return
        self.items.append(newitem)
        self.save()

    def find_mutihop_relation(self, target_list):
        for item in self.items:
            if "multihop" in item and item['multihop'] != "":
                # 将'multihop'字符串转换为列表
                multihop_list = json.loads(item['multihop'].replace("'", "\""))
                if multihop_list == target_list:
                    return item['name']
        return False