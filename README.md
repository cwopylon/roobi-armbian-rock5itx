# Roobi OS custom source for Armbian on ROCK 5 ITX

This repository hosts a Roobi-compatible source catalog for Armbian images for the ROCK 5 ITX platform. The workflow and generator in this repo produce the two-tier JSON structure described in the implementation plan:

- a catalog file in `images/list.json`
- one manifest per image under `images/`

The manifest names and descriptions are intentionally polished so they appear clearly in Roobi as ROCK 5 ITX-specific options.

## Repository layout

- `.github/workflows/update-images.yml` — scheduled and manual refresh workflow
- `scripts/generate.py` — generator for the manifests and catalog
- `images/` — generated JSON artifacts for Roobi

## How it works

1. The workflow runs daily and can also be triggered manually.
2. The generator polls the Armbian `.sha` files for each ROCK 5 ITX endpoint.
3. It writes a per-image JSON manifest and refreshes the shared catalog.
4. Any changed artifacts are committed and pushed back to the repository.

## Local generation

Run the generator locally with:

```bash
python3 scripts/generate.py --skip-download
```

Use the full download path for production refreshes:

```bash
python3 scripts/generate.py
```

## GitHub Pages publishing

The repository is prepared for a first GitHub Pages publish from the repository root:

- a root `index.html` landing page is included for the published site
- a `.nojekyll` file is included so static JSON content is served without Jekyll processing
- the generated catalog is available at `images/list.json`

After Pages is enabled in GitHub, use these settings:

- Source: Deploy from a branch
- Branch: `main`
- Folder: `/ (root)`

Once the site is live, the public catalog URL will be:

```text
https://<your-username>.github.io/roobi-armbian-rock5itx/images/list.json
```

Add that exact URL as a custom source in Roobi.

```text
https://<your-username>.github.io/roobi-armbian-rock5itx/images/list.json
```

## Notes

- The manifest schema follows the Roobi expectations from the provided implementation plan.
- The workflow uses the Armbian endpoint names directly so the latest builds remain available without hand editing.
- The same UUIDs are reused for each image to keep Roobi's image tracking stable.
