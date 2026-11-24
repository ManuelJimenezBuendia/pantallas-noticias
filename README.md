# Noticias para pantallas

Página web que muestra, una a una, las últimas noticias de ciencia y tecnología de la
[Agencia SINC](https://www.agenciasinc.es) o las de la
[Universidad Politécnica de Cartagena](https://www.upct.es/destacados/noticias.php), pensada
para pantallas informativas con [Anthias](https://github.com/Screenly/Anthias) (contenido de
tipo web, a 1920×1080 o cualquier resolución 16:9). La usa la ETSII de la UPCT.

## Qué muestra
- **SINC** (por defecto): las **20 últimas noticias** de todas las secciones, **12 s cada una**
  (4 minutos).
- **UPCT** (`?fuente=upct`): también las **20 últimas noticias**, **12 s cada una**.
- **Diseño** según el Manual de Identidad Corporativa de la UPCT (2026),
  «Sistema visual» (pp. 61-64): una retícula de 3 columnas y 5 filas en la que la foto, el
  texto y manchas de color (el del centro, blanco y negro) ocupan módulos enteros. Por defecto,
  la foto entera (3:2, sin recortar) en 2 × 4 módulos, con el titular en una columna del color
  del centro; con `?diseno=foto`, la foto a sangre y el titular en un bloque abajo. Titular,
  fechas y avisos en **Funnel Sans** Medium (la letra de la UPCT para comunicación); el texto
  corrido en Inter (el manual pide Helvetica Now Text, que es de pago).
- **Pantalla vertical** (`?vertical=1`), con las dos fuentes: retícula de 5 × 3, con la foto
  arriba, el titular en medio y el resto abajo. Si la Raspberry gira la imagen, la página lo
  detecta sola; si solo se ha girado el monitor, la página se gira ella misma.
- En cada noticia: el **logo del centro** sobre negro (por defecto, la ETSII; cualquier otro
  centro de la UPCT con `?escuela=`, que cambia también el color), la foto, la fecha, el
  titular, el resumen y un **QR** a la noticia completa, con la fuente. En SINC, además, la
  sección, el pie de foto, el autor y la licencia.
- Un fundido entre noticias, una barra de progreso y un contador («4 / 25»). Todo se puede
  cambiar con los parámetros de la dirección (ver más abajo).
- Si el titular es largo, reduce la letra; si no cabe todo, acorta el resumen.
- Sin conexión, la última copia guardada en el navegador; si no hay ninguna, una pantalla neutra
  con el logo.

## Cómo funciona
- **SINC**: la página lee el RSS `https://www.agenciasinc.es/feed/Noticias` desde el navegador:
  SINC permite leerlo desde otra web (`Access-Control-Allow-Origin: *`). Las fotos se piden en
  la versión reducida que usa la web de SINC (unos 1300 px).
- **UPCT**: la web de la UPCT no tiene RSS ni deja leerla desde otra web. Una **tarea
  programada de GitHub** ([`.github/workflows/upct.yml`](.github/workflows/upct.yml)) ejecuta
  [`scripts/upct.py`](scripts/upct.py) cada hora, de 7 a 21 h: lee el listado de noticias de
  actualidad y, de cada noticia nueva, su resumen y su foto mediana (1200×800). En
  [`datos/upct.json`](datos/upct.json), que es lo que lee la página, guarda las 20 más recientes:
  las del listado (unas 13) y, detrás, las que ya tenía y han salido de él. Solo hace un commit cuando
  hay noticias nuevas. Si no encuentra ninguna (por ejemplo, porque la UPCT ha cambiado su web),
  no toca los datos y la tarea falla: GitHub avisa por correo. Se puede lanzar a mano en la
  pestaña **Actions** del repositorio («Noticias de la UPCT» → «Run workflow»).
- Las letras (Funnel Sans e Inter), el generador de QR y los logos van en `recursos/`: la
  pantalla solo necesita llegar a esta página, a `agenciasinc.es` y a `www.upct.es` (fotos).
- Para probarla en un ordenador: SINC, abriendo `index.html` como fichero (`file:///…`), porque
  SINC responde a `localhost` y `127.0.0.1` con una cabecera CORS doble que el navegador rechaza
  (desde GitHub Pages no pasa); la UPCT, con un servidor local (`python -m http.server`), porque
  como fichero el navegador no deja leer `datos/upct.json`.

## En Anthias
Contenido de tipo **web**, con una duración de **245 s** con las dos fuentes (20 noticias ×
12 s y 5 s para la carga). Las noticias de SINC:

```
https://manueljimenezbuendia.github.io/pantallas-noticias/
```

Las noticias de la UPCT:

```
https://manueljimenezbuendia.github.io/pantallas-noticias/?fuente=upct
```

Los parámetros (ver más abajo) se añaden al final de la dirección, después de `?` y separados
por `&`. Entonces la duración en Anthias es la que se ponga en `duracion` (o n × segundos más
unos segundos, si se usa `n`). Por ejemplo, la versión corta de SINC para probarla (3 noticias
de 8 s; **26 s** en Anthias):

```
https://manueljimenezbuendia.github.io/pantallas-noticias/?categorias=ciencia,tecnologia,innova,tierra&n=3&segundos=8
```

En una **pantalla vertical** se añade `vertical=1`, con la misma duración (si el texto sale boca
abajo, `vertical=izquierda`):

```
https://manueljimenezbuendia.github.io/pantallas-noticias/?vertical=1
https://manueljimenezbuendia.github.io/pantallas-noticias/?fuente=upct&vertical=1
```

Anthias vuelve a cargar la página cada vez que la muestra.

## Parámetros (opcionales, en la dirección)
| Parámetro | Por defecto | Uso |
|---|---|---|
| `fuente` | SINC | `upct`: noticias de la UPCT |
| `diseno` | `mitad` | `foto`: foto a sangre (a pantalla completa), con el titular en un bloque de 2 × 2 módulos abajo; `mitad`: foto entera, sin recortar, junto a la columna del titular |
| `categorias` | todas | Solo SINC. Secciones separadas por comas: `Ciencia`, `Tecnología`, `Innova`, `Tierra`, `Salud`, `Sociedad` (da igual con o sin tildes y mayúsculas); `todas` para no filtrar |
| `segundos` | `12` | Segundos por noticia (mínimo 4) |
| `duracion` | `245` (20 noticias) | Duración total en segundos, **la misma que se pone en Anthias**: la página calcula cuántas noticias caben, dejando 5 s para la carga; si no hay bastantes, vuelve a empezar. Manda sobre `n` |
| `n` | — | En vez de la duración, el número de noticias (1 a 60); al acabar se queda en la última |
| `bucle` | — | `1`: vuelve a empezar al acabar (para verla en un navegador) |
| `vertical` | según la ventana | `1`: pantalla vertical (retícula de 5 × 3: foto arriba, titular en medio y el resto abajo; con las dos fuentes; no admite `diseno=foto`). Si la ventana ya es vertical, se usa sola, sin el parámetro. Si es horizontal (solo se ha girado el monitor), la página se gira 90° a la derecha; `izquierda`, hacia el otro lado (si el texto sale boca abajo); `0`, siempre horizontal |
| `escuela` | `etsii` | Logo y color del centro (los del manual de identidad). Siglas o un nombre corto (da igual con o sin tildes y mayúsculas): `etsii` o `industriales`; `etsit` o `teleco`; `etsia` o `agronomos`; `etsae` o `arquitectura`; `etsino` o `naval`; `eicm` o `caminos`; `fce` o `empresa`; `cud` o `defensa`; `doctorado`; `formacion`. Si no se reconoce, la ETSII |
| `pausa`, `inicio` | — | `pausa=1` no pasa de noticia; `inicio=k` empieza en la k-ésima (para capturas) |

Con más de 8 noticias, la barra de progreso es solo la de la noticia actual, con un contador
(«4 / 25»). Con `duracion`, si hay menos noticias de las que caben (o caben más de 60), se
muestran las que haya y se **vuelve a empezar desde la primera** hasta que Anthias pase al
siguiente contenido. Con `n`, al acabar se queda en la última. El RSS de SINC trae las 150
últimas noticias (unas seis semanas); Tierra y Salud son las secciones con más, y Tecnología e
Innova publican muy pocas: filtrando solo esas, salen pocas noticias y algunas de hace semanas.
De la UPCT se guardan las 20 más recientes: las del listado de actualidad (unas 13, de unos
cuatro días) y las anteriores que ya tenía la tarea. Si hay menos de 20, la página vuelve a
empezar para llenar la duración.

Ejemplos:
| Dirección | Noticias | Duración en Anthias |
|---|---|---|
| `…/` | 20 de SINC, de todas las secciones, 12 s | **245 s** |
| `…/?fuente=upct` | 20 de la UPCT, 12 s | **245 s** |
| `…/?duracion=305` | 25 de SINC, de todas las secciones, 12 s | 305 s (5 min) |
| `…/?duracion=125` | 10 de SINC, de todas las secciones, 12 s | 125 s |
| `…/?categorias=ciencia,tierra&segundos=10&duracion=125` | 12 de Ciencia y Tierra, 10 s | 125 s |
| `…/?categorias=ciencia,tecnologia,innova,tierra&n=3&segundos=8` | 3 de Ciencia, Tecnología, Innova y Tierra, 8 s | 26 s |

Las fotos se cargan de una en una (la actual y la siguiente), así que una serie larga no
satura la Raspberry.

## Licencias
- **Noticias de SINC**: textos de la Agencia SINC (FECYT) con licencia
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es); en cada noticia se citan
  SINC y su autor. Las fotos llevan el crédito que indica SINC. Nada de esto se guarda en este
  repositorio: se lee en el momento.
- **Noticias de la UPCT**: textos y fotos de la Universidad Politécnica de Cartagena, de su web.
  En `datos/upct.json` se guardan solo el titular, la fecha, el resumen, el pie de foto y los
  enlaces; las fotos se leen de `www.upct.es`.
- **Logos** (`recursos/logos/`): de la Universidad Politécnica de Cartagena y sus centros, de su
  identidad corporativa (versión para fondo negro, sin el fondo y recortada); no están bajo
  ninguna licencia libre.
- **Letra Inter**: SIL Open Font License 1.1 (`recursos/OFL-Inter.txt`).
- **Letra Funnel Sans** (The Funnel Project Authors, de Google Fonts): SIL Open Font License 1.1
  (`recursos/OFL-FunnelSans.txt`).
- **qrcodejs** (davidshimjs): licencia MIT (`recursos/LICENSE-qrcodejs.txt`).
