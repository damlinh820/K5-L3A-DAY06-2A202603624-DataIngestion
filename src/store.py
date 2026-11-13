"""Persistent Chroma namespaces for the locked legal chunking experiment."""
import json
from pathlib import Path

import chromadb
from chromadb.config import Settings

ROOT = Path(__file__).resolve().parents[1]


def metadata(chunk):
    result = {key: chunk[key] for key in
              ['document_id', 'source', 'part', 'page', 'page_end', 'unit_type', 'n_tokens']}
    for key in ['chapter', 'article', 'section', 'clause']:
        if chunk.get(key) is not None:
            result[key] = str(chunk[key])
    result['provenance_json'] = json.dumps(chunk['provenance'], ensure_ascii=False)
    result['context_provenance_json'] = json.dumps(chunk['context_provenance'], ensure_ascii=False)
    return result


class LegalStore:
    def __init__(self, model, path=None):
        self.model = model
        self.client = chromadb.PersistentClient(path=str(path or ROOT / 'results/chroma'),
                                              settings=Settings(anonymized_telemetry=False))

    def collection(self, config):
        if config not in {'A', 'B', 'C'}:
            raise ValueError('Unknown legal strategy')
        collection = self.client.get_or_create_collection('land_law_' + config.lower(),
            embedding_function=None, configuration={'hnsw': {'space': 'cosine'}},
            metadata={'model': self.model, 'metric': 'cosine'})
        if collection.metadata.get('model') != self.model:
            raise ValueError('Existing collection uses a different model; refusing to mix embeddings')
        return collection

    def replace(self, config, chunks, vectors):
        if len(chunks) != len(vectors):
            raise ValueError('Chunks/vector count mismatch')
        coll = self.collection(config)
        old_ids = set(coll.get(include=[])['ids'])
        ids = [c['chunk_id'] for c in chunks]
        if len(ids) != len(set(ids)):
            raise ValueError('Duplicate chunk IDs')
        for start in range(0, len(chunks), 128):
            selected = chunks[start:start + 128]
            coll.upsert(ids=[c['chunk_id'] for c in selected], documents=[c['text'] for c in selected],
                        metadatas=[metadata(c) for c in selected], embeddings=vectors[start:start + 128])
        obsolete = sorted(old_ids - set(ids))
        for start in range(0, len(obsolete), 128):
            coll.delete(ids=obsolete[start:start + 128])
        actual = set(coll.get(include=[])['ids'])
        if actual != set(ids):
            raise RuntimeError('Persisted chunk IDs differ from expected snapshot')
        return {'count': coll.count(), 'obsolete_removed': len(obsolete)}

    def search(self, config, query_vector, filters=None, top_k=3):
        coll = self.collection(config)
        if not coll.count():
            return []
        clauses = [{key: value} for key, value in (filters or {}).items()]
        where = {'$and': clauses} if len(clauses) > 1 else clauses[0] if clauses else None
        result = coll.query(query_embeddings=[query_vector], n_results=min(top_k, coll.count()),
                            where=where, include=['documents', 'metadatas', 'distances'])
        return [{'chunk_id': key, 'text': text, 'metadata': meta, 'cosine_distance': float(distance),
                 'score': 1 - float(distance)} for key, text, meta, distance in zip(
                     result['ids'][0], result['documents'][0], result['metadatas'][0], result['distances'][0])]
