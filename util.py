

def sort_dict(node_group):
    """
    return sorted dictionary by key
    """
    
    sorted_node_id = dict(sorted(node_group.items(), key = lambda x:x[0]))
    return sorted_node_id