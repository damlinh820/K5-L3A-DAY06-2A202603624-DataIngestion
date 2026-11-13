"""Retrieval receives only the question vector and optional user-supplied filter."""
from .store import metadata


def retrieve(store, config, vector, chunk_lookup, user_filter=None):
    hits = store.search(config, vector, filters=user_filter, top_k=3)
    result = []
    for rank, hit in enumerate(hits, 1):
        chunk = chunk_lookup.get(hit['chunk_id'])
        if chunk is None or chunk['text'] != hit['text']:
            raise RuntimeError('Index does not match approved chunk text/IDs')
        if hit['metadata'] != metadata(chunk):
            raise RuntimeError('Retrieved metadata differs from approved chunk snapshot')
        result.append({**hit, 'rank': rank, 'document_id': chunk['document_id'],
                       'source': chunk['source'], 'page': chunk['page'], 'page_end': chunk['page_end'],
                       'article': chunk['article'], 'clause': chunk['clause'],
                       'provenance': chunk['provenance'], 'context_provenance': chunk['context_provenance']})
    return result
