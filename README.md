# Noticias de ciencia para pantallas

Página web que muestra, una a una, las últimas noticias de ciencia y tecnología de la
[Agencia SINC](https://www.agenciasinc.es), pensada para pantallas informativas con
[Anthias](https://github.com/Screenly/Anthias) (contenido de tipo web, a 1920×1080 o cualquier
resolución 16:9). La usa la ETSII de la Universidad Politécnica de Cartagena.

## Qué muestra
- Las **3 últimas noticias** de las secciones Ciencia, Tecnología, Innova y Tierra, **8 s cada
  una**, con un fundido y una barra de progreso.
- En cada noticia: la foto con su pie, la sección, la fecha, el titular, el resumen y un **QR**
  a la noticia completa, con la fuente, el autor y la licencia.
- Si el titular es largo, reduce la letra; si no cabe todo, acorta el resumen.
- Sin conexión, la última copia guardada en el navegador; si no hay ninguna, una pantalla neutra.

## Cómo funciona
- Lee el RSS `https://www.agenciasinc.es/feed/Noticias` desde el navegador: SINC permite leerlo
  desde otra web (`Access-Control-Allow-Origin: *`). No necesita servidor propio.
- Las fotos se piden en la versión reducida que usa la web de SINC (unos 1300 px), no la
  original (puede pesar varios MB).
- La letra (Inter) y el generador de QR van en `recursos/`: la pantalla solo necesita llegar a
  esta página y a `agenciasinc.es`.

## En Anthias
Contenido de tipo **web** con la dirección de esta página y una duración de **26 s**
(3 noticias × 8 s y un margen para la carga). Anthias vuelve a cargar la página cada vez que la
muestra, así que al acabar la tercera noticia se queda en ella.

## Parámetros (opcionales, en la dirección)
| Parámetro | Por defecto | Uso |
|---|---|---|
| `categorias` | `Ciencia,Tecnología,Innova,Tierra` | Secciones de SINC; `todas` para no filtrar |
| `n` | `3` | Noticias que se muestran (1 a 8) |
| `segundos` | `8` | Segundos por noticia |
| `bucle` | — | `1`: vuelve a empezar al acabar (para verla en un navegador) |
| `pausa`, `inicio` | — | `pausa=1` no pasa de noticia; `inicio=k` empieza en la k-ésima (para capturas) |

Ejemplo: `…/?categorias=Tecnología,Innova&n=4&segundos=7` (duración en Anthias: 30 s).

## Licencias
- **Noticias**: textos de la Agencia SINC (FECYT) con licencia
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es); en cada noticia se citan
  SINC y su autor. Las fotos llevan el crédito que indica SINC. Nada de esto se guarda en este
  repositorio: se lee en el momento.
- **Letra Inter**: SIL Open Font License 1.1 (`recursos/OFL-Inter.txt`).
- **qrcodejs** (davidshimjs): licencia MIT (`recursos/LICENSE-qrcodejs.txt`).
