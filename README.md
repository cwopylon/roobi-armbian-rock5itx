# Roobi OS custom source for Armbian on ROCK 5 ITX

This repository hosts a Roobi-compatible source catalog for Armbian images for the ROCK 5 ITX platform. It generates a catalog file plus one manifest per image, publishes them through GitHub Pages, and refreshes them automatically with GitHub Actions.

## Current status

> Disclaimer: This repository is maintained for personal use on a Radxa ROCK 5 ITX setup. It is intended as a practical, self-hosted reference for installing Armbian through Roobi and is not a production-grade support channel or a guaranteed long-term distribution platform.

The live catalog for this repository is available at:

```text
https://cwopylon.github.io/roobi-armbian-rock5itx/images/list.json
```

Use that URL as the custom source in Roobi.

## Repository layout

- `.github/workflows/update-images.yml` — refreshes the manifests on a schedule or manually
- `.github/workflows/deploy-pages.yml` — builds and publishes the GitHub Pages site from the repository root
- `scripts/generate.py` — generates the manifests and catalog JSON files
- `images/` — the generated Roobi image manifests and `list.json`
- `index.html` and `.nojekyll` — the GitHub Pages landing page and static-file support for the JSON catalog and manifests

## How it works

1. The update workflow checks the Armbian `.sha` files for each ROCK 5 ITX endpoint.
2. The generator writes one manifest per image and refreshes the shared catalog.
3. The deploy workflow publishes the repository contents to GitHub Pages.
4. Any updated artifacts are committed and pushed back to the repository.

## Local generation

Run the generator locally with:

```bash
python3 scripts/generate.py --skip-download
```

Use the full download path when you want the generator to download the image archives and compute MD5 values:

```bash
python3 scripts/generate.py
```

## GitHub Pages publishing

The repository is prepared to publish from the repository root through GitHub Actions.

Recommended GitHub Pages settings:

- Source: GitHub Actions
- Branch: `main` (for the repository content)

Once the workflow finishes, the catalog will be served at the URL above.

## Notes

- The manifest schema follows the Roobi expectations from the implementation plan.
- The workflow uses the Armbian endpoint names directly so the latest builds remain available without hand editing.
- The same UUIDs are reused for each image to keep Roobi's image tracking stable.
