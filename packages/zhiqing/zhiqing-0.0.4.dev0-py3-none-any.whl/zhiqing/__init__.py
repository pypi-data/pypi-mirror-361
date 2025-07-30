import copy


def min_repetend_length(inputs):
    count = len(inputs)
    for i in range(1, count):
        for j in range(i+1, count):
            if not (inputs[j-i] == inputs[j]):
                break
        else:
            return i
    return count


def merge_dicts(arg, *args):
    results = copy.copy(arg)
    for a in args:
        results.update(a)
    return results
