# Thesis topic template

LaTeX template for the one-page thesis topic flyers. Each card in the **Thesis topics** section of the website links to one of these PDFs.

## Write a topic on Overleaf

1. Download `thesis-topic-template.zip` from `Documents/theses/`.
2. On Overleaf, choose **New Project → Upload Project** and select the zip.
3. Check that the compiler is **pdfLaTeX** (**Menu → Compiler**).
4. Edit `main.tex`: fill in the fields and replace the text in `[square brackets]`. Keep it to one page.

## Publish a topic on the website

1. Download the PDF from Overleaf. Name it after the topic, in lowercase with hyphens, e.g. `co2-adsorption-mofs.pdf`.
2. Put it in `Documents/theses/`.
3. In `index.html`, duplicate a card in the Thesis topics section and point its link at the PDF.
4. When a topic is no longer available, remove its card and its PDF.

## Files

- `main.tex`: the content, and the only file to edit for a new topic.
- `corelab-thesis.cls`: the layout shared by all flyers. Change it only to change every flyer.
- `logos/`: the CoReLab and UiS logos.

`Documents/theses/example-topic.pdf` is this template compiled as it is, with the placeholder text.

If you change the template, rebuild the zip:

```sh
cd Documents/theses/template
zip -r ../thesis-topic-template.zip main.tex corelab-thesis.cls logos
```
