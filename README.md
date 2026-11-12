# Coolest Art — make.fun coolest-art-01

A lone astronaut stands on a jagged alien ridge beneath a huge ringed amber
planet. Aurora curtains sweep behind it, amid a distant moon, scattered stars,
two shooting stars and diffuse nebula clouds. Planet light catches the ring,
ridge crest and suit; a cool visor and dark foreground keep the figure readable.
The image is drawn procedurally without external assets.

## How it works

- `draw.py` (Python 3 + Pillow) builds a pixel-level dusk gradient, then
  composites blurred nebula clouds, stars and aurora curtains. The planet uses
  radial lighting, warped sine bands, a small storm and separate ring passes.
- A fixed random seed controls all scattered details, and the rendering uses
  stable drawing and PNG encoding settings. Running `python3 draw.py` with
  the same Pillow version produces the same `entry.png` bytes each time.
- `main.ts` (Node 22, standard library only) copies `entry.png` to
  `$MAKEFUN_OUTPUT_DIR/entry.png`, after checking the PNG signature,
  1024×1024 dimensions and 1 MiB maximum size. If the variable is unset, the
  destination defaults to `/output/entry.png`.

## Determinism

draw.py uses a fixed seed, so each run writes byte-identical output with the same Pillow version.
main.ts only copies the file unchanged.

## Run it

```sh
python3 draw.py
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

Rendering is byte-for-byte deterministic with the same Python and Pillow
versions; the entrypoint copies the rendered image unchanged.

## License

MIT — see `LICENSE`.
