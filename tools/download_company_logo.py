import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from PIL import Image


USER_AGENT = "FinancialsLogoDownloader/1.0"


def fetch_json(url):
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def download_bytes(url):
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        return response.read()


def commons_api(params):
    query = urlencode({"format": "json", "formatversion": "2", **params})
    return fetch_json(f"https://commons.wikimedia.org/w/api.php?{query}")


def search_commons(company, limit=12):
    data = commons_api(
        {
            "action": "query",
            "generator": "search",
            "gsrnamespace": "6",
            "gsrsearch": f'"{company}" logo',
            "gsrlimit": str(limit),
            "prop": "imageinfo",
            "iiprop": "url|mime",
            "iiurlwidth": "1600",
        }
    )
    return data.get("query", {}).get("pages", [])


def score_candidate(company, candidate):
    title = candidate.get("title", "").lower()
    imageinfo = (candidate.get("imageinfo") or [{}])[0]
    mime = imageinfo.get("mime", "")
    company_tokens = [token for token in re.split(r"[^a-z0-9]+", company.lower()) if token]
    normalized_company = " ".join(company_tokens)
    normalized_title = " ".join(token for token in re.split(r"[^a-z0-9]+", title) if token)
    score = 0
    if "logo" in title:
        score += 20
    if normalized_title.startswith(f"file {normalized_company} logo") or normalized_title.startswith(
        f"file {normalized_company} s logo"
    ):
        score += 30
    score += sum(6 for token in company_tokens if token in title)
    if mime == "image/png":
        score += 5
    elif mime == "image/svg+xml":
        score += 8
    if any(word in title for word in ("old", "former", "historical", "icon", "acquisition", "post")):
        score -= 15
    score -= min(len(title) // 20, 10)
    return score


def select_logo(company, candidates):
    usable = []
    for candidate in candidates:
        imageinfo = (candidate.get("imageinfo") or [{}])[0]
        if imageinfo.get("mime") not in {"image/png", "image/svg+xml"}:
            continue
        url = imageinfo.get("thumburl") or imageinfo.get("url")
        if url:
            usable.append((score_candidate(company, candidate), candidate, url))
    if not usable:
        raise ValueError(f"No PNG/SVG logo candidates found on Wikimedia Commons for {company}.")
    return max(usable, key=lambda item: item[0])


def corner_color(image):
    width, height = image.size
    corners = [
        image.getpixel((0, 0)),
        image.getpixel((width - 1, 0)),
        image.getpixel((0, height - 1)),
        image.getpixel((width - 1, height - 1)),
    ]
    return max(set(corners), key=corners.count)


def make_corner_background_transparent(image, tolerance=12):
    rgba = image.convert("RGBA")
    bg = corner_color(rgba)
    if bg[3] < 255:
        return rgba
    if not all(channel >= 240 for channel in bg[:3]):
        return rgba

    pixels = rgba.load()
    width, height = rgba.size
    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]
            if all(abs(pixel[i] - bg[i]) <= tolerance for i in range(3)):
                pixels[x, y] = (pixel[0], pixel[1], pixel[2], 0)
    return rgba


def normalize_to_transparent_png(raw_bytes, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_suffix(".download")
    temp_path.write_bytes(raw_bytes)
    try:
        with Image.open(temp_path) as source:
            normalized = make_corner_background_transparent(source)
            normalized.save(output_path, "PNG")
    finally:
        temp_path.unlink(missing_ok=True)
    return output_path


def download_company_logo(company, output_path):
    candidates = search_commons(company)
    _, candidate, image_url = select_logo(company, candidates)
    raw = download_bytes(image_url)
    logo_path = normalize_to_transparent_png(raw, output_path)
    return logo_path, candidate.get("title"), image_url


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("company", nargs="?")
    parser.add_argument("--output", required=True)
    parser.add_argument("--url", default=None)
    args = parser.parse_args()

    if args.url:
        logo_path = normalize_to_transparent_png(download_bytes(args.url), args.output)
        print(f"Logo: {logo_path}")
        print(f"Source URL: {args.url}")
        return
    if not args.company:
        raise SystemExit("Provide a company name or --url.")

    logo_path, title, image_url = download_company_logo(args.company, args.output)
    print(f"Company: {args.company}")
    print(f"Logo: {logo_path}")
    print(f"Source title: {title}")
    print(f"Source URL: {image_url}")


if __name__ == "__main__":
    main()
