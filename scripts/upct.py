"""Guarda las últimas noticias de la web de la UPCT en un JSON para la página de noticias.

Uso: python scripts/upct.py datos/upct.json

La web de la UPCT no tiene RSS ni deja leerla desde otra web, así que esto lo hace una tarea
programada de GitHub (.github/workflows/upct.yml) cada hora:
- lee el listado de noticias de actualidad (una página, unas 13 noticias);
- de cada noticia nueva lee su página para sacar el resumen (la entradilla o, si no tiene, el
  primer párrafo) y la foto mediana (1200x800). Las que ya estaban no se vuelven a pedir, pero
  se les ponen el titular, la fecha y el pie de foto del listado (por si la UPCT los corrige); si
  ha cambiado la foto, sí se vuelve a pedir su página;
- guarda las 20 más recientes (la página muestra 20 por defecto): las del listado y, detrás,
  las que ya tenía y han salido de él;
- solo reescribe el JSON si las noticias han cambiado (así no hay un commit cada hora);
- si no encuentra ninguna noticia en el listado, o fallan todas las páginas de noticia que ha
  pedido (la web ha cambiado o no deja leerla), no toca el JSON y termina con error para que
  GitHub avise.

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
MAXIMO = 20       # noticias que se guardan: el listado trae unas 13, el resto son anteriores
PAUSA = 1.0       # segundos entre peticiones, para no cargar la web
MESES = {m: i + 1 for i, m in enumerate("ene feb mar abr may jun jul ago sep oct nov dic".split())}
MESES.update({"jan": 1, "apr": 4, "aug": 8, "dec": 12})
# Etiquetas que van dentro de una línea de texto: al quitarlas no se deja espacio (como hace el
# navegador), para que «<b>palabra</b>,» quede «palabra,» y no «palabra ,».
EN_LINEA = "a|abbr|b|cite|code|em|font|i|mark|q|s|small|span|strong|sub|sup|u"


def pedir(url):
    req = urllib.request.Request(url, headers={"User-Agent": AGENTE})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")


def avisar(mensaje):
    """En el registro de la tarea; GitHub lo muestra además como aviso en el resumen."""
    print(f"::warning::{mensaje}")


def url_limpia(url, base):
    """URL absoluta, con los espacios y tildes codificados (las fotos los llevan)."""
    url = urllib.parse.urljoin(base, html.unescape(url.strip()))
    partes = urllib.parse.urlsplit(url)
    ruta = urllib.parse.quote(urllib.parse.unquote(partes.path), safe="/")
    return urllib.parse.urlunsplit(partes._replace(path=ruta))


def sin_comentarios(pagina):
    return re.sub(r"<!--.*?-->", "", pagina, flags=re.S)


def texto(s):
    s = re.sub(rf"</?(?:{EN_LINEA})\b[^>]*>", "", s or "", flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def atributo(etiqueta, nombre):
    """Valor de un atributo de una etiqueta, en cualquier orden y con comillas dobles, simples
    o sin comillas; None si no lo tiene."""
    m = re.search(rf"""\s{nombre}\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'>]+))""", etiqueta, re.I)
    return next(g for g in m.groups() if g is not None) if m else None


def meta(pagina, nombre):
    """Contenido de <meta name="nombre" content="…">."""
    for etiqueta in re.findall(r"<meta\b[^>]*>", pagina, re.I):
        if (atributo(etiqueta, "name") or "").lower() == nombre:
            return atributo(etiqueta, "content") or ""
    return ""


def fecha_iso(s):
    """'21.Nov.2026' -> '2026-11-21' (también 'NOV' o 'noviembre'); '' si no es una fecha."""
    m = re.search(r"(\d{1,2})\.([a-z]{3})[a-z]*\.(\d{4})", s or "", re.I)
    if not m or m.group(2).lower() not in MESES:
        return ""
    try:
        return datetime(int(m.group(3)), MESES[m.group(2).lower()], int(m.group(1))).date().isoformat()
    except ValueError:  # p. ej., 31.Feb
        return ""


def leer_listado():
    pagina = sin_comentarios(pedir(LISTADO))
    noticias, vistas = [], set()
    # Cada noticia es un <a class="box" href="…">, con la foto, la fecha y el titular dentro.
    for a, cuerpo in re.findall(r"(<a\b[^>]*>)(.*?)</a>", pagina, re.S | re.I):
        enlace = atributo(a, "href") or ""
        if "box" not in (atributo(a, "class") or "").split() or "/noticias/" not in enlace:
            continue
        img = re.search(r"<img\b[^>]*>", cuerpo, re.I)
        titulo = re.search(r"<h3\b[^>]*>(.*?)</h3>", cuerpo, re.S | re.I)
        fecha = re.search(r"<(\w+)\b[^>]*\bfecha_noticias\b[^>]*>(.*?)</\1>", cuerpo, re.S | re.I)
        noticia = {
            "enlace": url_limpia(enlace, LISTADO),
            "titulo": texto(titulo.group(1)) if titulo else "",
            "fecha": fecha_iso(texto(fecha.group(2))) if fecha else "",
            "foto": url_limpia(atributo(img.group(), "src") or "", LISTADO) if img else "",
            "pieFoto": texto(atributo(img.group(), "alt")) if img else "",
        }
        if noticia["titulo"] and noticia["enlace"] not in vistas:  # una vez cada noticia
            vistas.add(noticia["enlace"])
            noticias.append(noticia)
    return noticias


