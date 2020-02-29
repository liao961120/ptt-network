from functools import reduce

def merge_dicts(dicts):
    """
    Given any number of dicts, merge into a new dict
    """

    return reduce(merge_2dicts, dicts)

def merge_2dicts(d1, d2):
    common_keys = set(d1) & set(d2)
    merged = {k: d1[k] + d2[k] for k in common_keys}

    for k in ((set(d1) | set(d2)) - common_keys):
        if k in d1:
            merged[k] = d1[k]
        else:
            merged[k] = d2[k]
        
    return merged