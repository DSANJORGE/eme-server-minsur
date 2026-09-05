#!/usr/bin/env python3
"""Registra un PDF ya subido como documento de referencia de un tutorial y
lo deja citable por IRIS: entityasset + una entityassetpage por página
(texto de pdftotext) + embedding en embed.emediaworkspace.com.

    python3 embed_doc.py <assetid> <entitytutorial> "<título visible>" <pages.txt> <fecha ISO>

Idempotente: reutiliza el entityasset con ese título y las páginas ya
creadas. Cookie admin en /tmp/adm.txt (ver embed_manual.py, del que sale).
"""
import json, sys, time, urllib.request

H = 'http://localhost:8080/site/mediadb/'
ES = 'http://localhost:9200/site_catalog1788378629820'
cookies = '; '.join(l.split('\t')[5] + '=' + l.split('\t')[6].strip() for l in open('/tmp/adm.txt') if '\t' in l)


def api(path, method='POST', body=None):
    r = urllib.request.Request(H + path, data=json.dumps(body).encode() if body is not None else None, method=method,
                               headers={'Content-Type': 'application/json', 'Cookie': cookies})
    return json.loads(urllib.request.urlopen(r, timeout=120).read().decode())


def es(path, body=None):
    r = urllib.request.Request(ES + path, data=json.dumps(body).encode() if body else None,
                               headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(r, timeout=30).read().decode())


def main():
    asset, tutorial, title, pages_file, date = sys.argv[1:6]
    pages = [p.strip() for p in open(pages_file, encoding='utf-8').read().split('\f')]
    while pages and not pages[-1]: pages.pop()
    hits = es('/entityasset/_search', {'query': {'term': {'name': title}}, 'size': 1})['hits']['hits']
    hits = [h for h in hits if h['_source'].get('name') == title]
    if hits:
        ea = hits[0]['_id']
    else:
        ea = api('services/module/entityasset/create.json', body={'name': title, 'primarymedia': asset, 'primaryimage': asset,
                                                                  'entitytutorial': tutorial, 'entity_date': date})['response']['id']
    print('entityasset', ea)
    existing = {h['_source']['pagenum']: h['_id'] for h in es('/entityassetpage/_search?size=500&q=entityasset:' + ea)['hits']['hits']}
    ids = {}
    for i, text in enumerate(pages, start=1):
        if i in existing:
            ids[i] = existing[i]; continue
        r = api('services/module/entityassetpage/create.json', body={'name': '%s - Page %d' % (title, i), 'pagenum': i, 'entityasset': ea,
                                                                     'primaryimage': asset, 'parentasset': asset, 'entity_date': date, 'markdowncontent': text})
        ids[i] = r['response']['id']
    print('pages', len(ids))
    modtime = es('/asset/' + asset)['_source'].get('assetmodificationdate')
    api('services/module/entityasset/data/%s.json' % ea, 'PUT', {'totalpages': len(pages), 'pagescreatedfor': asset + '|' + str(modtime)})
    payload = {'doc_id': 'entityasset_' + ea, 'file_name': title, 'file_type': 'application/pdf', 'creation_date': date[:10],
               'pages': [{'page_id': 'entityassetpage_' + ids[i], 'text': t, 'page_label': str(i)} for i, t in enumerate(pages, start=1) if len(t) > 20]}
    r = urllib.request.Request('https://embed.emediaworkspace.com/save', data=json.dumps(payload).encode(),
                               headers={'Content-Type': 'application/json', 'Authorization': 'Bearer YOUR_SECRET_TOKEN', 'x-customerkey': 'demo'})
    print('save:', urllib.request.urlopen(r, timeout=600).read().decode()[:200])
    api('services/module/entityasset/data/%s.json' % ea, 'PUT',
        {'entityembeddingstatus': 'embedded', 'entityembeddeddate': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())})
    print('embedded', ea)


if __name__ == '__main__':
    main()
