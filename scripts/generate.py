#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
IMAGES_DIR = ROOT / "images"

CATALOG = [
    {
        "endpoint": "Trixie_vendor_minimal",
        "json_filename": "armbian_trixie_vendor_minimal.json",
        "display_name": "ROCK 5 ITX Armbian Trixie Minimal (Vendor)",
        "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567801",
        "base_url": "https://dl.armbian.com/rock-5-itx/",
    },
    {
        "endpoint": "Trixie_current_minimal",
        "json_filename": "armbian_trixie_current_minimal.json",
        "display_name": "ROCK 5 ITX Armbian Trixie Minimal (Current)",
        "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567802",
        "base_url": "https://dl.armbian.com/rock-5-itx/",
    },
    {
        "endpoint": "Resolute_vendor_minimal",
        "json_filename": "armbian_resolute_vendor_minimal.json",
        "display_name": "ROCK 5 ITX Armbian Resolute Minimal (Vendor)",
        "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567803",
        "base_url": "https://dl.armbian.com/rock-5-itx/",
    },
    {
        "endpoint": "Resolute_current_minimal",
        "json_filename": "armbian_resolute_current_minimal.json",
        "display_name": "ROCK 5 ITX Armbian Resolute Minimal (Current)",
        "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567804",
        "base_url": "https://dl.armbian.com/rock-5-itx/",
    },
    {
        "endpoint": "Resolute_vendor_gnome",
        "json_filename": "armbian_resolute_vendor_gnome.json",
        "display_name": "ROCK 5 ITX Armbian Resolute GNOME (Vendor)",
        "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567805",
        "base_url": "https://dl.armbian.com/rock-5-itx/",
    },
    {
        "endpoint": "Resolute_current_gnome",
        "json_filename": "armbian_resolute_current_gnome.json",
        "display_name": "ROCK 5 ITX Armbian Resolute GNOME (Current)",
        "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567806",
        "base_url": "https://dl.armbian.com/rock-5-itx/",
    },
    {
        "endpoint": "Resolute_vendor_kde-plasma",
        "json_filename": "armbian_resolute_vendor_kde.json",
        "display_name": "ROCK 5 ITX Armbian Resolute KDE Plasma (Vendor)",
        "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567807",
        "base_url": "https://dl.armbian.com/rock-5-itx/",
    },
    {
        "endpoint": "Resolute_current_kde-plasma",
        "json_filename": "armbian_resolute_current_kde.json",
        "display_name": "ROCK 5 ITX Armbian Resolute KDE Plasma (Current)",
        "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567808",
        "base_url": "https://dl.armbian.com/rock-5-itx/",
    },
    {
        "endpoint": "Sid_vendor_server-kali",
        "json_filename": "armbian_sid_vendor_kali.json",
        "display_name": "ROCK 5 ITX Armbian Kali Linux (Vendor)",
        "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567809",
        "base_url": "https://dl.armbian.com/rock-5-itx/",
    },
    {
        "endpoint": "Trixie_vendor_server-homeassistant",
        "json_filename": "armbian_trixie_vendor_homeassistant.json",
        "display_name": "ROCK 5 ITX Armbian Home Assistant (Vendor)",
        "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567810",
        "base_url": "https://dl.armbian.com/rock-5-itx/",
    },
    {
        "endpoint": "Trixie_vendor_minimal-omv",
        "json_filename": "armbian_trixie_vendor_omv.json",
        "display_name": "ROCK 5 ITX Armbian OpenMediaVault (Vendor)",
        "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567811",
        "base_url": "https://dl.armbian.com/rock-5-itx/",
    },
    {
        "endpoint": "Trixie_vendor_server-openhab",
        "json_filename": "armbian_trixie_vendor_openhab.json",
        "display_name": "ROCK 5 ITX Armbian openHAB (Vendor)",
        "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567812",
        "base_url": "https://dl.armbian.com/rock-5-itx/",
    },
    {
        "endpoint": "Forky_vendor_minimal",
        "json_filename": "armbian_forky_vendor_minimal.json",
        "display_name": "ROCK 5 ITX Armbian Forky Minimal (Nightly)",
        "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567813",
        "base_url": "https://dl.armbian.com/nightly/rock-5-itx/",
    },
    {
        "endpoint": "Resolute_vendor_gnome",
        "json_filename": "armbian_resolute_vendor_gnome_nightly.json",
        "display_name": "ROCK 5 ITX Armbian Resolute GNOME (Nightly)",
        "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567814",
        "base_url": "https://dl.armbian.com/nightly/rock-5-itx/",
    },
]


def fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "roobi-armbian-generator/1.0"})
    with urlopen(request, timeout=90) as response:
        return response.read().decode("utf-8", errors="replace")


def fetch_bytes(url: str, destination: Path) -> int:
    request = Request(url, headers={"User-Agent": "roobi-armbian-generator/1.0"})
    with urlopen(request, timeout=300) as response:
        content_length = response.headers.get("Content-Length")
        size = int(content_length) if content_length and content_length.isdigit() else 0
        with destination.open("wb") as handle:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)
        return size


