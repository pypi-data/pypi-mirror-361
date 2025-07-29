import argparse, json, pprint, ast, sys
import jwt
import importlib.metadata
from jwt.utils import base64url_decode

def parse_input(raw):
    try:
        return json.loads(raw)
    except:
        return ast.literal_eval(raw)

def is_jwt(token):
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return False
        header = json.loads(base64url_decode(parts[0] + '=='))
        return 'alg' in header and 'typ' in header
    except: return False

def decode_jwts(obj):
    if isinstance(obj, dict):
        res = {}
        for k, v in obj.items():
            res[k] = decode_jwts(v)
            if isinstance(v, str) and is_jwt(v):
                try:
                    res[f"{k}__decoded"] = jwt.decode(v, options={"verify_signature": False})
                except Exception as e:
                    res[f"{k}__decoded_error"] = str(e)
        return res
    if isinstance(obj, list):
        return [decode_jwts(x) for x in obj]
    return obj

def main():
    parser = argparse.ArgumentParser(description='JSON/JWT formatter and decoder.')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--file')
    group.add_argument('--json')
    group.add_argument('--input', action='store_true')
    parser.add_argument('--decode-jwt', action='store_true')
    parser.add_argument('--output')
    parser.add_argument('--version', action='store_true')
    args = parser.parse_args()

    if args.version:
        print(importlib.metadata.version("jsonstruct-cli"))
        return

    if args.file:
        raw = open(args.file).read()
    elif args.json:
        raw = args.json
    elif args.input:
        print("Paste JSON (end Ctrl+D):")
        raw = sys.stdin.read()
    else:
        parser.print_help()
        return

    obj = parse_input(raw)
    if args.decode_jwt:
        obj = decode_jwts(obj)
    out = pprint.pformat(obj, indent=2, width=100)
    if args.output:
        with open(args.output, 'w') as f: f.write(out)
    else:
        print(out)

if __name__ == '__main__':
    main()