def cuerpo_noticia(pagina):
    """Lo que hay dentro de <div class="descripcion_noticia">, hasta su </div> (contando los
    <div> de dentro), y nunca la columna «Últimas noticias» que va detrás: sus titulares
    también van en <p> y uno acabaría como resumen de otra noticia."""
    m = re.search(r"<div\b[^>]*\bdescripcion_noticia\b[^>]*>", pagina, re.I)
    if not m:
        return ""
    resto = pagina[m.end():]
    lateral = resto.find("ultimasNoticias")
    if lateral >= 0:
        resto = resto[:lateral]
    nivel = 1
    for div in re.finditer(r"<(/?)div\b", resto, re.I):
        nivel += -1 if div.group(1) else 1
        if nivel == 0:
            return resto[:div.start()]
    return resto if lateral >= 0 else ""  # sin cierre ni columna: mejor sin resumen


def completar(noticia):
    """Resumen y foto mediana, de la página de la noticia."""
    pagina = pedir(noticia["enlace"])
    limpia = sin_comentarios(pagina)
    noticia["resumen"] = texto(meta(limpia, "description"))
    if not noticia["resumen"]:
        # Sin entradilla: el primer párrafo con texto del cuerpo de la noticia.
        parrafos = (texto(p) for p in re.findall(r"<p\b[^>]*>(.*?)</p>", cuerpo_noticia(limpia), re.S | re.I))
        noticia["resumen"] = next((p for p in parrafos if len(p) > 40), "")
    # La primera dirección de /imagenes_medianas/ de la página, comentarios incluidos: en noviembre
    # de 2026 la UPCT dejó comentada la etiqueta twitter:image que la llevaba (con la misma foto);
    # la foto principal de la noticia también la usa (con dirección relativa). Las demás noticias
    # de la página van con /imagenes/.
    mediana = re.search(r'["\']([^"\']*/imagenes_medianas/[^"\']+)["\']', pagina)
    if mediana:
        noticia["fotoMediana"] = url_limpia(mediana.group(1), noticia["enlace"])
    if not noticia["fecha"]:
        pub = re.search(r"Publicada el ([^<]+)<", limpia)
        noticia["fecha"] = fecha_iso(pub.group(1)) if pub else ""
    return noticia


def main():
    salida = sys.argv[1]
    try:
        with open(salida, encoding="utf-8") as f:
            anteriores = json.load(f).get("noticias", [])
    except FileNotFoundError:
        anteriores = []
    except (OSError, ValueError, AttributeError) as e:
        # Dañado: se rehace con el listado; las que ya habían salido de él siguen en el historial de git.
        avisar(f"No se ha podido leer {salida} ({e}): se rehace con las noticias del listado.")
        anteriores = []
    guardadas = {x["enlace"]: x for x in anteriores}

    listado = leer_listado()[:MAXIMO]
    if not listado:
        sys.exit("No se ha encontrado ninguna noticia en el listado: ¿ha cambiado la web de la UPCT?")

    noticias, pedidas, fallos = [], 0, 0
    for noticia in listado:
        guardada = guardadas.get(noticia["enlace"])
        if guardada and (not noticia["foto"] or noticia["foto"] == guardada.get("foto")):
            # Ya se tenía: no se pide su página otra vez, pero se le ponen los datos del listado.
            noticias.append(guardada | {k: v for k, v in noticia.items() if v})
            continue
        time.sleep(PAUSA)
        pedidas += 1
        try:
            noticias.append(completar(noticia))
        except Exception as e:  # una noticia que falla no para el resto (se reintenta en la próxima)
            fallos += 1
            avisar(f"{noticia['enlace']}: {e}")
            if guardada:  # había cambiado la foto: se queda como estaba
                noticias.append(guardada)

    if pedidas and fallos == pedidas:
        sys.exit(f"Han fallado las {fallos} páginas de noticia pedidas: ¿ha cambiado la web de la "
                 "UPCT o no deja leerla? No se tocan los datos.")

    # Detrás, las que ya se tenían y han salido del listado, hasta llegar a MAXIMO.
    en_listado = {n["enlace"] for n in listado}
    salidas = [n for n in anteriores if n["enlace"] not in en_listado]
    noticias += salidas[:max(0, MAXIMO - len(noticias))]

    if noticias == anteriores:
        print(f"Sin cambios ({len(noticias)} noticias).")
        return
    datos = {"fuente": LISTADO,
             "actualizado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "noticias": noticias}
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"{len(noticias)} noticias. Páginas de noticia leídas: {pedidas - fallos}; con error: {fallos}.")


if __name__ == "__main__":
    main()
