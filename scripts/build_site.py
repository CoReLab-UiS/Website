#!/usr/bin/env python3
"""Build the website into _site/ with an up-to-date publication list.

The publications come from the members' ORCID records (data/members.toml), from SINCE_YEAR
on, plus the additions and exclusions in data/publications.toml. Authors and journals are
looked up through doi.org. The lists are written into index.html (the latest few) and
publications.html (all of them) between their marker comments; every other file is copied
unchanged.

Needs Python 3.11 or newer and nothing else. From the repository root:

    python3 scripts/build_site.py
    python3 -m http.server 8000 --directory _site

GitHub runs this before every publish, see .github/workflows/pages.yml.
"""

import html
import json
import os
import re
import shutil
import sys
import time
import tomllib
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_site"
SINCE_YEAR = 2024    # earliest publication year taken from ORCID
LATEST_COUNT = 5     # publications shown on the main page
MAX_AUTHORS = 12     # longer author lists are cut to the first 10 + "et al."

SKIP_AT_ROOT = {".git", ".github", "_site", "data", "scripts"}  # not published
SKIP_ANYWHERE = {"__pycache__", ".DS_Store"}

USER_AGENT = "CoReLab-website/1.0 (+https://corelab-uis.github.io/Website/)"
CSL_JSON = "application/vnd.citationstyles.csl+json"
ORCID_RE = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")


class BuildError(Exception):
    pass


@dataclass
class Member:
    name: str
    orcid: str
    scholar: str = ""
    researchgate: str = ""


@dataclass
class Publication:
    title: str = ""
    year: int | None = None
    month: int | None = None
    day: int | None = None
    doi: str = ""
    url: str = ""
    authors: list[str] = field(default_factory=list)
    venue: str = ""      # journal or conference
    publisher: str = ""  # shown when there's no venue, e.g. for preprints
    volume: str = ""
    pages: str = ""
    manual: bool = False


def warn(message):
    # Shown as a warning annotation on the run's page on GitHub
    prefix = "::warning::" if os.environ.get("GITHUB_ACTIONS") else "Warning: "
    print(prefix + message, file=sys.stderr)


# ---------- Reading the data files ----------

def load_toml(name):
    path = ROOT / "data" / name
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise BuildError(f"data/{name} has a syntax error: {e}")


def clean_orcid(value):
    value = re.sub(r"^https?://(www\.)?orcid\.org/", "", str(value).strip())
    return value.upper()


def clean_doi(value):
    value = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", str(value).strip(), flags=re.I)
    return value.lower()


def load_members():
    members = []
    for i, entry in enumerate(load_toml("members.toml").get("member", []), 1):
        name = str(entry.get("name", "")).strip()
        orcid = clean_orcid(entry.get("orcid", ""))
        if not name:
            raise BuildError(f"data/members.toml: member {i} has no name")
        if orcid and not ORCID_RE.match(orcid):
            raise BuildError(f"data/members.toml: {entry.get('orcid')!r} for {name} is not an "
                             "ORCID iD (it should look like 0000-0002-1825-0097)")
        members.append(Member(name, orcid,
                              str(entry.get("scholar", "")).strip(),
                              str(entry.get("researchgate", "")).strip()))
    return members


def load_manual():
    data = load_toml("publications.toml")
    exclude = {clean_doi(doi) for doi in data.get("exclude", [])}
    publications = []
    for i, entry in enumerate(data.get("publication", []), 1):
        if entry.get("doi"):
            publications.append(Publication(doi=clean_doi(entry["doi"]), manual=True))
            continue
        title, year = str(entry.get("title", "")).strip(), entry.get("year")
        if not title or not isinstance(year, int):
            raise BuildError(f"data/publications.toml: publication {i} needs a doi, "
                             "or at least a title and a year")
        authors = entry.get("authors", [])
        if isinstance(authors, str):
            authors = authors.split(",")
        publications.append(Publication(
            title=title, year=year, month=entry.get("month"),
            authors=[a.strip() for a in authors if a.strip()],
            venue=str(entry.get("venue", "")).strip(),
            url=str(entry.get("url", "")).strip(), manual=True))
    return exclude, publications


# ---------- Fetching ----------

def fetch_json(url, accept="application/json", attempts=3):
    request = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": USER_AGENT})
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as e:
            # Client errors won't go away by retrying, except "too many requests"
            if e.code < 500 and e.code != 429 or attempt == attempts - 1:
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == attempts - 1:
                raise
        time.sleep(2 ** (attempt + 1))


def value(node):
    return node.get("value") if isinstance(node, dict) else None


def to_int(text):
    try:
        return int(text)
    except (TypeError, ValueError):
        return None


def first(node):
    if isinstance(node, list):
        return str(node[0]) if node else ""
    return str(node or "")


def find_doi(external_ids):
    for entry in (external_ids or {}).get("external-id") or []:
        if entry.get("external-id-type") == "doi" and entry.get("external-id-relationship", "self") == "self":
            return clean_doi(entry.get("external-id-value", ""))
    return ""


