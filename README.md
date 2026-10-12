# CoReLab website

The website of CoReLab, the Computational Research Laboratory at the University of Stavanger.

**Live site:** https://corelab-uis.github.io/Website/

It's a plain HTML and CSS site, published by GitHub Pages from the `main` branch. There's no build step: whatever is merged into `main` goes live about a minute later.

## Rules

- **Nobody pushes directly to `main`.** Every change goes through a pull request.
- **Every pull request needs an approval** from Jonas (@jonasjaeger-sci) or Enrico (@EnricoRiccardi) before it can be merged. GitHub asks them for a review automatically.
- **Changing a pull request after it was approved needs a new approval.**
- **One change per pull request**, for example "Add my photo" or "Add thesis topic X". Small pull requests get reviewed faster.
- **Everything in this repository is public.** Don't add private files, and shrink images before adding them (see [Images](#images)).

You need **Write** access to the repository to make changes. Ask Jonas if you don't have it yet.

## How to make a change

### Small changes in the browser

For a typo, your role or a short text, you don't need Git:

1. Open the file on GitHub, for example `index.html`, and click the pencil icon (**Edit this file**).
2. Make your change.
3. Click **Commit changes…**, write a short description, choose **Create a new branch for this commit and start a pull request**, and click **Propose changes**.
4. Click **Create pull request**.

To add a file, such as your photo, open the folder on GitHub and choose **Add file → Upload files**. Then continue as in step 3.

### Larger changes on your computer

Once, download the repository:

```sh
git clone git@github.com:CoReLab-UiS/Website.git
cd Website
```

If you haven't set up an SSH key with GitHub, use `https://github.com/CoReLab-UiS/Website.git` instead.

For each change:

```sh
git switch main
git pull                         # start from the latest version
git switch -c add-my-photo       # a new branch, named after the change

# ... edit files and preview them (see below) ...

git status                       # shows which files you changed
git add index.html Images/members/jane-doe.jpg
git commit -m "Add photo of Jane Doe"
git push -u origin add-my-photo
```

Then open the repository on GitHub. A banner offers **Compare & pull request**: click it, describe your change and click **Create pull request**. With the GitHub CLI, `gh pr create --fill` does the same from the terminal.

### After you open a pull request

- Jonas or Enrico review it. They either approve it or ask for changes in a comment.
- To make changes, edit the files on the same branch, then `git add`, `git commit` and `git push` again. The pull request updates itself.
- Once it's approved, the reviewer merges it, or you click **Merge pull request** yourself. The change is live about a minute later.
- Afterwards, click **Delete branch** on the pull request page and update your copy with `git switch main` and `git pull`.

## Preview locally

From the repository folder:

```sh
python3 -m http.server 8000
```

Then open http://localhost:8000. Stop the server with Ctrl+C.

## Common changes

Text in `[square brackets]` is placeholder text that still needs real content. Repeated items, such as cards, publications and news, are copies of each other: to add one, copy an existing one in `index.html` and change its content.

- **Your photo:** crop it square around your face, scale it to about 400 × 400 px and put it in `Images/members/`. In your member card in `index.html`, change the `src` of the image from `Images/members/placeholder.svg` to your file.
- **Publication:** copy a `<li class="pub">` in the Publications section, under the right year. Newest year first. Put the DOI address in the `href` of its DOI link.
- **News:** the News section is hidden for now. The comment above it in `index.html` explains how to show it again.
- **Research topic:** copy `research/topic-template.html` to a new file in `research/`, for example `research/my-topic.html`, and follow the instructions at the top of the file. Then copy a research card in `index.html` and link it to the new page.
- **Thesis topic:** write the flyer with the LaTeX template on Overleaf, as described in the [template's README](Documents/theses/template/README.md). Put the PDF in `Documents/theses/`, then copy a thesis card in `index.html` and link it to the PDF. When a topic is no longer available, remove its card and its PDF.

## Images

Large images slow the site down, and every file stays in the repository's history for good, even after it's deleted. Keep them small:

| Image | Size | File size |
|---|---|---|
| Member photo | 400 × 400 px, square | under 100 KB |
| Research card thumbnail | about 1200 × 675 px (16:9) | under 200 KB |
| Figure on a research page | about 1600 px wide | under 300 KB |

[Squoosh](https://squoosh.app) resizes and compresses images in the browser. Use JPEG or WebP for photos.

File names are case-sensitive on the live site, so `Photo.jpg` and `photo.jpg` are different files. Avoid spaces in file names; lowercase with hyphens is easiest.

## Where things are

| Path | Content |
|---|---|
| `index.html` | The main page with all sections |
| `research/` | One page per research topic, plus the template |
| `Documents/theses/` | Thesis topic PDFs and the LaTeX template |
| `Images/` | Member photos, research thumbnails and UiS logos |
| `Logos/` | CoReLab logos |
| `assets/css/style.css` | Layout and colors |
| `assets/js/main.js` | Mobile menu and small scripts |

The header and footer are copied into every page: `index.html` and each page in `research/`. If you change them, change them everywhere.

## Need help?

Ask Jonas or Enrico, or [open an issue](https://github.com/CoReLab-UiS/Website/issues) in this repository.
