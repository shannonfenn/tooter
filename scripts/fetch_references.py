from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def clean_filename(filename: str) -> str:
    marker = "_MIT18_703S13_"
    if marker in filename:
        return "MIT18_703S13_" + filename.split(marker, maxsplit=1)[1]
    return filename


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self.links.append(href)


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 0:
        print(f"exists {destination.relative_to(ROOT)}", flush=True)
        return
    request = Request(url, headers={"User-Agent": "learning-aata-resource-fetcher/0.1"})
    with urlopen(request, timeout=60) as response:
        destination.write_bytes(response.read())
    print(f"downloaded {url} -> {destination.relative_to(ROOT)}", flush=True)


def fetch_linked_files(base_url: str, destination: Path, *, pdf_only: bool = False) -> None:
    html_path = destination / "index.html"
    download(base_url, html_path)
    parser = LinkParser()
    parser.feed(html_path.read_text(encoding="utf-8", errors="ignore"))

    base = urlparse(base_url)
    base_dir = base.path if base.path.endswith("/") else str(Path(base.path).parent) + "/"

    for href in sorted(set(parser.links)):
        absolute = urljoin(base_url, href)
        parsed = urlparse(absolute)
        if parsed.scheme not in {"http", "https"}:
            continue
        if parsed.netloc != base.netloc:
            continue
        if not parsed.path.startswith(base_dir) and "ocw.mit.edu" not in parsed.netloc:
            continue

        suffix = Path(parsed.path).suffix.lower()
        if pdf_only and suffix != ".pdf":
            continue
        if not pdf_only and suffix not in {".pdf", ".tex", ".html"}:
            continue

        filename = unquote(Path(parsed.path).name)
        if not filename:
            continue
        download(absolute, destination / clean_filename(filename))


def fetch_mit_resource_pdfs(index_url: str, destination: Path) -> None:
    index_path = destination / "index.html"
    download(index_url, index_path)
    parser = LinkParser()
    parser.feed(index_path.read_text(encoding="utf-8", errors="ignore"))

    resource_urls = sorted(
        {
            urljoin(index_url, href)
            for href in parser.links
            if "/courses/18-703-modern-algebra-spring-2013/resources/" in href
        }
    )

    for resource_url in resource_urls:
        resource_request = Request(
            resource_url, headers={"User-Agent": "learning-aata-resource-fetcher/0.1"}
        )
        with urlopen(resource_request, timeout=60) as response:
            resource_html = response.read().decode("utf-8", errors="ignore")

        resource_parser = LinkParser()
        resource_parser.feed(resource_html)
        for href in resource_parser.links:
            absolute = urljoin(resource_url, href)
            parsed = urlparse(absolute)
            if parsed.netloc not in {"ocw.mit.edu", "www.ocw.mit.edu"}:
                continue
            if Path(parsed.path).suffix.lower() != ".pdf":
                continue
            filename = clean_filename(unquote(Path(parsed.path).name))
            download(absolute, destination / filename)
            break


def main() -> None:
    download(
        "https://twjudson.github.io/aata-files/aata-20210809.pdf",
        ROOT / "references/aata/pdfs/aata-2021.pdf",
    )
    download(
        "https://twjudson.github.io/aata-files/aata-20250801.pdf",
        ROOT / "references/aata/pdfs/aata-2025.pdf",
    )

    fetch_linked_files(
        "https://math.mit.edu/~roed/courses/430/",
        ROOT / "references/courses/pitt-math0430/fall-2017",
    )
    fetch_linked_files(
        "https://math.mit.edu/~roed/courses/430_S16/",
        ROOT / "references/courses/pitt-math0430/spring-2016",
    )

    fetch_mit_resource_pdfs(
        "https://www.ocw.mit.edu/courses/18-703-modern-algebra-spring-2013/pages/lecture-notes/",
        ROOT / "references/courses/mit-18.703/lecture-notes",
    )
    fetch_mit_resource_pdfs(
        "https://www.ocw.mit.edu/courses/18-703-modern-algebra-spring-2013/pages/assignments/",
        ROOT / "references/courses/mit-18.703/assignments",
    )
    fetch_mit_resource_pdfs(
        "https://www.ocw.mit.edu/courses/18-703-modern-algebra-spring-2013/pages/exams/",
        ROOT / "references/courses/mit-18.703/exams",
    )


if __name__ == "__main__":
    main()
