"""OpenRouter embeddings with bounded retries, real-response cache and usage ledger."""
import hashlib
import json
import logging
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import load_dotenv

from .tokenizer import count_tokens

ROOT = Path(__file__).resolve().parents[1]
LOG = logging.getLogger(__name__)


class OpenRouterEmbedder:
    def __init__(self, model='openai/text-embedding-3-small', dimensions=1536):
        load_dotenv(ROOT / '.env')
        load_dotenv(ROOT / 'starter/.env')
        key = os.getenv('OPENROUTER_API_KEY')
        if not key:
            raise RuntimeError('OPENROUTER_API_KEY is missing in local .env; no fallback is permitted')
        self.model, self.dimensions = model, dimensions
        self.client = httpx.Client(timeout=httpx.Timeout(120, connect=30),
                                   headers={'Authorization': 'Bearer ' + key})
        self.cache_path = ROOT / 'results/embedding_cache.jsonl'
        self.cache = {}
        if self.cache_path.exists():
            with self.cache_path.open(encoding='utf-8') as stream:
                for line in stream:
                    row = json.loads(line)
                    if row['model'] == self.model:
                        self._validate(row['vector'])
                        self.cache[row['key']] = row['vector']

    def _validate(self, vector):
        if len(vector) != self.dimensions or not all(math.isfinite(float(v)) for v in vector):
            raise ValueError('Embedding response/cache has invalid dimensions or nonfinite values')
        if not any(vector):
            raise ValueError('Zero embedding is invalid for cosine search')

    def key(self, text):
        return hashlib.sha256((self.model + '\0' + text).encode()).hexdigest()

    def _request(self, texts):
        for attempt in range(1, 4):
            try:
                response = self.client.post('https://openrouter.ai/api/v1/embeddings',
                                            json={'model': self.model, 'input': texts})
            except httpx.TransportError as exc:
                LOG.warning('Embedding transport failure attempt %d: %s', attempt, type(exc).__name__)
                if attempt == 3:
                    raise RuntimeError('Embedding transport failed after 3 attempts; stopped without fallback') from None
                time.sleep(2 ** attempt)
                continue
            if response.status_code == 200:
                return response.json()
            LOG.warning('Embedding HTTP %d, attempt %d', response.status_code, attempt)
            if response.status_code != 429 and response.status_code < 500:
                raise RuntimeError(f'Embedding HTTP {response.status_code}; stopped without fallback')
            if attempt == 3:
                raise RuntimeError(f'Embedding HTTP {response.status_code} after 3 attempts; stopped without fallback')
            time.sleep(2 ** attempt)
        raise RuntimeError('Embedding request did not finish')

    def embed(self, texts, purpose):
        started = time.perf_counter()
        pending = {}
        for text in texts:
            key = self.key(text)
            if key not in self.cache:
                tokens = count_tokens(text)
                if tokens > 8192:
                    raise ValueError(f'Input has {tokens} tokens, exceeding model context; no truncation allowed')
                pending[key] = (text, tokens)
        missing = list(pending.items())
        usage_rows, new_count = [], 0
        while missing:
            batch, batch_tokens = [], 0
            while missing and len(batch) < 32:
                key, (text, tokens) = missing[0]
                if batch and batch_tokens + tokens > 20000:
                    break
                batch.append((key, text))
                batch_tokens += tokens
                missing.pop(0)
            body = self._request([text for _, text in batch])
            if body.get('model') not in {self.model, self.model.split('/', 1)[-1]}:
                raise RuntimeError('Response model does not match locked model')
            rows = sorted(body['data'], key=lambda row: row['index'])
            if [row['index'] for row in rows] != list(range(len(batch))):
                raise ValueError('Embedding response indices/count mismatch')
            for row in rows:
                self._validate(row['embedding'])
            usage = body.get('usage', {})
            ledger = {'at_utc': datetime.now(timezone.utc).isoformat(), 'purpose': purpose,
                      'model': self.model, 'dimensions': self.dimensions, 'inputs': len(batch),
                      'estimated_input_tokens': batch_tokens, 'usage': usage,
                      'input_keys': [key for key, _ in batch]}
            with (ROOT / 'results/embedding_usage.jsonl').open('a', encoding='utf-8', newline='\n') as stream:
                stream.write(json.dumps(ledger, ensure_ascii=False) + '\n')
                stream.flush()
                os.fsync(stream.fileno())
            with self.cache_path.open('a', encoding='utf-8', newline='\n') as stream:
                for (key, _), row in zip(batch, rows):
                    vector = row['embedding']
                    stream.write(json.dumps({'key': key, 'model': self.model, 'vector': vector}) + '\n')
                    self.cache[key] = vector
                stream.flush()
                os.fsync(stream.fileno())
            usage_rows.append(usage)
            new_count += len(batch)
            LOG.info('%s: embedded %d inputs this run; %d left; API tokens=%s cost=%s',
                     purpose, new_count, len(missing), usage.get('total_tokens'), usage.get('cost'))
        token_values = [u.get('total_tokens') for u in usage_rows]
        cost_values = [u.get('cost') for u in usage_rows]
        report = {'requested_inputs': len(texts), 'new_unique_inputs': new_count,
                  'all_inputs_cached': not usage_rows, 'api_calls': len(usage_rows),
                  'actual_api_tokens': sum(token_values) if all(v is not None for v in token_values) else None,
                  'actual_api_cost_usd': sum(cost_values) if all(v is not None for v in cost_values) else None,
                  'seconds': time.perf_counter() - started}
        return [self.cache[self.key(text)] for text in texts], report

    def close(self):
        self.client.close()
