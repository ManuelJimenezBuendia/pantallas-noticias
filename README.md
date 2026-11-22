# Noticias de ciencia para pantallas

Página web que muestra, una a una, las últimas noticias de ciencia y tecnología de la
[Agencia SINC](https://www.agenciasinc.es), pensada para pantallas informativas con
[Anthias](https://github.com/Screenly/Anthias) (contenido de tipo web, a 1920×1080 o cualquier
resolución 16:9). La usa la ETSII de la Universidad Politécnica de Cartagena.

## Qué muestra
- Por defecto, las **25 últimas noticias** de todas las secciones, **12 s cada una** (5 minutos),
  con un fundido, una barra de progreso y un contador («4 / 25»). Se puede cambiar con los
  parámetros de la dirección (ver más abajo).
- En cada noticia: el **logo de la UPCT · ETSII** (arriba a la derecha), la foto con su pie, la
  sección, la fecha, el titular, el resumen y un **QR** a la noticia completa, con la fuente, el
  autor y la licencia.
- Si el titular es largo, reduce la letra; si no cabe todo, acorta el resumen.
- Sin conexión, la última copia guardada en el navegador; si no hay ninguna, una pantalla neutra
  con el logo.

## Cómo funciona
- Lee el RSS `https://www.agenciasinc.es/feed/Noticias` desde el navegador: SINC permite leerlo
  desde otra web (`Access-Control-Allow-Origin: *`). No necesita servidor propio.
- Las fotos se piden en la versión reducida que usa la web de SINC (unos 1300 px), no la
  original (puede pesar varios MB).
- La letra (Inter), el generador de QR y el logo van en `recursos/`: la pantalla solo necesita
  llegar a esta página y a `agenciasinc.es`.
- Para probarla en un ordenador, abrir `index.html` como fichero (`file:///…`), no con un
  servidor local: SINC responde a `localhost` y `127.0.0.1` con una cabecera CORS doble que el
  navegador rechaza (y sale la pantalla neutra). Desde GitHub Pages no pasa.

## En Anthias
Contenido de tipo **web** con la dirección de esta página y una duración de **305 s** (25
noticias × 12 s y 5 s para la carga). Si se cambian los parámetros, la duración en Anthias es la
que se ponga en `duracion` (o n × segundos más unos segundos, si se usa `n`). Anthias vuelve a
cargar la página cada vez que la muestra.

## Parámetros (opcionales, en la dirección)
| Parámetro | Por defecto | Uso |
|---|---|---|
| `categorias` | todas | Secciones separadas por comas: `Ciencia`, `Tecnología`, `Innova`, `Tierra`, `Salud`, `Sociedad` (da igual con o sin tildes y mayúsculas); `todas` para no filtrar |
| `segundos` | `12` | Segundos por noticia (mínimo 4) |
| `duracion` | `305` | Duración total en segundos, **la misma que se pone en Anthias**: la página calcula cuántas noticias caben, dejando 5 s para la carga; si no hay bastantes, vuelve a empezar. Manda sobre `n` |
| `n` | — | En vez de la duración, el número de noticias (1 a 60); al acabar se queda en la última |
| `bucle` | — | `1`: vuelve a empezar al acabar (para verla en un navegador) |
| `pausa`, `inicio` | — | `pausa=1` no pasa de noticia; `inicio=k` empieza en la k-ésima (para capturas) |

Con más de 8 noticias, la barra de progreso es solo la de la noticia actual, con un contador
(«4 / 25»). Con `duracion`, si en las secciones elegidas hay menos noticias de las que caben (o
caben más de 60), se muestran las que haya y se **vuelve a empezar desde la primera** hasta que
Anthias pase al siguiente contenido. Con `n`, al acabar se queda en la última. El RSS
trae las 150 últimas noticias (unas seis semanas); Tierra y Salud son las secciones con más, y
Tecnología e Innova publican muy pocas: filtrando solo esas, salen pocas noticias y algunas de
hace semanas.

Ejemplos:
| Dirección | Noticias | Duración en Anthias |
|---|---|---|
| `…/` | 25 de todas las secciones, 12 s | **305 s** (5 min) |
| `…/?duracion=125` | 10 de todas las secciones, 12 s | 125 s |
| `…/?categorias=ciencia,tierra&segundos=10&duracion=125` | 12 de Ciencia y Tierra, 10 s | 125 s |
| `…/?categorias=ciencia,tecnologia,innova,tierra&n=3&segundos=8` | 3 de Ciencia, Tecnología, Innova y Tierra, 8 s | 26 s |

Las fotos se cargan de una en una (la actual y la siguiente), así que una serie larga no
satura la Raspberry.

## Licencias
- **Noticias**: textos de la Agencia SINC (FECYT) con licencia
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es); en cada noticia se citan
  SINC y su autor. Las fotos llevan el crédito que indica SINC. Nada de esto se guarda en este
  repositorio: se lee en el momento.
- **Logo** (`recursos/logo-upct-etsii.svg`): de la Universidad Politécnica de Cartagena y su
  Escuela Técnica Superior de Ingeniería Industrial; no está bajo ninguna licencia libre.
- **Letra Inter**: SIL Open Font License 1.1 (`recursos/OFL-Inter.txt`).
- **qrcodejs** (davidshimjs): licencia MIT (`recursos/LICENSE-qrcodejs.txt`).
