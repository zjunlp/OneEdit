from typing import Any, Dict, List, Tuple
import torch
from functools import partial
from copy import deepcopy
from transformers import AutoModelForCausalLM, AutoTokenizer,LlamaTokenizer
from .GRACE import GRACE
from .grace_hparams import GraceHyperParams
from .utils import tokenize
import os

def apply_grace_to_model(
        name: str,
        hparams: GraceHyperParams,
        **kwargs: Any,
):
    if 'llama' in name.lower():
        model = AutoModelForCausalLM.from_pretrained(name).to(f'cuda:{hparams.device}')
        tok = AutoTokenizer.from_pretrained(name)
    else:
        model = AutoModelForCausalLM.from_pretrained(name).to(f'cuda:{hparams.device}')
        tok = AutoTokenizer.from_pretrained(name)
    tok.pad_token_id = tok.eos_token_id

    device = torch.device(f'cuda:{hparams.device}')
    
    tok4grace = partial(tokenize,tokenizer=tok, device=device)
    editor = GRACE(model=model, config=hparams, device=device)
    return editor,tok4grace,tok

# def apply_grace_to_model(
#         name: str,
#         hparams: GraceHyperParams,
#         **kwargs: Any,
# ):
#     return 1,1,1
