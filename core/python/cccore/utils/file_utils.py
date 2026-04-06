import sys

def reload_cc_modules():
    """
    Reload all control chaos modules
    """
    to_remove = list()
    for k, v in sys.modules.items():
        if k.startswith("cc"):
            to_remove.append(k)
    for e in to_remove:
        print(f"Reloading...{e}")
        del sys.modules[e]
