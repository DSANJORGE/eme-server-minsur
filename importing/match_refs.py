#!/usr/bin/env python3
"""Referencia (cita + documento + página) por pregunta, sacada del texto de
un manual. Dos pasos:

    python3 match_refs.py candidates <pages.txt> "<título>" <id_min> <id_max> <out.json>
        tf-idf por página + solapamiento por oración → hasta 5 candidatos por
        pregunta en <out.json> (para que un LLM o una persona elija).
    python3 match_refs.py apply <choice.json>
        <choice.json> = {"<qid>": {"page": N, "quote": "...", "cite": "..."}} →
        PUT sourcequote/sourcecite/sourcepage en entityquestion (localhost,
        cookie admin en /tmp/adm.txt). Sin entrada = sin referencia.

<pages.txt> es la salida de `pdftotext` (páginas separadas por \\f).
ponytail: sin embeddings; la demo necesita una cita plausible por pregunta.
"""
import json, math, os, re, sys, unicodedata, urllib.request

H = 'http://localhost:8080/site/mediadb/'
STOP = '''de la el los las y o u a en que se del al por para con sin sobre un una unos unas es son fue ser
como mas pero su sus lo le les este esta estos estas ese esa esos esas que cual cuales como cuando donde
tambien entre hasta desde muy ya si no ni cada todo toda todos todas otro otra otros otras puede pueden
debe deben ha han hay ante bajo tras segun mediante dentro fuera antes despues traves respecto ademas
persona personas empresa empresas colaborador colaboradora colaboradores minsur curso caso trabajo area
usuario usuarios informacion correo forma parte mismo misma tipo manera ejemplo situacion deber hacer
quien primer primera mejor mayor menor solo siempre nunca porque cuenta cuentas tener tiene tienen'''.split()


def plain(s):
    s = unicodedata.normalize('NFKD', s.lower())
    return ''.join(c for c in s if not unicodedata.combining(c))


STOP = set(STOP)


def terms(s):
    return [t for t in re.findall(r'[a-z0-9]{4,}', plain(s)) if t not in STOP]


def sentences(page):
    text = re.sub(r'\s+', ' ', page)
    out = []
    for s in re.split(r'(?<=[.;:!?])\s+(?=[A-ZÁÉÍÓÚÑ¿¡•])', text):
        s = s.strip(' •-–')
        words = s.split()
        digits = sum(c.isdigit() for c in s)
        # Frases reales: 9-60 palabras, pocas cifras, sin cabeceras de página
        # ("46 PNA 2021-2025 Capítulo II ...") ni índices ("5.3. Mecanismo...").
        if not 9 <= len(words) <= 60 or digits > len(s) * 0.06: continue
        if re.match(r'^\d', s) or re.search(r'\bCapítulo [IVX]+\b', s) or 'PNA 2021-2025' in s[:40]: continue
        if s.count('.') > 6 or '|' in s: continue
        out.append(s)
    return out


def candidates(pages_file, title, lo, hi, out):
    pages = [p.strip() for p in open(pages_file, encoding='utf-8').read().split('\f')]
    ptoks = [terms(p) for p in pages]
    n = len(pages)
    df = {}
    for toks in ptoks:
        for t in set(toks): df[t] = df.get(t, 0) + 1
    idf = {t: math.log(1 + n / (1 + d)) for t, d in df.items()}
    tf = [{t: toks.count(t) / max(1, len(toks)) for t in set(toks)} for toks in ptoks]
    psents = [sentences(p) for p in pages]
    skip = {int(x) for x in os.environ.get('SKIP_PAGES', '').split(',') if x}  # páginas 1-based sin contenido citable

    qs = [q for q in json.load(open('/tmp/questions_all.json')) if q['id'].isdigit() and lo <= int(q['id']) <= hi]
    res = []
    for q in sorted(qs, key=lambda q: int(q['id'])):
        ok = q.get('option_' + q.get('correctoption', 'a').lower(), '')
        qt = set(terms(q['question'] + ' ' + ok + ' ' + q.get('rationale', '')))
        qw = {t: idf.get(t, 0) * (2 if t in set(terms(q['question'] + ' ' + ok)) else 1) for t in qt}
        pscore = lambda i: sum(tf[i].get(t, 0) * qw[t] for t in qt) if len(ptoks[i]) > 40 and i + 1 not in skip else 0
        top = sorted(range(n), key=pscore, reverse=True)[:5]
        cands = []
        for i in top:
            for s in psents[i]:
                st = set(terms(s))
                sc = sum(qw[t] for t in qt & st) / math.sqrt(len(st) + 4)
                cands.append((sc, i + 1, s))
        cands.sort(reverse=True)
        res.append({'id': q['id'], 'question': q['question'], 'answer': ok, 'rationale': q.get('rationale', '')[:400],
                    'cite': title, 'candidates': [{'page': p, 'quote': s, 'score': round(sc, 2)} for sc, p, s in cands[:6]]})
        print(q['id'], [(p, round(sc, 2)) for sc, p, _ in cands[:3]])
    json.dump(res, open(out, 'w'), ensure_ascii=False, indent=1)
    print('preguntas', len(res), '→', out)


def apply(choice_file):
    choice = json.load(open(choice_file))
    cookies = '; '.join(l.split('\t')[5] + '=' + l.split('\t')[6].strip() for l in open('/tmp/adm.txt') if '\t' in l)
    for qid, c in choice.items():
        body = json.dumps({'sourcequote': c['quote'], 'sourcecite': c['cite'], 'sourcepage': str(c['page'])}).encode()
        r = urllib.request.Request(H + 'services/lists/data/entityquestion/%s.json' % qid, data=body, method='PUT',
                                   headers={'Content-Type': 'application/json', 'Cookie': cookies})
        urllib.request.urlopen(r, timeout=60).read()
    print('aplicadas', len(choice))


if __name__ == '__main__':
    if sys.argv[1] == 'candidates':
        candidates(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6])
    else:
        apply(sys.argv[2])