def orcid_publications(member):
    """The member's ORCID works from SINCE_YEAR on (or without a year)."""
    try:
        data = fetch_json(f"https://pub.orcid.org/v3.0/{member.orcid}/works")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise BuildError(f"ORCID iD {member.orcid} of {member.name} does not exist "
                             "(data/members.toml)")
        raise BuildError(f"Could not read the ORCID record of {member.name}: {e}")
    except (urllib.error.URLError, TimeoutError) as e:
        raise BuildError(f"Could not reach ORCID for {member.name}: {e}")

    publications = []
    for group in data.get("group") or []:
        versions = group.get("work-summary") or []
        if not versions:
            continue
        # A work can be listed by several sources; ORCID shows the one with the highest index
        work = max(versions, key=lambda w: to_int(w.get("display-index")) or 0)
        date = work.get("publication-date") or {}
        year = to_int(value(date.get("year")))
        if year is not None and year < SINCE_YEAR:
            continue
        publications.append(Publication(
            title=value((work.get("title") or {}).get("title")) or "",
            year=year,
            month=to_int(value(date.get("month"))),
            day=to_int(value(date.get("day"))),
            doi=find_doi(work.get("external-ids")) or find_doi(group.get("external-ids")),
            url=value(work.get("url")) or "",
            venue=value(work.get("journal-title")) or ""))
    return publications


def look_up_doi(publication):
    """Fill in title, authors and journal from the DOI's metadata (Crossref, DataCite, ...)."""
    url = "https://doi.org/" + urllib.parse.quote(publication.doi, safe="/:;()")
    try:
        csl = fetch_json(url, accept=CSL_JSON)
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        if publication.manual:
            raise BuildError(f"data/publications.toml: could not look up DOI {publication.doi} "
                             f"({e}). Check the DOI, or fill in the details by hand.")
        warn(f"Could not look up DOI {publication.doi} ({e}); using the ORCID data instead.")
        return

    publication.title = first(csl.get("title")) or publication.title
    authors = []
    for author in csl.get("author") or []:
        name = author.get("literal") or " ".join(
            part for part in (author.get("given"), author.get("family")) if part)
        if name.strip():
            authors.append(name.strip())
    publication.authors = authors or publication.authors
    publication.venue = first(csl.get("container-title")) or publication.venue
    publication.publisher = first(csl.get("publisher"))
    publication.volume = first(csl.get("volume"))
    publication.pages = first(csl.get("page")) or first(csl.get("article-number"))
    issued = ((csl.get("issued") or {}).get("date-parts") or [[]])[0] or []
    if issued and to_int(issued[0]):
        publication.year = to_int(issued[0])
        publication.month = to_int(issued[1]) if len(issued) > 1 else None
        publication.day = to_int(issued[2]) if len(issued) > 2 else None


# ---------- Combining ----------

def strip_accents(text):
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def title_key(title):
    return re.sub(r"[^a-z0-9]", "", strip_accents(title.lower()))


def collect(members, exclude, manual):
    with ThreadPoolExecutor(max_workers=8) as pool:
        per_member = list(pool.map(orcid_publications, [m for m in members if m.orcid]))

    # Papers by several members appear in several ORCID records; keep each once
    merged = {}
    for publication in [p for found in per_member for p in found] + manual:
        key = publication.doi or f"{title_key(publication.title)}:{publication.year}"
        if key in merged:
            merged[key].manual |= publication.manual
        else:
            merged[key] = publication
    publications = [p for p in merged.values() if not (p.doi and p.doi in exclude)]

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(look_up_doi, [p for p in publications if p.doi]))

    kept = []
    for p in publications:
        if not p.title or p.year is None:
            warn(f"Skipped {p.doi or p.title!r}: no {'title' if not p.title else 'year'}.")
        elif p.manual or p.year >= SINCE_YEAR:
            kept.append(p)
    kept.sort(key=lambda p: (-p.year, -(p.month or 0), -(p.day or 0), p.title.lower()))
    return kept


# ---------- HTML ----------

def rich(text):
    """Escape text, but keep the simple markup that titles often contain, e.g. CO<sub>2</sub>."""
    text = html.escape(" ".join(str(text).split()), quote=False)
    text = re.sub(r"&lt;(/?)(sub|sup|i|b|em|strong)&gt;", r"<\1\2>", text, flags=re.I)
    return re.sub(r"&lt;/?[a-zA-Z][\w:.-]*(\s[^&]*)?&gt;", "", text)  # drop other tags, e.g. <scp>


def family_variants(name):
    """Last name in the spellings it may appear in, e.g. jäger -> {jager, jaeger}."""
    family = name.split()[-1].lower()
    german = family.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    return {strip_accents(family), strip_accents(german)}


def is_member(author, members):
    parts = author.replace(",", " ").split()
    if not parts:
        return False
    initial = strip_accents(parts[0][0].lower())
    families = family_variants(author)
    return any(initial == strip_accents(m.name[0].lower()) and families & family_variants(m.name)
               for m in members)


