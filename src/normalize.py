"""Reflow printed lines without changing words, punctuation or legal markers."""
import re
import unicodedata

STRUCTURAL = re.compile(r'^(?:Điều\s+\d+[a-z]?\.|Chương\s+[IVXLCDM]+\b|Mục\s+\d+\b|\d+\.\s|[a-zđ]\)\s)')


def normalize(text):
    lines = [re.sub(r'[ \t]+', ' ', x).strip() for x in unicodedata.normalize('NFC', text).replace('\u00a0', ' ').splitlines()]
    output = []
    previous = ''
    for line in lines:
        if not line or re.search(r'CÔNG BÁO\s*/\s*Số', line, re.I) or re.fullmatch(r'\d+', line):
            continue
        keep_break = (not output or STRUCTURAL.match(line)
                      or re.match(r'^(Chương\s|Mục\s)', previous)
                      or (previous.startswith('Điều ') and not line[0].islower()))
        if output and not keep_break:
            output[-1] += ' ' + line
        else:
            output.append(line)
        previous = line
    return '\n'.join(output)
