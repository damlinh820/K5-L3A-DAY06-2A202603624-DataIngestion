"""List live embedding models and make one explicit probe; never log API keys."""
import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    settings = {}
    for path in [ROOT / 'starter' / '.env', ROOT / '.env']:
        if path.exists():
            for line in path.read_text(encoding='utf-8-sig').splitlines():
                if '=' in line and not line.lstrip().startswith('#'):
                    key, value = line.split('=', 1)
                    settings[key.strip()] = value.strip().strip('\"').strip("'")
    key = settings.get('OPENROUTER_API_KEY', '')
    if not key:
        raise SystemExit('OPENROUTER_API_KEY missing; configure it locally, never paste it into chat.')
    headers = {'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'}
    def call(route, payload=None):
        request = urllib.request.Request('https://openrouter.ai/api/v1/' + route,
            data=json.dumps(payload).encode() if payload is not None else None, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f'OpenRouter HTTP {exc.code}; no fallback used') from None
    catalog = call('embeddings/models')
    models = catalog.get('data', [])
    model_id = 'openai/text-embedding-3-small'
    selected = next((m for m in models if m.get('id') == model_id), None)
    if selected is None:
        raise RuntimeError('Selected multilingual embedding model absent from live catalog; choose explicitly before proceeding')
    reply = call('embeddings', {'model': model_id, 'input': ['Kiểm tra embedding văn bản pháp luật tiếng Việt.']})
    vector = reply['data'][0]['embedding']
    result = {'model': reply.get('model', model_id), 'dimensions': len(vector),
              'pricing': selected.get('pricing'), 'usage': reply.get('usage'),
              'catalog_model': selected, 'status': 'one-real-embedding-probe-succeeded'}
    output = ROOT / 'results'
    output.mkdir(exist_ok=True)
    (output / 'embedding_probe.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['model', 'dimensions', 'pricing', 'usage', 'status']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
