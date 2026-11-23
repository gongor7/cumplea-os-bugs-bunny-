# 🥕 Cómo poner los audios e imágenes oficiales (cuando los tengas)

La landing ya funciona con la voz sintética de fábrica. Para cambiarla por el
audio oficial de Bugs (México) o por canciones/imágenes de TVXQ **no hay que
tocar código**: solo copia tus archivos con estos nombres exactos.

## Audios → carpeta `assets/audio/`

| Archivo a crear              | Qué suena ahí por defecto                  | Qué poner tú |
|------------------------------|--------------------------------------------|--------------|
| `bugs-talk.mp3`              | Frases de Bugs (11 s)                      | Clips de la voz oficial: "¿Qué hay de nuevo, viejo?" etc. |
| `bugs-song.mp3`              | La canción de cumpleaños (18.5 s)          | El "Cumpleaños feliz" con la voz oficial |
| `drama-theme.mp3`            | Balada instrumental de fondo del dorama    | Tu canción de TVXQ (¡que sea un instrumental o volumen bajo para que no pelele con la carta!) |

- Copia tu archivo **encima** del que ya existe (mismo nombre).
- Los originales sintéticos quedan de respaldo en `assets/audio/assets-default/`
  por si quieres volver atrás.
- Formato: MP3. Si tienes WAV/OGG/M4A, conviértelo o renómbralo no — mejor
  conviértelo (por ejemplo con el ffmpeg que ya tienes, o con cualquier
  convertidor online).
- La boca de Bugs se mueve sola con el volumen: si el nuevo audio dura distinto,
  la boca usa un modo automático. Para sincronía perfecta se puede regenerar la
  envolvente (ver README avanzado), pero no es necesario.

## Imágenes → carpeta `assets/img/`

Si consigues una imagen oficial de Bugs o fotos de TVXQ y quieres que reemplace
los dibujos del dorama: guárdalas ahí y dime cuál va en qué postal — te las
conecto yo (eso sí es un cambio de una línea por postal).

## Textos → `content.js`

Todo lo editable vive en `content.js` (la carta, la firma, los créditos, las
letras). Ábrelo con el Bloc de notas, cambia lo que quieras y guarda.

## Subirla a Vercel 🚀

**Opción A — arrastrar (la más fácil):**
1. Entra a https://vercel.com/new (con cuenta gratuita, se puede entrar con GitHub).
2. Arrastra la carpeta completa `bugs bunny` a la página.
3. Le das un nombre bonito al proyecto (por ejemplo `paola-birthday`) y **Deploy**.
4. Te da un link `https://paola-birthday.vercel.app` → ese le mandas a Paola.

**Opción B — desde la terminal:**
```
cd "C:\Users\LEANDRO\Documents\Trabajo\Nueva carpeta\bugs bunny"
npx vercel
```
La primera vez te pide iniciar sesión; después acepta todo con Enter y al final
te imprime el link.

> Importante: el micrófono para soplar las velitas solo funciona con el link de
> Vercel (https), no abriendo el archivo con doble clic. Ahí cae al respaldo de
> tocar las llamas.

## Escuchar las muestras de voz 🎧

En `samples/` hay previews para que decidas si te gusta la voz por defecto:
- `voz-preview-frases.mp3` — las frases de Bugs
- `cancion-preview-A.mp3` — versión A de la canción (la activa)
- `cancion-preview-B.mp3` — versión B (contorno melódico)
