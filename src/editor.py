from .utils import *
from easyedit import *
import random

class Editor:
    def __init__(self,hparam):
        if hparam['edit_method'] == 'GRACE':
            self.method = 'GRACE'
            editing_hparams = GraceHyperParams
            self.hparam = editing_hparams.from_hparams(f"./easyedit/hparams/{hparam['edit_method']}/{hparam['model_name']}.yaml")
            self.device = f'cuda:{self.hparam.device}'
            self.editor,self.tok4grace,self.tok = apply_grace_to_model(name=self.hparam.model_name,hparams=self.hparam)
            
        elif hparam['edit_method'] == 'ROME':
            self.method = 'ROME'
            editing_hparams = ROMEHyperParams
            self.hparam = editing_hparams.from_hparams(f"./easyedit/hparams/{hparam['edit_method']}/{hparam['model_name']}.yaml")
            self.device = f'cuda:{self.hparam.device}'
            self.editor,self.tok = apply_rome_to_model(name=self.hparam.model_name, hparams=self.hparam)    
        elif hparam['edit_method'] == 'MEMIT':
            self.method = 'MEMIT'
            editing_hparams = MEMITHyperParams
            self.hparam = editing_hparams.from_hparams(f"./easyedit/hparams/{hparam['edit_method']}/{hparam['model_name']}.yaml")
            self.device = f'cuda:{self.hparam.device}'
            self.editor,self.tok = apply_memit_to_model(name=self.hparam.model_name, hparams=self.hparam)         
        else:
            raise NotImplementedError

    def triple_to_requests(self,triple)->dict:
        if len(triple) == 3:
            request1 = {}
            request2 = {}
            # request3 = {}
            request1['prompt'] = f"the {triple[1].replace('_',' ')} of {triple[0].replace('_',' ')} is"
            request1['target_new'] = triple[2].replace('_',' ')
            request1['subject'] = triple[0].replace('_',' ')

            request2['prompt'] = f"{triple[0].replace('_',' ')}'s {triple[1].replace('_',' ')} is"
            request2['target_new'] = triple[2].replace('_',' ')
            request2['subject'] = triple[0].replace('_',' ')

            # request3['prompt'] = f"{triple[0].replace('_',' ')} is {triple[1].replace('_',' ')}"
            # request3['target_new'] = triple[2].replace('_',' ')
            # requests = [request1,request2,request3] 
            requests = [request1,request2]
        else:
            request1 = {}
            request2 = {}
            # request3 = {}
            request1['prompt'] = f"the {triple[1][1].replace('_',' ')} of the {triple[0][1].replace('_',' ')} of {triple[0][0].replace('_',' ')} is"
            request1['target_new'] = triple[1][2].replace('_',' ')
            request1['subject'] = triple[0][0].replace('_',' ')
            requests = [request1]           
        return requests
        
    def edit(self,triples):
        random.shuffle(triples)

        if self.method == 'MEMIT':
            batch_edit = []
            new_key = generate_edit_key(triples[0])
            for triple in triples:
                requests = self.triple_to_requests(triple)
                batch_edit += requests
                
            random.shuffle(batch_edit)
            self.editor.edit(requests=batch_edit, edit_id=new_key)
            return  
        for new_triple in triples:
            if self.method == 'GRACE':
                # new_key = generate_edit_key(new_triple)
                requests = self.triple_to_requests(new_triple)
                for request in requests:
                    tokens = self.tok4grace(request)
                    print(request)
                    self.editor.edit(config=self.hparam, tokens=tokens, edit_id=request)
            elif self.method == 'ROME':
                new_key = generate_edit_key(new_triple)
                requests = self.triple_to_requests(new_triple)
                for request in requests:
                    print(request)
                    self.editor.edit(request=request, edit_id=new_key)         
   
        print("finish edit")
            
            
    def rollback(self,old_triples):    
        # for old_triple in old_triples:
        #     old_key = generate_edit_key(old_triple)
        #     self.editor.rollback(edit_id=old_key)
            
        print(f"finish rollback to {old_triples}")
        
    
    def generate(self,request:str):    
        tokens = self.tok(request,return_tensors='pt').to(self.device)
        out_tokens = self.editor.generate(tokens['input_ids'],max_length=20,max_new_tokens=20)
        output = self.tok.decode(out_tokens[0],skip_special_tokens=True)
        return output
    
    def generate_lte(self,request:str,list_edit:list,list_rollback:list):    
        tokens = self.tok(request,return_tensors='pt').to(self.device)
        out_tokens = self.editor.generate(tokens['input_ids'],max_length=30)
        output = self.tok.decode(out_tokens[0],skip_special_tokens=True)
        return output