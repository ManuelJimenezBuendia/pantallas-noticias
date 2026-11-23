"""Guarda las últimas noticias de la web de la UPCT en un JSON para la página de noticias.

Uso: python scripts/upct.py datos/upct.json

La web de la UPCT no tiene RSS ni deja leerla desde otra web, así que esto lo hace una tarea
programada de GitHub (.github/workflows/upct.yml) cada hora:
- lee el listado de noticias de actualidad (una página, unas 13 noticias);
- de cada noticia nueva lee su página para sacar el resumen (la entradilla o, si no tiene, el
  primer párrafo) y la foto mediana (1200x800); las que ya estaban no se vuelven a pedir;
- solo reescribe el JSON si las noticias han cambiado (así no hay un commit cada hora);
- si no encuentra ninguna noticia (la web ha cambiado), no toca el JSON y termina con error
  para que GitHub avise.

El robots.txt de www.upct.es permite leer /destacados/ y /noticias/. Solo biblioteca estándar.
"""
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

LISTADO = "https://www.upct.es/destacados/noticias.php?ubicacion=general&op=2"
AGENTE = "pantallas-noticias/1.0"
MAXIMO = 15       # noticias que se guardan (el listado trae unas 13)
PAUSA = 1.0       # segundos entre peticiones, para no cargar la web
MESES = {m: i + 1 for i, m in enumerate("ene feb mar abr may jun jul ago sep oct nov dic".split())}
MESES.update({"jan": 1, "apr": 4, "aug": 8, "dec": 12})


def pedir(url):
    req = urllib.request.Request(url, headers={"User-Agent": AGENTE})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")


def url_limpia(url, base):
    """URL absoluta, con los espacios y tildes codificados (las fotos los llevan)."""
    url = urllib.parse.urljoin(base, html.unescape(url.strip()))
    partes = urllib.parse.urlsplit(url)
    ruta = urllib.parse.quote(urllib.parse.unquote(partes.path), safe="/")
    return urllib.parse.urlunsplit(partes._replace(path=ruta))


def texto(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def fecha_iso(s):
    """'21.Nov.2026' -> '2026-11-21'."""
    m = re.search(r"(\d{1,2})\.([A-Za-z]{3})[a-z]*\.(\d{4})", s or "")
    if not m or m.group(2).lower() not in MESES:
        return ""
    return f"{m.group(3)}-{MESES[m.group(2).lower()]:02d}-{int(m.group(1)):02d}"


def leer_listado():
    pagina = pedir(LISTADO)
    noticias = []
    for enlace, cuerpo in re.findall(r'<a\s+class="box"\s+href="([^"]+)"\s*>(.*?)</a>', pagina, re.S):
        if "/noticias/" not in enlace:
            continue
        img = re.search(r'<img[^>]+src="([^"]+)"[^>]*alt=\'([^\']*)\'', cuerpo)
        titulo = re.search(r"<h3[^>]*>(.*?)</h3>", cuerpo, re.S)
        fecha = re.search(r'class="fecha_noticias"[^>]*>([^<]+)<', cuerpo)
        noticias.append({
            "enlace": url_limpia(enlace, LISTADO),
            "titulo": texto(titulo.group(1)) if titulo else "",
            "fecha": fecha_iso(fecha.group(1)) if fecha else "",
            "foto": url_limpia(img.group(1), LISTADO) if img else "",
            "pieFoto": texto(img.group(2)) if img else "",
        })
    return [n for n in noticias if n["titulo"]]


def completar(noticia):
    """Resumen y foto mediana, de la página de la noticia."""
    pagina = pedir(noticia["enlace"])
    desc = re.search(r'<meta name="description" content="([^"]*)"', pagina)
    noticia["resumen"] = texto(desc.group(1)) if desc else ""
    if not noticia["resumen"]:
        # Sin entradilla: el primer párrafo con texto del cuerpo de la noticia.
        cuerpo = re.search(r"class=.descripcion_noticia.[^>]*>(.*)", pagina, re.S)
        for parrafo in re.findall(r"<p[^>]*>(.*?)</p>", cuerpo.group(1) if cuerpo else "", re.S):
            if len(texto(parrafo)) > 40:
                noticia["resumen"] = texto(parrafo)
                break
    # La primera dirección de /imagenes_medianas/ de la página: en noviembre de 2026 la UPCT dejó
    # comentada la etiqueta twitter:image que la llevaba; la foto principal de la noticia también
    # la usa (con dirección relativa). Las demás noticias de la página van con /imagenes/.
    mediana = re.search(r'["\']([^"\']*/imagenes_medianas/[^"\']+)["\']', pagina)
    if mediana:
        noticia["fotoMediana"] = url_limpia(mediana.group(1), noticia["enlace"])
    if not noticia["fecha"]:
        pub = re.search(r"Publicada el ([^<]+)<", pagina)
        noticia["fecha"] = fecha_iso(pub.group(1)) if pub else ""
    return noticia


def main():
    salida = sys.argv[1]
    try:
        with open(salida, encoding="utf-8") as f:
            anteriores = json.load(f).get("noticias", [])
    except (OSError, ValueError):
        anteriores = []
    guardadas = {x["enlace"]: x for x in anteriores}

    listado = leer_listado()[:MAXIMO]
    if not listado:
        sys.exit("No se ha encontrado ninguna noticia en el listado: ¿ha cambiado la web de la UPCT?")

    noticias, nuevas = [], 0
    for noticia in listado:
        if noticia["enlace"] in guardadas:
            noticias.append(guardadas[noticia["enlace"]])
            continue
        time.sleep(PAUSA)
        try:
            noticias.append(completar(noticia))
            nuevas += 1
        except Exception as e:  # una noticia que falla no para el resto (se reintenta en la próxima)
            print("aviso:", noticia["enlace"], e, file=sys.stderr)

    if noticias == anteriores:
        print(f"Sin cambios ({len(noticias)} noticias).")
        return
    datos = {"fuente": LISTADO,
             "actualizado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "noticias": noticias}
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"{len(noticias)} noticias, {nuevas} nuevas.")


if __name__ == "__main__":
    main()
