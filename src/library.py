import json

class RELATIONSHIP_LIBRARY:
    def __init__(self,path):
        self.path = path
        with open(path, 'r') as file:
            self.items = json.load(file)
    
    def save(self):
        with open(self.path, 'w') as file:
            json.dump(self.items, file, indent=4)
            
    def find_relationship(self, name):
        for item in self.items:
            if item["name"] == name:
                return item
        print("we not find the relationship in library")
        
        return None
    
    def updata_relationship_library(self,newitem):
        for item in self.items:
            if item["name"] == newitem["name"]:
                if newitem["type"] != "":
                    item["type"] = newitem["type"]
                if newitem["reverse"] != "":
                    item["reverse"] = newitem["reverse"]
                return
        self.items.append(newitem)
        self.save()
        