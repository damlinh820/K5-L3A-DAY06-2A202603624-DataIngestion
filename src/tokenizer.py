"""Fixed cl100k_base tokenizer with Unicode-safe token window boundaries."""
import os
from pathlib import Path

import tiktoken

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('TIKTOKEN_CACHE_DIR', str(ROOT / 'results/tokenizer_cache'))


def encoder():
    return tiktoken.get_encoding('cl100k_base')


def count_tokens(text):
    return len(encoder().encode(text, disallowed_special=()))


def windows(text, size=512, overlap=64):
    if size < 1 or not 0 <= overlap < size:
        raise ValueError('Require 0 <= overlap < size')
    enc = encoder()
    tokens = enc.encode(text, disallowed_special=())
    if not tokens:
        return
    decoded, offsets = enc.decode_with_offsets(tokens)
    if decoded != text:
        raise ValueError('Tokenizer round trip failed')
    offsets.append(len(text))
    start = 0
    while start < len(tokens):
        end = min(start + size, len(tokens))
        # A token can be only part of a Vietnamese UTF-8 character: avoid U+FFFD.
        while end < len(tokens) and offsets[end] == offsets[end - 1]:
            end -= 1
        if end <= start:
            raise ValueError('Token window too small for a Unicode character')
        yield {'token_start': start, 'token_end': end,
               'start': offsets[start], 'end': offsets[end],
               'text': text[offsets[start]:offsets[end]]}
        if end == len(tokens):
            break
        start = end - overlap
        if start <= 0 and end <= overlap:
            raise ValueError('Token windows cannot make progress')
        while start > 0 and offsets[start] == offsets[start - 1]:
            start -= 1
