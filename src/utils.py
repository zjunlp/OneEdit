import yaml
from collections import defaultdict

def generate_edit_key(triple):
    if len(triple)==3:   
        key = triple[0] + '_' + triple[1] + '_' + triple[2]
    else:
        key = triple[1][0] + '_' + triple[1][1] + '_' + triple[1][2] + '_' + triple[0][0] + '_' + triple[0][1] + '_' + triple[0][2]
    return key

def load_yaml(path):
    with open(path, 'r') as file:
        hparams = yaml.safe_load(file)   
    return hparams

def str2triple(str):
    str = str.strip('()')
    words = str.split(',')
    triple =  (words[0].strip(' ').replace(' ','_'),words[1].strip(' ').replace(' ','_'),words[2].strip(' ').replace(' ','_'))
    print(triple)
    return triple


def find_pairwise_connected_triples(triples):
    out_degree = defaultdict(list)

    for triple in triples:
        start, _, end = triple
        out_degree[start].append(triple)

    connected_pairs = []
    for triple in triples:
        _, _, end = triple
        if end in out_degree:
            for next_triple in out_degree[end]:
                connected_pairs.append((triple, next_triple))
    return connected_pairs

def is_nested_tuple(item):
    return isinstance(item, tuple) and any(isinstance(sub_item, tuple) for sub_item in item)

def extract_relations_with_heads_and_tails(nested_triple):
    def extract_from_nested(item, relations):
        head = None
        tail = None
        for sub_item in item:
            if isinstance(sub_item, tuple):
                if any(isinstance(i, tuple) for i in sub_item):
                    sub_head, sub_tail = extract_from_nested(sub_item, relations)
                    head = head if head is not None else sub_head
                    tail = sub_tail
                else:
                    relations.append(sub_item[1])
                    head = head if head is not None else sub_item[0]
                    tail = sub_item[2]
        return head, tail

    relations = []
    head, tail = extract_from_nested(nested_triple, relations)
    return head, tail, relations
