"""Read a running local API without displaying bearer credentials."""
import argparse
import json
from pathlib import Path
from urllib.request import Request, urlopen

parser = argparse.ArgumentParser()
parser.add_argument('--tenant', default='DEMO-ALPHA')
parser.add_argument('--credentials', default='artifacts/local-credentials.json')
args = parser.parse_args()
credentials = json.loads(Path(args.credentials).read_text(encoding='utf-8'))
token = next(key for key, identity in credentials.items()
             if identity['tenant'] == args.tenant and identity['role'] == 'reviewer')
request = Request('http://127.0.0.1:8080/cases', headers={'Authorization': f'Bearer {token}'})
with urlopen(request, timeout=10) as response:
    print(json.dumps(json.load(response), indent=2))
