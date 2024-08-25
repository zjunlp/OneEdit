from src.system import *
import numpy as np
import json
import torch
import random
import argparse
from utils import slice_list, test_prediction_acc

parser = argparse.ArgumentParser()
parser.add_argument('--datapath', type=str, required=True)
parser.add_argument('--harampath', type=str, required=True)

args = parser.parse_args()


with open(f'{args.datapath}/one_hop.json') as f:
    one_hop_datas = json.load(f)
    random.shuffle(one_hop_datas)

with open(f'{args.datapath}/reverse.json') as f:
    reverse_datas = json.load(f)
    random.shuffle(reverse_datas)
    
with open(f'{args.datapath}/subrep.json') as f:
    subrep_datas = json.load(f)
    random.shuffle(subrep_datas)

rels = []

onehops = []
for data in one_hop_datas:
    oneedit = OneEdit(f'{args.datapath}/hparams.yaml')
    oneedit.edit_knowledge(data['prompt']+ ' ' + data['ans'])
    onehop = test_prediction_acc(oneedit.editor.editor, oneedit.editor.tok, data['onehop'], data['onehop_ans'], oneedit.editor.device,locality=False,vanilla_generation=True if oneedit.editor.method=='MEMIT' else True)
    rel = test_prediction_acc(oneedit.editor.editor, oneedit.editor.tok, data['prompt'], data['ans'], oneedit.editor.device,locality=False,vanilla_generation=True if oneedit.editor.method=='MEMIT' else True)
    onehops.append(onehop[0])
    rels.append(rel[0])
    oneedit.rollback_knowledge(data['prompt']+ ' ' + data['ans'])
    oneedit.release()
    
reverses = []
for data in reverse_datas:
    oneedit = OneEdit(f'{args.datapath}/hparams.yaml')
    oneedit.edit_knowledge(data['prompt']+ ' ' + data['ans'])
    onehop = test_prediction_acc(oneedit.editor.editor, oneedit.editor.tok, data['reverse'], data['subject'], oneedit.editor.device,locality=False,vanilla_generation=True if oneedit.editor.method=='MEMIT' else True)
    rel = test_prediction_acc(oneedit.editor.editor, oneedit.editor.tok, data['prompt'], data['ans'], oneedit.editor.device,locality=False,vanilla_generation=True if oneedit.editor.method=='MEMIT' else True)
    reverses.append(onehop[0])
    rels.append(rel[0])
    oneedit.rollback_knowledge(data['prompt']+ ' ' + data['ans'])
    oneedit.release()
    
subreps = []
for data in subrep_datas:
    oneedit = OneEdit(f'{args.datapath}/hparams.yaml')
    oneedit.edit_knowledge(data['prompt']+ ' ' + data['ans'])
    subrep = test_prediction_acc(oneedit.editor.editor, oneedit.editor.tok, data['sub_prompt'], data['ans'], oneedit.editor.device,locality=False,vanilla_generation=True if oneedit.editor.method=='MEMIT' else True)
    rel = test_prediction_acc(oneedit.editor.editor, oneedit.editor.tok, data['prompt'], data['ans'], oneedit.editor.device,locality=False,vanilla_generation=True if oneedit.editor.method=='MEMIT' else True)
    subreps.append(subrep[0])
    rels.append(rel[0])
    oneedit.rollback_knowledge(data['prompt']+ ' ' + data['ans'])
    oneedit.release()    

print(sum(rels)/len(rels))
print(sum(onehops)/len(onehops))
print(sum(reverses)/len(reverses))
print(sum(subreps)/len(subreps))