def render_publication(p, members, indent):
    authors = p.authors if len(p.authors) <= MAX_AUTHORS else p.authors[:10]
    authors_html = ", ".join(
        f"<strong>{html.escape(a)}</strong>" if is_member(a, members) else html.escape(a)
        for a in authors)
    if len(authors) < len(p.authors):
        authors_html += ", et al."

    details = [html.escape(p.volume),
               html.escape(re.sub(r"(?<=\d)-(?=\d)", "–", p.pages))]
    venue = " ".join(part for part in (
        f"<em>{rich(p.venue)}</em>" if p.venue else html.escape(p.publisher),
        ", ".join(d for d in details if d)) if part)
    venue = f"{venue} ({p.year})" if venue else f"({p.year})"

    lines = [f'{indent}<li class="pub">',
             f'{indent}  <p class="pub-title">{rich(p.title)}</p>']
    if authors_html:
        lines.append(f'{indent}  <p class="pub-authors">{authors_html}</p>')
    lines.append(f'{indent}  <p class="pub-venue">{venue}</p>')
    if p.doi:
        href = "https://doi.org/" + urllib.parse.quote(p.doi, safe="/:;()")
        lines.append(f'{indent}  <a class="pub-link" href="{html.escape(href)}">DOI</a>')
    elif p.url:
        lines.append(f'{indent}  <a class="pub-link" href="{html.escape(p.url)}">Link</a>')
    lines.append(f"{indent}</li>")
    return "\n".join(lines)


def render_list(publications, members, indent):
    items = "\n".join(render_publication(p, members, indent + "  ") for p in publications)
    return f'{indent}<ol class="pub-list">\n{items}\n{indent}</ol>'


def render_latest(publications, members, indent):
    if not publications:
        return f'{indent}<p class="muted">No publications yet.</p>'
    return render_list(publications[:LATEST_COUNT], members, indent)


def render_all(publications, members, indent):
    blocks = []
    for year in sorted({p.year for p in publications}, reverse=True):
        blocks.append(f'{indent}<h3 class="pub-year">{year}</h3>\n'
                      + render_list([p for p in publications if p.year == year], members, indent))
    if not blocks:
        blocks.append(f'{indent}<p class="muted">No publications yet.</p>')
    today = datetime.now(timezone.utc)
    blocks.append(f'{indent}<p class="pub-updated">Updated {today.day} {today:%B %Y} '
                  "from the members' ORCID records.</p>")
    return "\n\n".join(blocks)


def render_profiles(members, indent):
    items = []
    for m in members:
        links = [(f"https://orcid.org/{m.orcid}" if m.orcid else "", "ORCID"),
                 (m.scholar, "Google Scholar"),
                 (m.researchgate, "ResearchGate")]
        links_html = "".join(f'\n{indent}      <a href="{html.escape(url)}" rel="noopener">{label}</a>'
                             for url, label in links if url)
        items.append(f'{indent}  <li class="profile">\n'
                     f'{indent}    <span class="profile-name">{html.escape(m.name)}</span>\n'
                     f'{indent}    <span class="profile-links">{links_html}\n'
                     f'{indent}    </span>\n'
                     f'{indent}  </li>')
    return f'{indent}<ul class="profile-list">\n' + "\n".join(items) + f'\n{indent}</ul>'


def fill(page, name, render):
    """Replace what's between <!-- name:start ... --> and <!-- name:end --> in a page of _site/."""
    path = OUT / page
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"<!-- {name}:start[^>]*-->[^\n]*\n.*?^([ \t]*)<!-- {name}:end -->",
                      text, re.S | re.M)
    if not match:
        raise BuildError(f"{page}: the marker comments for {name} are missing")
    start = text.index("-->", match.start()) + 3
    start = text.index("\n", start) + 1
    end = match.start(1)
    path.write_text(text[:start] + render(match.group(1)) + "\n" + text[end:], encoding="utf-8")


# ---------- Build ----------

def copy_site():
    def ignore(directory, names):
        skip = {n for n in names if n in SKIP_ANYWHERE}
        if Path(directory).resolve() == ROOT:
            skip |= {n for n in names if n in SKIP_AT_ROOT}
        return skip

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT, OUT, ignore=ignore)


def main():
    members = load_members()
    exclude, manual = load_manual()
    publications = collect(members, exclude, manual)

    copy_site()
    fill("index.html", "publications-latest", lambda i: render_latest(publications, members, i))
    fill("publications.html", "publications-all", lambda i: render_all(publications, members, i))
    fill("publications.html", "member-profiles", lambda i: render_profiles(members, i))

    added = sum(p.manual for p in publications)
    print(f"Built {OUT.relative_to(ROOT)}/ with {len(publications)} publications "
          f"({len(publications) - added} from ORCID since {SINCE_YEAR}, {added} added by hand).")


if __name__ == "__main__":
    try:
        main()
    except BuildError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
