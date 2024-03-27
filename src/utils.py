def generate_edit_key(triple):
    """
    根据triple的头实体和关系生成唯一的edit_key
    """    
    key = triple[0] + '_' + triple[1] + '_' + triple[2]
    return key