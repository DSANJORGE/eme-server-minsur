"""Carga el Banco 2026 (Ciberseguridad + DDHH) en el eme-server local.

Lee los 4 CSV que genera build_import.py en Banco_2026 y los mete por las
APIs JSON (PUT lists/data por fila, POST module/asset/data/create para las
imágenes, DELETE para las filas viejas que sobran). Idempotente: se puede
repetir tras regenerar los CSV.

Uso: python3 banco2026_load.py [--sin-assets] [--img-local] [--solo-con-imagen]
  --solo-con-imagen  omite (y borra del servidor) las preguntas que no tienen fila Asset
  --img-local  descarga las imágenes de http://127.0.0.1:8765 (python3 -m http.server 8765
               dentro de Banco_2026/imagenes) porque la JVM local no resuelve raw.githubusercontent.com
"""
import csv, json, os, sys, time, urllib.request, urllib.parse

H = 'http://localhost:8080/site/mediadb/services'
BANCO = ('/Users/DSANJORGE/Documents/Claude/Projects/Minsur (Altal)/'
         'TestU - Muestra Mejorada (ALTAL)/Banco_2026')

# Los CSV numeran desde 1 por curso; en el servidor conviven, así que Ciber va desplazado.
CURSOS = {
    'DDHH':           dict(offset=0,     tutorial='AZ_tFsHKimsE6yOlqXpA', carpeta='Tutorials/Derechos humanos'),
    'Ciberseguridad': dict(offset=10000, tutorial='ciberseguridad-1',     carpeta='Tutorials/Ciberseguridad'),
}
TIPO = {'Heading': 'heading', 'Paragraph': 'paragraph', 'Asset': 'asset', 'Multiple Choice Question': 'mcq'}
ROL = {'Feature Image': 'featureimage', 'Exercise': 'exercise', 'Source': 'source', 'Heading': 'Heading', '': ''}

COOKIE = ''

def call(method, url, body=None, form=None):
    data = json.dumps(body).encode() if body is not None else (urllib.parse.urlencode(form).encode() if form else None)
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={'Content-Type': 'application/json' if body is not None else 'application/x-www-form-urlencoded',
                                          'Cookie': COOKIE})
    for intento in range(8):  # ponytail: otros agentes reinician Tomcat (~10 s) mientras cargamos; esperar y reintentar
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read() or b'{}'), r.headers
        except urllib.error.HTTPError as e:
            if e.code in (401, 403) and intento < 7 and not url.endswith('/login'):   # reinicio = sesión admin nueva
                time.sleep(5); login(); req.add_header('Cookie', COOKIE); continue
            return {'response': {'status': 'http %d' % e.code}}, e.headers
        except (ConnectionResetError, urllib.error.URLError, ConnectionRefusedError):
            if intento == 7:
                raise
            time.sleep(10)

def login():
    global COOKIE
    _, hdr = call('POST', H + '/authentication/login', form={'accountname': 'admin', 'password': 'admin'})
    COOKIE = '; '.join(c.split(';')[0] for c in hdr.get_all('Set-Cookie') or [])
    assert 'emekey=' in COOKIE, 'login admin falló'

def ids_en(table):
    q = {'page': '1', 'hitsperpage': '5000', 'query': {'terms': [{'field': 'id', 'operation': 'matches', 'value': '*'}]}}
    r, _ = call('POST', f'{H}/lists/search/{table}.json', q)
    return {x['id'] for x in r.get('results', [])}

def put(table, row):
    body = {k: v for k, v in row.items() if v not in (None, '')}
    r, _ = call('PUT', f"{H}/lists/data/{table}/{row['id']}.json", body)
    ok = r.get('response', {}).get('status') == 'ok'
    if not ok:
        print('  !', table, row['id'], r.get('response'))
    return ok

def off(v, n):
    return str(int(v) + n) if v not in (None, '') else ''

def filas(curso, tabla):
    return list(csv.DictReader(open(os.path.join(BANCO, 'testu_import_' + curso, tabla + '.csv'), encoding='utf-8')))

