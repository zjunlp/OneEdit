import json
from transformers import AutoModelForCausalLM,AutoTokenizer
from peft import PeftModel, PeftConfig
import torch
from src.utils import *
import os

class Interpreter:
    def __init__(self,hparams):
        self.hparams = hparams
        peft_model_id = self.hparams['adapter_path']
        model_path = self.hparams['model_path']
        model = AutoModelForCausalLM.from_pretrained(model_path,torch_dtype=torch.bfloat16,trust_remote_code=True)
        self.model = PeftModel.from_pretrained(model, peft_model_id).to(self.hparams['device'])
        self.tokenizer = AutoTokenizer.from_pretrained(model_path,trust_remote_code=True)

    def interpret(self,text:str):
        respond, _ = self.model.chat(self.tokenizer, text)
        assert '<edit>' in respond, "The input text is not a triple."
        respond = respond.replace('<edit>','').strip()
        respond = str2triple(respond)        
        return respond
    
