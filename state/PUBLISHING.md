# NORMAL POSITION — PUBLISHING

Status: ACTIVE.

## Source of truth

Manuscript chapters live at:

manuscript/<NNN>/current.md

First line:
# Chapter Title

Everything after first heading is chapter body.

## Build

scripts/build_site.py scans manuscript folders and generates:

- docs/manifest.json
- docs/chapters/<NNN>/index.html

The script uses only Python standard library.

## Deployment

GitHub Pages workflow:

1. checkout
2. run build script
3. configure Pages
4. upload docs
5. deploy

## Continue behavior

After a chapter passes audit:

1. create / update manuscript/<NNN>/current.md
2. update state files
3. commit main
4. workflow rebuilds reader automatically
5. verify workflow / deployment before claiming chapter is live

Do not hand-edit generated chapter HTML unless fixing the generator itself.

## Reader rules

- homepage reads manifest
- chapters link previous / next
- word counts generated automatically
- empty manuscript produces empty manifest safely