def main(con_assets=True):
    login()
    nuevos = {'componentsection': set(), 'componentcontent': set(), 'entityquestion': set()}
    assets = {}
    for curso, cfg in CURSOS.items():
        n = cfg['offset']
        secs = [dict(id=off(r['id'], n), name=r['name'], ordering=r['ordering'],
                     playbackentitymoduleid='entitytutorial', playbackentityid=cfg['tutorial'])
                for r in filas(curso, 'componentsection')]
        qs = [dict(id=off(r['id'], n), question=r['question'], correctoption=r['correctoption'],
                   mcqcognitivelevel=r['cognitivelevel'], rationale=r['rationale'],
                   **{k: r[k] for k in ('option_a', 'option_b', 'option_c', 'option_d', 'option_e', 'option_f')})
              for r in filas(curso, 'entityquestion')]
        cont = [dict(id=off(r['id'], n), componenttype=TIPO[r['componenttype']], contentrole=ROL[r['contentrole']],
                     content=r['content'], componentsectionid=off(r['componentsectionid'], n),
                     questionid=off(r['questionid'], n), ordering=r['ordering'], assetid=r['assetid'])
                for r in filas(curso, 'componentcontent')]
        if SOLO_CON_IMAGEN:  # ponytail: demo — ocultar preguntas sin fila Asset (el DELETE de sobrantes las quita del servidor)
            con_img = {c['questionid'] for c in cont if c['componenttype'] == 'asset'}
            cont = [c for c in cont if not c['questionid'] or c['questionid'] in con_img]
            qs = [q for q in qs if q['id'] in con_img]
        for r in filas(curso, 'assets'):
            assets[r['id']] = dict(id=r['id'], fetchurl=r['fetchurl'], name=r['name'], importstatus='needsdownload',
                                   sourcepath='%s/%s' % (cfg['carpeta'], r['name']))
        for tabla, rows in (('componentsection', secs), ('entityquestion', qs), ('componentcontent', cont)):
            malas = sum(not put(tabla, r) for r in rows)
            nuevos[tabla] |= {r['id'] for r in rows}
            print(f'{curso:15s} {tabla:17s} {len(rows):4d} filas, {malas} fallidas')

    # filas viejas (cargas de prueba anteriores) que no están en el banco 2026
    for tabla, ids in nuevos.items():
        sobran = ids_en(tabla) - ids
        for i in sobran:
            r, _ = call('DELETE', f'{H}/lists/data/{tabla}/{i}.json')
            if r.get('response', {}).get('status') != 'ok':
                print('  ! delete', tabla, i, r.get('response'))
        print(f'{tabla:17s} borradas {len(sobran)} viejas → {len(ids_en(tabla))} en tabla (esperadas {len(ids)})')

    if con_assets:
        creados = saltados = reintentados = malos = 0
        for aid, a in sorted(assets.items()):
            if IMG_LOCAL:  # la JVM local no resuelve raw.githubusercontent.com; servir imagenes/ con http.server
                a['fetchurl'] = f"{IMG_LOCAL}/{a['name']}"
            r, _ = call('GET', f'{H}/module/asset/data/{aid}.json')
            if r.get('response', {}).get('status') == 'ok':
                if r['data'].get('importstatus', {}).get('id') != 'error':
                    saltados += 1; continue
                r, _ = call('PUT', f'{H}/module/asset/data/{aid}.json', a)   # descarga fallida: reapuntar y reencolar
                reintentados += 1
            else:
                r, _ = call('POST', f'{H}/module/asset/data/create.json', a)
                creados += 1
            if not (r.get('response', {}).get('status') == 'ok' and r['response'].get('id') == aid):
                malos += 1; print('  ! asset', aid, r.get('response'))
        print(f'assets: {len(assets)} referenciados · {creados} creados · {reintentados} reencolados · {saltados} ya estaban · {malos} fallidos')
        if creados or reintentados:  # el evento periódico corre cada 5 h; dispararlo ahora
            call('GET', 'http://localhost:8080/site/catalog/events/importing/fetchdownloads.html')
            print('fetchdownloads disparado; las previews tardan ~1 min en generarse')

IMG_LOCAL = 'http://127.0.0.1:8765' if '--img-local' in sys.argv else ''
SOLO_CON_IMAGEN = '--solo-con-imagen' in sys.argv

if __name__ == '__main__':
    main(con_assets='--sin-assets' not in sys.argv)
