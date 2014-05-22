import scrib_util as util


# Clones list/set/dict structures recursively; otherwise returns identity
def clone_collection(c):
    if c is None:
        return None
    if isinstance(c, list):
        return clone_list_aux(c)
    elif isinstance(c, set):
        return clone_set_aux(c)
    elif isinstance(c, dict):
        return clone_dict_aux(c)
    else:
        return c


# Could make the following non-public
    
def clone_list_aux(list_):
    if list_ is None:
        return None
    if not isinstance(list_, list):
        util.report_error("Expected list, not: " + list)
    clone = []
    for x in list_:
        clone.append(clone_collection(x))
    return clone

def clone_set_aux(set_):
    if set_ is None:
        return None
    if not isinstance(set_, set):
        util.report_error("Expected set, not: " + set)
    clone = set([])
    for x in set_:
        clone.add(clone_collection(x))
    return clone

def clone_dict_aux(dict_):
    if dict_ is None:
        return None
    if not isinstance(dict_, dict):
        util.report_error("Expected dict, not: " + type(dict_))
    clone = {}
    for k in dict_.keys():
        clone[clone_collection(k)] = clone_collection(dict_[k])
    return clone
