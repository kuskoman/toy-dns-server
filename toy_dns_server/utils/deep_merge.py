# take as many dicts, and override the values of first dict with the values of the next dict
def deep_merge(*dicts: dict) -> dict:
    merged = {}
    for d in dicts:
        for k, v in d.items():
            if isinstance(v, dict):
                merged[k] = deep_merge(merged.get(k, {}), v)
            else:
                merged[k] = v
    return merged
