# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Website for **CoReLab (Computational Research Laboratory)**, a university research group. It's a static site written in plain HTML (with CSS and, if needed, minimal JavaScript), hosted and maintained on GitHub with GitHub Pages.

Live site: https://corelab-uis.github.io/Website/ (repo `CoReLab-UiS/Website`, published from the root of `main`). It's a project site, so links must be relative.

## Structure

- `index.html` is the main page, with anchored sections (`#research`, `#group`, `#publications`, `#theses`, `#contact`). The `#news` section and its nav links are commented out on every page for now; the comment above the section says how to restore it. The header nav and footer nav both link to these anchors. If you add, rename, or split out a section, update both navs on every page.
- `research/` holds one page per research topic, linked from the research cards. `research/topic-template.html` is the copy-me template (it has `noindex` and a how-to comment, which the real pages drop). These pages copy the header and footer of `index.html` with `../` paths and nav links to `../index.html#…`, and mark the Research nav link with `is-active`.
- `Documents/theses/` holds the thesis topic PDFs that the thesis cards link to. `Documents/theses/template/` is the LaTeX source for them (`main.tex` for content, `corelab-thesis.cls` for the shared layout, pdfLaTeX, meant for Overleaf). `thesis-topic-template.zip` is a zip of that folder for Overleaf upload, and `example-topic.pdf` is the template compiled with its placeholders. After changing the template, rebuild both.
- `assets/css/style.css` holds the color palette and spacing tokens on `:root`. Use those variables instead of hard-coded colors.
- `assets/js/main.js` handles the mobile menu toggle, highlights the active nav link (via IntersectionObserver on `main > section[id]`), and sets the footer year.
- `Logos/` contains the CoReLab logos. The site uses variant 1 (atom). `corelab_mark.svg` is the icon-only version, used for the favicon, header, and hero. `corelab_variant1_atom_cropped.svg` (empty margins removed, university line in sky blue) is the footer logo.
- The header logo is not an image of the full logo. It's `corelab_mark.svg` plus a divider and HTML text (wordmark, tagline, university line) styled to match it, because the full logo's small text becomes unreadable at header height. If you change the logo, keep the two in sync.
- `Images/` contains the UiS logos (opaque white background, so only place them on white or use `mix-blend-mode: multiply`). `UiS_Logo_mark.png` is a cropped copy of `UiS_Logo.png`, used at the right of the header. Member photos go in `Images/members/`, which has `placeholder.svg` as the default. They're shown as a 128 px circle, so crop them square around the face and scale to about 400 × 400 px (well under 100 KB). Research thumbnails (16:9) go in `Images/research/`, also with a `placeholder.svg`.

## Content conventions

- Placeholder text is wrapped in `[square brackets]`. Grep for `\[` to find what still needs real content.
- Each repeated item (research topic card, member card, publication, thesis card, news item) is a copy of its sibling markup. To add one, duplicate an existing item. Publications are grouped under year headings, and news is listed newest first.
- Research and thesis cards are clickable: the title is an `a.card-link` whose `::after` stretches over the whole card. A new research topic needs a card plus a page copied from `research/topic-template.html`. A new thesis topic needs a card plus a PDF in `Documents/theses/`.

## Colors

The palette is white plus two blues from the CoReLab logo: deep `#0062A3` and sky `#4A9AD4`. Headings use UiS navy `#004090`. The sky blue has only about 3:1 contrast on white, so use it for decoration only, never for text.

## Constraints

- **Static only.** GitHub Pages serves files as they are. There's no server-side code, database, or form handling. Anything dynamic has to run in the browser or use an external service.
- **No build step** unless one is deliberately added later. The files in the repo are the deployed site.
- **No templating.** Plain HTML has no includes, so shared parts like the header, navigation, and footer are copied into every page. When you change one, change it on every page and keep them in sync.

## Local development

You can preview the site with any static file server from the repo root, for example:

```sh
python3 -m http.server 8000
```

Then open http://localhost:8000. Prefer this over opening files with `file://`, because relative paths and `fetch` behave differently there than on GitHub Pages.

## GitHub Pages specifics

- Pages publishes from a chosen branch, either from the repo root or from `/docs`. This is set in the repo settings under **Settings → Pages**.
- By default Pages runs Jekyll, which ignores files and folders whose names start with `_`. Add an empty `.nojekyll` file at the publish root to serve the plain HTML untouched.
- Paths are case-sensitive on Pages even if they aren't locally. Make sure link and asset paths match file names exactly.
- If the site is a project site (`<user>.github.io/<repo>/`) rather than a user or org site or a custom domain, root-absolute links like `/css/style.css` will break. Use relative links.
- A `404.html` at the publish root becomes the site's custom 404 page.
- A custom domain is set with a `CNAME` file at the publish root plus DNS records.
