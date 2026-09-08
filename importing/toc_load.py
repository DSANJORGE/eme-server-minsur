"""Índice (tabla de contenidos) de los PDF de referencia → campo `chapters` del
entityasset, una línea por entrada: "p. <página PDF> Título". El visor de la app
lo muestra como índice navegable (los videos usan el mismo campo con "m:ss").

Ningún PDF trae outline, así que se lee el índice impreso con pdftotext -layout
y se corrige el desfase entre numeración impresa y página PDF buscando cada
título en el texto del documento.

Uso: python3 toc_load.py [--dry]
"""
import json, re, subprocess, sys, urllib.request
from collections import Counter

ES = 'http://localhost:9200/site_catalog1788378629820/entityasset'
ORIG = '/Users/DSANJORGE/Code/eme-server-minsur/webapp/WEB-INF/data/site/catalog/originals/Tutorials/'
PDFTOTEXT = '/opt/homebrew/bin/pdftotext'

DOCS = [
    # (entityasset id, pdf, páginas del índice, columnas: corte de caracteres)
    ('AaBpgrCOmR19YlCbKaUd', 'Derechos humanos/Plan_Nacional_Empresas_DDHH_2021-2025.pdf', (7, 8), None),
    ('AaBsxx3_SbjkUhYseP3s', 'Ciberseguridad/Guia_ciberataques_INCIBE.pdf', (2, 2), 80),
]

ENTRY = re.compile(r'^(.*?)\s{2,}(\d{1,3})\s*$')
NUMBERED = re.compile(r'^(\d+(\.\d+)*\.?\s|Capítulo\s)')
STOP = re.compile(r'^(Licencia|Índice|Contenido|pag\.|Guía de ciberataques\s{2,}|Plan Nacional de Acción sobre Empresas y Derechos Humanos 2021-2025\s+\d+)')


def text(pdf, first, last, layout=True):
    args = [PDFTOTEXT] + (['-layout'] if layout else []) + ['-f', str(first), '-l', str(last), pdf, '-']
    return subprocess.run(args, capture_output=True, text=True).stdout


def columns(lines, cut):
    if cut is None:
        return [lines]
    return [[l[:cut] for l in lines], [l[cut:] for l in lines]]


def parse(pdf, pages, cut):
    lines = text(pdf, *pages).split('\n')
    entries = []
    for col in columns(lines, cut):
        pending = ''
        for raw in col:
            line = raw.strip().lstrip('| ').strip()
            if not line or STOP.match(line):
                continue
            m = ENTRY.match(line)
            if not m:
                pending = (pending + ' ' + line).strip()
                continue
            title = m.group(1).strip()
            # ponytail: a heading without page ("Tipos de ciberataques") glued
            # before a numbered entry is dropped, not merged into it.
            if pending and not NUMBERED.match(title):
                title = pending + ' ' + title
            pending = ''
            entries.append((re.sub(r'\s+', ' ', title), int(m.group(2))))
    return entries


def key(title):
    words = re.sub(r'^(\d+(\.\d+)*\.?|Capítulo\s+[IVX]+)\s*', '', title).lower().split()
    return ' '.join(words[:3])


def printed_map(pdf):
    """Página impresa → página PDF, leída del número que cada página lleva en
    cabecera o pie (el desfase cambia dentro del DDHH: hay un decreto insertado)."""
    pages = text(pdf, 1, 999).split('\f')
    m = {}
    for i, p in enumerate(pages, 1):
        ls = [l.strip() for l in p.split('\n') if l.strip()]
        for l in ls[:3] + ls[-3:]:
            for tok in re.findall(r'(?:^|\s)(\d{1,3})(?:\s|$)', l):
                n = int(tok)
                if i - 6 <= n <= i and n not in m:
                    m[n] = i
    return m


def resolve(pdf, entries):
    m = printed_map(pdf)
    norm = [re.sub(r'\s+', ' ', p.lower()) for p in text(pdf, 1, 999, layout=False).split('\f')]
    out = []
    for title, printed in entries:
        page = m.get(printed)
        if page is None:  # ponytail: page without a readable number → nearest known offset
            below = [n for n in m if n < printed]
            page = printed + (m[max(below)] - max(below) if below else 0)
        ok = key(title) in norm[page - 1] if page - 1 < len(norm) else False
        out.append((title, page, ok))
    return out


def main(dry):
    for docid, rel, pages, cut in DOCS:
        pdf = ORIG + rel
        entries = parse(pdf, pages, cut)
        resolved = resolve(pdf, entries)
        lines = [f'p. {page} {title}' for title, page, _ in resolved]
        print(f'== {rel}: {len(lines)} entradas, {sum(ok for *_, ok in resolved)} verificadas en el texto')
        print('\n'.join(('✓ ' if ok else '✗ ') + l for l, (*_, ok) in zip(lines, resolved)))
        if dry:
            continue
        body = json.dumps({'doc': {'chapters': '\n'.join(lines)}}).encode()
        req = urllib.request.Request(f'{ES}/{docid}/_update', data=body, method='POST',
                                     headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=30) as r:
            print('  ES:', json.loads(r.read()).get('_version'))


if __name__ == '__main__':
    main('--dry' in sys.argv)
