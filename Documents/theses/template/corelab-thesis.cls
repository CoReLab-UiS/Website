% CoReLab thesis topic flyer – layout.
% Write the content in main.tex. Change this file only to change the layout of every topic flyer.
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{corelab-thesis}[2026/10/12 CoReLab thesis topic flyer]

\LoadClass[11pt,a4paper]{article}

\RequirePackage[T1]{fontenc}
\RequirePackage[utf8]{inputenc}
\RequirePackage{tgheros}                  % Helvetica-like, matches the Arial wordmark of the logo
\renewcommand*{\familydefault}{\sfdefault}
\RequirePackage{microtype}
\RequirePackage[a4paper,top=1.3cm,bottom=1.9cm,left=1.9cm,right=1.9cm,footskip=1cm]{geometry}
\RequirePackage{xcolor}
\RequirePackage{graphicx}
\RequirePackage{paracol}
\RequirePackage{enumitem}
\RequirePackage{titlesec}
\RequirePackage[most]{tcolorbox}
\RequirePackage{qrcode}
\RequirePackage{fancyhdr}
\RequirePackage{hyperref}

% ---------- Colors (same palette as the website) ----------
\definecolor{clblue}{HTML}{0062A3}   % CoReLab deep blue
\definecolor{clsky}{HTML}{4A9AD4}    % CoReLab sky blue – decoration only, too light for text
\definecolor{cllight}{HTML}{A8CBEA}  % CoReLab light blue
\definecolor{clnavy}{HTML}{004090}   % UiS navy, used for headings
\definecolor{cltint}{HTML}{EEF5FC}   % light background
\definecolor{cltext}{HTML}{1A2633}
\definecolor{clmuted}{HTML}{556373}

\hypersetup{colorlinks=true, urlcolor=clblue, linkcolor=clblue, pdfcreator={CoReLab thesis topic template}}
\AtBeginDocument{\color{cltext}}

\setlength{\parindent}{0pt}
\setlength{\parskip}{0.5em}
\linespread{1.04}

% ---------- Fields set in main.tex ----------
\newcommand{\@thesistype}{Thesis}
\newcommand{\@thesistitle}{}
\newcommand{\@topicsurl}{https://corelab-uis.github.io/Website/\#theses}
\newcommand{\thesistype}[1]{\renewcommand{\@thesistype}{#1}}
\newcommand{\thesistitle}[1]{\renewcommand{\@thesistitle}{#1}\hypersetup{pdftitle={#1}}}

% ---------- Header: logos, thesis type, title between two rules ----------
\newcommand{\makeflyerhead}{%
  \thispagestyle{fancy}%
  \noindent
  \begin{minipage}[c]{0.7\textwidth}\includegraphics[height=1.7cm]{logos/corelab-logo}\end{minipage}%
  \hfill
  \begin{minipage}[c]{0.2\textwidth}\raggedleft\includegraphics[height=1.7cm]{logos/uis-logo}\end{minipage}\par
  \vspace{0.7cm}%
  {\color{clblue}\small\bfseries\textls[120]{\MakeUppercase{\@thesistype}}\par}
  \vspace{0.15cm}%
  {\color{clsky}\rule{\textwidth}{0.8pt}}\par
  \vspace{0.2cm}%
  {\raggedright\fontsize{21}{26}\selectfont\color{clblue}\@thesistitle\par}
  \vspace{0.3cm}%
  {\color{clsky}\rule{\textwidth}{0.8pt}}\par
  \vspace{0.5cm}%
}

% ---------- Body: main text on the left, info sidebar on the right ----------
\newenvironment{topic}{%
  \columnratio{0.66}%
  \setlength{\columnsep}{0.9cm}%
  \setlength{\columnseprule}{0.4pt}%
  \colseprulecolor{cllight}%
  \begin{paracol}{2}\raggedright
}{%
  \end{paracol}%
}
\newcommand{\sidebar}{\switchcolumn\small\raggedright}

% \infoblock{Heading}{Content}
\newcommand{\infoblock}[2]{%
  {\color{clnavy}\bfseries #1\par}\nopagebreak
  {\setlength{\parskip}{0pt}#2\par}\vspace{0.9em}}

% \person{Name}{Position and institution}{email}
\newcommand{\person}[3]{%
  {\setlength{\parskip}{0pt}#1\par #2\par \email{#3}\par}}

\newcommand{\email}[1]{\href{mailto:#1}{#1}}

% \note{Text}: short remark in blue in the sidebar
\newcommand{\note}[1]{{\color{clblue}#1\par}\vspace{0.9em}}

% QR code to the thesis topics on the website
\newcommand{\moretopics}{%
  {\color{clnavy}\bfseries More topics\par}\nopagebreak
  \vspace{0.3em}%
  \href{https://corelab-uis.github.io/Website/\#theses}{\qrcode[height=2.3cm]{\@topicsurl}}\par
  \vspace{0.2em}%
  {\footnotesize\color{clmuted}corelab-uis.github.io/Website\par}}

% Highlighted paragraph, e.g. for a bonus such as a possible publication
\newtcolorbox{highlight}{enhanced, breakable, colback=cltint, colframe=cltint, boxrule=0pt,
  sharp corners, borderline west={3pt}{0pt}{clsky}, left=10pt, right=8pt, top=5pt, bottom=5pt,
  before skip=0.8em, after skip=0.4em, before upper=\raggedright}

% ---------- Headings and lists ----------
\titleformat{\section}{\normalsize\bfseries\color{clnavy}}{}{0pt}{}
\titlespacing*{\section}{0pt}{0.9em}{0.1em}

\setlist[itemize]{leftmargin=1.1em, itemsep=0.2em, parsep=0pt, topsep=0.2em,
  label={\color{clsky}\textbullet}}

% ---------- Footer ----------
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrule}{{\color{cllight}\hrule height 0.4pt}\vspace{0.3em}}
\fancyfoot[L]{\footnotesize\color{clmuted}CoReLab \textperiodcentered{} Computational Research Laboratory \textperiodcentered{} University of Stavanger}
\fancyfoot[R]{\footnotesize\href{https://corelab-uis.github.io/Website/}{corelab-uis.github.io/Website}}
