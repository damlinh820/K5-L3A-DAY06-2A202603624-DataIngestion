"""A: token windows; B: full articles; C: split long articles at original clauses."""
import hashlib
import re

from .extract import provenance
from .tokenizer import count_tokens, windows

ARTICLE = re.compile(r'^Điều\s+(\d+[a-z]?)\.', re.M)
CHAPTER = re.compile(r'^Chương\s+([IVXLCDM]+)\b')
SECTION = re.compile(r'^Mục\s+(\d+)\b')
CLAUSE = re.compile(r'^(\d+)\.\s')


def units(text, spans):
    markers = {0: ('preface', None)}
    previous_doc = None
    for span in spans:
        if span['document_id'] != previous_doc:
            markers[span['start']] = ('preface', None)
        previous_doc = span['document_id']
    offset, quote_depth = 0, 0
    for line in text.splitlines(keepends=True):
        article = ARTICLE.match(line)
        chapter, section = CHAPTER.match(line), SECTION.match(line)
        if article:
            markers[offset] = ('article', article.group(1))
            quote_depth = 0
        elif chapter and quote_depth == 0:
            markers[offset] = ('chapter', chapter.group(1))
        elif section and quote_depth == 0:
            markers[offset] = ('section', section.group(1))
        quote_depth = max(0, quote_depth + line.count('“') - line.count('”'))
        offset += len(line)
    result, current_chapter, current_section = [], None, None
    positions = sorted(markers)
    for i, start in enumerate(positions):
        end = positions[i + 1] if i + 1 < len(positions) else len(text)
        kind, value = markers[start]
        if kind == 'chapter':
            current_chapter, current_section = value, None
        elif kind == 'section':
            current_section = value
        result.append({'start': start, 'end': end, 'kind': kind,
                       'article': value if kind == 'article' else None,
                       'chapter': current_chapter, 'section': current_section,
                       'text': text[start:end]})
    return result


def make_chunk(config, text, spans, start, end, unit=None, clause=None, prefix=''):
    body_provenance = provenance(spans, start, end)
    if not body_provenance:
        raise ValueError('Chunk body has no source provenance')
    first, last = body_provenance[0], body_provenance[-1]
    value = prefix + text[start:end]
    key = f'{config}\0{start}\0{end}\0{value}'
    context = []
    if prefix and unit:
        context = provenance(spans, unit['start'], unit['start'] + len(prefix.rstrip('\n')))
    return {'chunk_id': hashlib.sha256(key.encode()).hexdigest()[:32],
            'config': config, 'document_id': first['document_id'], 'source': first['source'],
            'part': first['part'], 'page': first['page'], 'page_end': last['page'],
            'article': unit.get('article') if unit else None,
            'chapter': unit.get('chapter') if unit else None,
            'section': unit.get('section') if unit else None,
            'clause': clause, 'unit_type': unit['kind'] if unit else 'token_window',
            'text': value, 'n_tokens': count_tokens(value), 'prefix': prefix,
            'body_start': start, 'body_end': end,
            'provenance': body_provenance, 'context_provenance': context}


def fixed(text, spans, size=512, overlap=64):
    result = []
    for window in windows(text, size, overlap):
        chunk = make_chunk('A', text, spans, window['start'], window['end'])
        chunk.update({k: window[k] for k in ['token_start', 'token_end']})
        result.append(chunk)
    return result


def heading(text, spans):
    return [make_chunk('B', text, spans, u['start'], u['end'], u) for u in units(text, spans)]


def clause_boundaries(body):
    offset, quote_depth, last_number = 0, 0, 0
    starts = []
    for line in body.splitlines(keepends=True):
        match = CLAUSE.match(line)
        if match and quote_depth == 0 and int(match.group(1)) > last_number:
            last_number = int(match.group(1))
            starts.append((offset, match.group(1)))
        quote_depth = max(0, quote_depth + line.count('“') - line.count('”'))
        offset += len(line)
    return starts


def hybrid(text, spans, threshold=512):
    result = []
    for u in units(text, spans):
        if u['kind'] != 'article' or count_tokens(u['text']) <= threshold:
            result.append(make_chunk('C', text, spans, u['start'], u['end'], u))
            continue
        heading_line, separator, body = u['text'].partition('\n')
        body_start = u['start'] + len(heading_line) + len(separator)
        starts = clause_boundaries(body)
        if not starts:
            result.append(make_chunk('C', text, spans, u['start'], u['end'], u))
            continue
        boundaries = [(0, None)] if starts[0][0] > 0 else []
        boundaries.extend(starts)
        prefix = heading_line + '\n'
        for i, (relative, clause) in enumerate(boundaries):
            end = body_start + boundaries[i + 1][0] if i + 1 < len(boundaries) else u['end']
            result.append(make_chunk('C', text, spans, body_start + relative, end, u, clause, prefix))
    return result
