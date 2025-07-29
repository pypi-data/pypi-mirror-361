from collections import OrderedDict

"""
The keys of old pytorch model are saved as "module.xxxxxx",
but the keys of new pytorch model are saved as "xxxxxx".
So this func is used to remove "module." which existed in old pytorch model.
"""

def pretrained_old2new(old_pretrained:OrderedDict):
    keys = list(old_pretrained.keys())
    new_pretrained = OrderedDict()

    for key in keys:
        if key[:7] == "module.":
            new_pretrained[key[7:]] = old_pretrained[key]
        else:
            new_pretrained[key] = old_pretrained[key]
    
    return new_pretrained
