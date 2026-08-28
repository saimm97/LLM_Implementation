import hashlib, json


def make_key(model_name, prompt, parameters):
    raw = json.dumps(
        {"model": model_name, "prompt": prompt, "params": parameters},
        sort_keys=True,
        )
    return "cache:" + hashlib.sha256(raw.encode()).hexdigest()