def md5_file(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def estimate_uncompressed_size(display_name: str, compressed_size: int) -> int:
    lowered = display_name.lower()
    if "gnome" in lowered or "kde" in lowered or "desktop" in lowered:
        multiplier = 3
    elif "home assistant" in lowered or "openhab" in lowered or "omv" in lowered or "kali" in lowered:
        multiplier = 4
    else:
        multiplier = 4
    if compressed_size > 0:
        return max(1, compressed_size * multiplier)
    return 1_500_000_000


def build_description(display_name: str) -> dict:
    lowered = display_name.lower()
    if "minimal" in lowered:
        summary = "Lightweight, server-oriented image suited to headless deployments and custom setups."
    elif "gnome" in lowered:
        summary = "Desktop-oriented image with a full GNOME environment for everyday use."
    elif "kde" in lowered:
        summary = "Desktop-oriented image with the KDE Plasma environment for everyday use."
    elif "kali" in lowered:
        summary = "Security-focused Kali Linux image for penetration testing and specialist workflows."
    elif "home assistant" in lowered:
        summary = "Home Assistant image tailored for smart-home automation projects."
    elif "openmediavault" in lowered:
        summary = "OpenMediaVault image for NAS and storage-focused deployments."
    elif "openhab" in lowered:
        summary = "openHAB image for home automation and device control."
    elif "forky" in lowered or "nightly" in lowered:
        summary = "Rolling-release image for testing the latest Armbian developments."
    else:
        summary = "Armbian image packaged for the ROCK 5 ITX platform and made available through Roobi."

    title = display_name.replace("ROCK 5 ITX ", "").replace("Armbian ", "")
    return {
        "zh-CN": f"{title}，由 Armbian 社区维护并为 ROCK 5 ITX 打包，适用于 Roobi 自定义源安装。\n{summary}",
        "en": f"{title} is an Armbian image maintained for the ROCK 5 ITX platform and packaged for Roobi.\n{summary}",
    }


def get_pages_base_url() -> str:
    value = os.environ.get("GITHUB_PAGES_BASE_URL")
    if value:
        return value.rstrip("/")

    repository = os.environ.get("GITHUB_REPOSITORY")
    if repository and "/" in repository:
        owner, repo_name = repository.split("/", 1)
        return f"https://{owner}.github.io/{repo_name}/images"

    remote_url = os.environ.get("GITHUB_REMOTE_URL")
    if remote_url:
        remote_url = remote_url.rstrip("/")
        if remote_url.endswith(".git"):
            remote_url = remote_url[:-4]
        if remote_url.startswith("https://github.com/"):
            owner_repo = remote_url[len("https://github.com/"):]
            owner, repo_name = owner_repo.split("/", 1)
            return f"https://{owner}.github.io/{repo_name}/images"

    return "https://example.github.io/roobi-armbian-rock5itx/images"


def parse_sha_line(line: str) -> tuple[str, str]:
    if not line.strip():
        raise ValueError("empty .sha line")
    parts = line.strip().split()
    if len(parts) < 2:
        raise ValueError(f"unexpected .sha line: {line}")
    return parts[0], parts[-1]


def generate_image(entry: dict, skip_download: bool, force: bool) -> bool:
    image_path = IMAGES_DIR / entry["json_filename"]
    sha_url = f"{entry['base_url']}{entry['endpoint']}.sha"
    download_url = f"{entry['base_url']}{entry['endpoint']}"

    print(f"Processing {entry['display_name']} -> {sha_url}")

    filename = f"{entry['endpoint']}.img.xz"
    version = "unavailable"
    compressed_size = 0
    md5_value = ""
    uncompressed_size = estimate_uncompressed_size(entry["display_name"], 0)

    try:
        sha_content = fetch_text(sha_url)
        sha_value, filename = parse_sha_line(sha_content.splitlines()[0])
        version = filename[:-7] if filename.endswith(".img.xz") else filename
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        print(f"  Unable to fetch .sha metadata from {sha_url}: {exc}")

    if image_path.exists() and not force and version != "unavailable":
        try:
            current = json.loads(image_path.read_text(encoding="utf-8"))
            if current.get("version") == version and current.get("name") == entry["display_name"]:
                print(f"  Skipping {entry['json_filename']} because the version and name are unchanged")
                return False
        except json.JSONDecodeError:
            pass

    if version != "unavailable" and not skip_download:
        with tempfile.TemporaryDirectory(prefix="armbian-", dir=str(ROOT)) as tmp_dir:
            tmp_path = Path(tmp_dir) / filename
            try:
                compressed_size = fetch_bytes(download_url, tmp_path)
                md5_value = md5_file(tmp_path)
                uncompressed_size = estimate_uncompressed_size(entry["display_name"], compressed_size)
                print(f"  Downloaded {filename} ({compressed_size} bytes, md5={md5_value})")
            except (HTTPError, URLError, TimeoutError) as exc:
                print(f"  Download failed for {download_url}: {exc}; falling back to metadata-only output")

    record = {
        "script_version": "1",
        "uuid": entry["uuid"],
        "name": entry["display_name"],
        "img": "https://roobi.radxa.com/pic/armbian.svg",
        "description": build_description(entry["display_name"]),
        "version": version,
        "author": "Armbian",
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "download": [{
            "file_name": filename,
            "size": compressed_size,
            "urls": [download_url],
            "md5": md5_value,
        }],
        "scripts": [{"type": "auto", "text": "start", "size": uncompressed_size}],
    }

    image_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return True


def write_list(entries: list[dict]) -> None:
    base_url = get_pages_base_url()
    catalog = []
    for entry in entries:
        catalog.append({
            "uuid": entry["uuid"],
            "name": entry["display_name"],
            "url": f"{base_url}/{entry['json_filename']}",
        })
    (IMAGES_DIR / "list.json").write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Roobi-compatible Armbian manifests")
    parser.add_argument("--skip-download", action="store_true", help="Skip downloading image files")
    parser.add_argument("--force", action="store_true", help="Overwrite existing JSON files")
    args = parser.parse_args()

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("GITHUB_REMOTE_URL", "https://github.com/cwopylon/roobi-armbian-rock5itx.git")
    for entry in CATALOG:
        generate_image(entry, skip_download=args.skip_download, force=args.force)
    write_list(CATALOG)
    print(f"Wrote {len(CATALOG)} manifests to {IMAGES_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
