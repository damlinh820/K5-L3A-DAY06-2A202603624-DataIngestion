"""Check persistent Chroma using real API vectors for isolated non-corpus strings."""
import argparse
import importlib.metadata
import json
import os
import subprocess
import sys
from pathlib import Path

import chromadb
import httpx
from chromadb.config import Settings
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'results/chroma_setup_probe'
COLLECTION = 'phase1_infrastructure_probe'


def collection():
    client = chromadb.PersistentClient(path=str(DB), settings=Settings(anonymized_telemetry=False))
    return client.get_or_create_collection(COLLECTION, embedding_function=None,
        configuration={'hnsw': {'space': 'cosine'}})


def verify_reopened():
    coll = collection()
    vector = coll.get(ids=['setup-one'], include=['embeddings'])['embeddings'][0].tolist()
    result = coll.query(query_embeddings=[vector], n_results=1)
    filtered = coll.query(query_embeddings=[vector], n_results=2, where={'probe_group': 'b'})
    assert coll.count() == 2, 'Expected two infrastructure probe records after reopening'
    assert result['ids'][0] == ['setup-one'], 'Exact-vector neighbor was not retrieved'
    assert filtered['ids'][0] == ['setup-two'], 'Metadata filter did not restrict group b'
    print(json.dumps({'reopened_count': coll.count(), 'top1_id': result['ids'][0][0],
                      'filtered_ids': filtered['ids'][0], 'metric': 'cosine',
                      'process_id': os.getpid()}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--read-only', action='store_true')
    args = parser.parse_args()
    if args.read_only:
        verify_reopened()
        return
    load_dotenv(ROOT / '.env')
    load_dotenv(ROOT / 'starter/.env')
    key = os.getenv('OPENROUTER_API_KEY')
    if not key:
        raise SystemExit('Configure OPENROUTER_API_KEY locally; do not paste it into chat.')
    # These are setup fixtures, not legal corpus pages or benchmark questions.
    texts = ['Kiểm tra lưu bền vững của kho vector, bản ghi một.',
             'Kiểm tra bộ lọc metadata, bản ghi hai.']
    with httpx.Client(timeout=60) as client:
        response = client.post('https://openrouter.ai/api/v1/embeddings',
            headers={'Authorization': 'Bearer ' + key},
            json={'model': 'openai/text-embedding-3-small', 'input': texts})
        if response.status_code != 200:
            raise RuntimeError(f'OpenRouter HTTP {response.status_code}; no fallback vectors used')
        body = response.json()
    vectors = [row['embedding'] for row in sorted(body['data'], key=lambda item: item['index'])]
    assert len(vectors) == 2 and all(len(v) == 1536 for v in vectors)
    coll = collection()
    ids = ['setup-one', 'setup-two']
    metadata = [{'probe_group': 'a'}, {'probe_group': 'b'}]
    coll.upsert(ids=ids, documents=texts, embeddings=vectors, metadatas=metadata)
    first_count = coll.count()
    coll.upsert(ids=ids, documents=texts, embeddings=vectors, metadatas=metadata)
    assert coll.count() == first_count == 2, 'Repeated upsert changed record count'
    process = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--read-only'],
                             capture_output=True, text=True, encoding='utf-8', check=True)
    read_result = json.loads(process.stdout.strip().splitlines()[-1])
    report = {'status': 'passed', 'model': 'openai/text-embedding-3-small',
              'dimensions': 1536, 'chroma_version': importlib.metadata.version('chromadb'),
              'path': 'results/chroma_setup_probe', 'first_write_count': first_count,
              'repeat_upsert_count': coll.count(), 'reader_check': read_result,
              'usage': body.get('usage'),
              'scope': 'Isolated setup fixtures with real API vectors; no corpus retrieval or benchmark results.'}
    (ROOT / 'results/store_probe.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
