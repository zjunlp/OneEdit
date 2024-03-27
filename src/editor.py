from .utils import *
from easyedit import *

class EDITOR:
    def __init__(self,hparam_path):
        self.hparam = GraceHyperParams.from_hparams(hparam_path)
        self.device = f'cuda:{self.hparam.device}'
        self.editor,self.tok4grace,self.tok = apply_grace_to_model(name=self.hparam.model_name,hparams=self.hparam)
    
    def triple_to_request(self,triple)->dict:
        request = {}
        request['prompt'] = triple[0] + ' ' +triple[1]
        request['target_new'] = triple[2]
        return request

    def edit(self,triples):
        
        for new_triple in triples:
            print(new_triple)
            new_key = generate_edit_key(new_triple)
            request = self.triple_to_request(new_triple)
            tokens = self.tok4grace(request)
            self.editor.edit(config=self.hparam, tokens=tokens, edit_id=new_key)
            
            
    def rollback(self,old_triples):
            
        for old_triple in old_triples:
            old_key = generate_edit_key(old_triple)
            self.editor.rolllback(edit_id=old_key)
            
        print(f"finish rollback to {old_triples}")
        
    #3 27任务，把easyedit的回滚加上一个cache，也就是每次编辑都会保存hidden state的状态，只是调入调出的关系，其实也可以不做
    
    def generate(self,request:str):
        tokens = self.tok(request,return_tensors='pt').to(self.device)
        out_tokens = self.editor.generate(tokens['input_ids'],max_length=30)
        output = self.tok.decode(out_tokens[0],skip_special_tokens=True)
        return output