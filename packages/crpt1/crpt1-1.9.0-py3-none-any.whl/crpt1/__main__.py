import os

with open(os.path.join(os.path.dirname(__file__), "crpt1.py"), encoding="utf-8") as f_in:
    code = f_in.read()
exec(code, globals())
