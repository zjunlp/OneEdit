from .utils import load_yaml
from .editor import Editor
from .interpreter import Interpreter
from .controller import Controller

class OneEdit:
    def __init__(self,hparams_path):
        self.hparams = load_yaml(hparams_path)
        self.editor = Editor(self.hparams['editor'])
        self.interpreter = Interpreter(self.hparams['interpreter'])
        self.controller = Controller(self.hparams['controller'])
        self.edit_triples = []
        self.rollback_triples = []
    
    def generate(self,str):
        return self.editor.generate(str)
    
    def generate_lte(self,str):
        return self.editor.generate_lte(str,self.rollback_triples,self.edit_triples)
    
    def rollback_knowledge(self,str):
        triple = self.interpreter.interpret(str)
        rollback_triples = self.editor.rollback(triple)
        self.editor.rollback(rollback_triples)
        
    def edit_knowledge_lte(self,str):
        triple = self.interpreter.interpret(str)
        edit_triples, rollback_triples = self.controller.resolve(triple)
        self.edit_triples.append(edit_triples)
        self.rollback_triples.append(rollback_triples)

        # self.editor.edit(edit_triples)
        # self.editor.rollback(rollback_triples)
    def lte_edit(self,str):
        self.editor.edit(self.edit_triples)
        self.editor.rollback(self.rollback_triples)
        
    def edit_knowledge(self,str):
        print('----------')
        print(str)
        print('----------')

        triple = self.interpreter.interpret(str)       
        edit_triples, rollback_triples = self.controller.resolve(triple)
        self.edit_triples.append(edit_triples)
        self.rollback_triples.append(rollback_triples)
        print("begin edit model")
        self.editor.edit(edit_triples)
        self.editor.rollback(rollback_triples)
        return f"finish edit knowledge {triple}!"
    
    def release(self):
        del self.editor
        del self.interpreter


    
        
