"""Typeset the separate PC-building companion in the approved book composition.

Each unit has two article pages and one local bibliography. Issue 1.1 is not modified.
"""

from pathlib import Path
import json
import re
import shutil
import subprocess
import sys
import tempfile

from content import C, S

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FONT_DIR = ROOT / "assets/fonts"
TARGET = HERE / "pc_build_20b.pdf"
MARKDOWN = HERE / "pc_build_20b.md"
SOURCE_INDEX = HERE / "sources.json"
RUNNING = ["20B: режимы работы", "Сборки и приёмка"]
GROUPS = ["Вводные работы", "Специализированные работы", "Фронтир исследований"]


def esc(value):
    for character, replacement in (("&", r"\&"), ("%", r"\%"),
                                   ("#", r"\#"), ("_", r"\_")):
        value = value.replace(character, replacement)
    return value


PREAMBLE = r"""\documentclass[10pt,a4paper]{article}
\usepackage[left=17mm,right=16mm,top=14mm,bottom=17mm]{geometry}
\usepackage{fontspec,polyglossia}
\setdefaultlanguage{russian}
\setmainfont{SourceSerif4-Regular.otf}[Path=fonts/,BoldFont=SourceSerif4-Bold.otf,ItalicFont=SourceSerif4-It.otf]
\setsansfont{NimbusSans-Regular.otf}[Path=/usr/share/fonts/opentype/urw-base35/,BoldFont=NimbusSans-Bold.otf]
\usepackage{unicode-math}\setmathfont{Latin Modern Math}
\usepackage{xcolor,amsmath,eso-pic,fancyhdr,needspace,changepage}
\definecolor{rulegray}{gray}{.5}
\usepackage[colorlinks=true,urlcolor=black,linkcolor=black,bookmarksnumbered=true]{hyperref}
\hypersetup{pdftitle={Локальный ИИ-ПК: сборка и 20B},pdfauthor={Атлас: аппаратная архитектура и локальные модели},pdfsubject={Учебный выпуск и локальная аннотированная библиография}}
\pagestyle{fancy}\fancyhf{}\renewcommand{\headrulewidth}{0pt}\renewcommand{\footrulewidth}{.3pt}
\fancyfoot[L]{\sffamily\fontsize{7.5}{9}\selectfont АТЛАС / ЖЕЛЕЗО И ЛОКАЛЬНЫЕ МОДЕЛИ}
\fancyfoot[R]{\sffamily\fontsize{8}{9}\selectfont\thepage}
\setlength{\footskip}{21pt}\setlength{\parindent}{0pt}\setlength{\parskip}{6pt}
\setlength{\emergencystretch}{1.5em}\widowpenalty=10000\clubpenalty=10000
\fancypagestyle{bibliopage}{\fancyhf{}\renewcommand{\headrulewidth}{0pt}\renewcommand{\footrulewidth}{0pt}\fancyfoot[C]{\fontsize{10}{12}\selectfont\thepage}}
\newif\ifbibpage
\newcommand{\thinrule}{\par{\color{rulegray}\hrule height .3pt}\par}
\newcommand{\subhead}[1]{\par\vspace{8pt}{\bfseries\fontsize{11}{13.2}\selectfont #1}\par\vspace{3pt}}
\newcommand{\sidehead}[1]{\par\vspace{10pt}\textbf{#1}\par\vspace{5pt}}
\newcommand{\step}[1]{\par\vspace{7pt}\textbf{#1}\par\vspace{3pt}}
\newsavebox{\maincolumn}\newsavebox{\sidecolumn}\newlength{\columnheight}\newlength{\columndepth}
\newcommand{\columns}[2]{
\begin{lrbox}{\maincolumn}\begin{minipage}[t]{.685\linewidth}\vspace{0pt}\fontsize{10.5}{13.4}\selectfont\setlength{\abovedisplayskip}{7pt}\setlength{\belowdisplayskip}{7pt}#1\end{minipage}\end{lrbox}
\begin{lrbox}{\sidecolumn}\begin{minipage}[t]{.266\linewidth}\vspace{0pt}\raggedright\sffamily\fontsize{9}{11.6}\selectfont#2\end{minipage}\end{lrbox}
\setlength{\columndepth}{\dp\maincolumn}\ifdim\dp\sidecolumn>\columndepth\setlength{\columndepth}{\dp\sidecolumn}\fi
\setlength{\columnheight}{\dimexpr\ht\maincolumn+\columndepth\relax}
\noindent\usebox{\maincolumn}\hfill\raisebox{-\columndepth}{\color{rulegray}\rule{.4pt}{\columnheight}}\hfill\usebox{\sidecolumn}}
\AddToShipoutPictureBG{\ifbibpage\else\AtPageLowerLeft{\color{rulegray}\put(41,42){\rule{.3pt}{760pt}}}\fi}
\begin{document}
"""


def work_links(text, references):
    def render(match):
        key, label = match.groups()
        assert key in references, (key, references)
        return (r"\href{" + S[key]["url"] + "}{" + label
                + r"\textsuperscript{" + str(references.index(key) + 1) + "}}")

    return re.sub(r"\\work\{([^{}]+)\}\{([^{}]+)\}", render, text)


def markdown(text, references):
    text = re.sub(r"\\work\{([^{}]+)\}\{([^{}]+)\}",
                  lambda m: f"[{m[2]}]({S[m[1]]['url']}) [{references.index(m[1])+1}]", text)
    def table(match):
        rows = [[cell.strip() for cell in row.split("&")]
                for row in match[1].strip().split(r"\\") if row.strip()]
        assert rows and all(len(row) == len(rows[0]) for row in rows)
        return ("\n\n| " + " | ".join(rows[0]) + " |\n"
                + "|" + "|".join("---" for _ in rows[0]) + "|\n"
                + "\n".join("| " + " | ".join(row) + " |" for row in rows[1:])
                + "\n\n")
    text = re.sub(
        r"\\begin\{center\}\\begin\{tabular\}\{rcc\}(.*?)\\end\{tabular\}\\end\{center\}",
        table, text, flags=re.S)
    text = re.sub(r"\\(subhead|sidehead)\{([^{}]+)\}", r"\n### \2\n\n", text)
    text = re.sub(r"\\step\{([^{}]+)\}", r"\n**\1** ", text)
    text = re.sub(r"\\hyperlink\{topic[0-9]+\}\{([^{}]+)\}", r"\1", text)
    text = text.replace(r"\emph{", "*").replace(r"\textbf{", "**")
    # All emphasis in source is one-level text without nested braces.
    text = re.sub(r"\*([^{}\n]+)\}", r"*\1*", text)
    text = text.replace(r"\(", "$" ).replace(r"\)", "$" )
    text = text.replace(r"\[", "\n$$\n").replace(r"\]", "\n$$\n")
    text = text.replace(r"\,", " ").replace(r"\par", "\n\n")
    return text.strip()


def page_header(index):
    left = "VII. Вычислительное железо, инфраструктура и локальные модели" if index == 0 else "Железо и локальные модели"
    right = "" if index == 0 else RUNNING[index]
    return (r"{\sffamily\fontsize{7.5}{9.5}\selectfont " + left + r"\hfill "
            + right + r"\par}\vspace{5pt}\thinrule\vspace{8pt}")


def bibliography(index, chapter):
    lines = [r"\clearpage\pdfbookmark[1]{Библиография: " + chapter["title"]
             + "}{bib" + str(index) + "}",
             r"\bibpagetrue\thispagestyle{bibliopage}\begingroup\setlength{\parskip}{0pt}\setlength{\emergencystretch}{3em}\begin{adjustwidth}{8mm}{9mm}\vspace*{12pt}",
             r"{\centering\fontsize{14}{18}\selectfont\addfontfeatures{LetterSpace=3}БИБЛИОГРАФИЯ\par}\vspace{11pt}{\centering\rule{.72\linewidth}{.35pt}\par}\vspace{9pt}"]
    previous = None
    for number, key in enumerate(chapter["refs"], 1):
        item = S[key]
        level = "Вводные работы" if index == 0 else item["group"]
        if level != previous:
            lines.append(r"\Needspace{120pt}\vspace{8pt}{\centering\fontsize{9.5}{12}\selectfont\addfontfeatures{LetterSpace=4}"
                         + level.upper() + r"\par}\vspace{10pt}")
            previous = level
        original = (str(number) + r".\enspace " + esc(item["author"]) + " ("
                    + esc(item["year"]) + r"), \href{" + item["url"]
                    + r"}{\textit{" + esc(item["title"]) + "}}. " + esc(item["kind"]) + ".")
        lines.append(r"\begin{minipage}[t]{\linewidth}\vspace{0pt}\fontsize{10.5}{13.2}\selectfont{\hangindent=1.4em\hangafter=1 "
                     + original + r"\par}\vspace{5pt}{\leftskip=1.4em "
                     + esc(item["ru"]) + r"\par\vspace{6pt}"
                     + esc(item["note"]) + r"\par\vspace{5pt}\textit{Что читать.} "
                     + esc(item["where"]) + r"\par}\end{minipage}\par\vspace{6pt}")
    lines.append(r"\vspace{6pt}{\fontsize{10}{12.8}\selectfont\textit{Порядок чтения.} "
                 + esc(chapter["route"]) + r"\par}\end{adjustwidth}\endgroup\clearpage\bibpagefalse")
    return "\n".join(lines)


def build():
    assert len(C) == 2
    for chapter in C:
        assert [S[k]["group"] for k in chapter["refs"]] == sorted(
            [S[k]["group"] for k in chapter["refs"]], key=GROUPS.index)

    parts = [PREAMBLE]
    md = ["# Локальный ИИ-ПК: сборка и 20B\n\nАтлас · учебный выпуск к блоку VII · 27 сентября 2026\n\n"
          "Две части к темам 7.9 и 7.11. Сборки являются учебными ведомостями; точные детали и модели требуют проверки.\n"]
    for index, chapter in enumerate(C):
        refs = chapter["refs"]
        for page_index, page in enumerate(chapter["pages"]):
            if index or page_index:
                parts.append(r"\clearpage")
            if page_index == 0:
                parts.append(r"\hypertarget{topic" + str(index) + r"}{}\pdfbookmark[0]{"
                             + chapter["title"] + "}{section" + str(index) + "}")
            parts.append(page_header(index))
            if page_index == 0:
                title = r"Локальный ИИ-ПК:\\[3pt]сборка и 20B" if index == 0 else chapter["title"]
                size = "25}{28" if index == 0 else "21}{24"
                parts.append(r"{\fontsize{" + size + r"}\selectfont " + title + r"\par}\vspace{8pt}")
                parts.append(r"{\fontsize{11.5}{14.5}\selectfont " + chapter["lead"]
                             + r"\par}\vspace{7pt}\thinrule")
                md.append("\n## " + chapter["title"] + "\n\n" + chapter["lead"] + "\n")
            parts.append(r"\columns{" + work_links(page["main"], refs) + "}{"
                         + work_links(page["side"], refs) + "}")
            side = markdown(page["side"], refs)
            quoted_side = "\n".join("> " + line if line else ">"
                                    for line in side.splitlines())
            md.append("\n" + markdown(page["main"], refs) + "\n\n"
                      + quoted_side + "\n")
        parts.append(bibliography(index, chapter))
        md.append("\n### Библиография\n")
        last = None
        for number, key in enumerate(refs, 1):
            item = S[key]
            level = "Вводные работы" if index == 0 else item["group"]
            if level != last:
                md.append("\n#### " + level + "\n")
                last = level
            md.append(f"\n{number}. {item['author']} ({item['year']}), *[{item['title']}]({item['url']})*. {item['kind']}.\n\n"
                      f"   {item['ru']}\n\n   {item['note']}\n\n   *Что читать.* {item['where']}\n")
        md.append("\n**Порядок чтения.** " + chapter["route"] + "\n")
    parts.append(r"\end{document}")
    tex = "\n".join(parts)

    try:
        import pyphen
    except ImportError as exc:
        raise SystemExit("Install pyphen from requirements.txt before typesetting") from exc
    hyphenator = pyphen.Pyphen(lang="ru_RU")
    start, body = tex.split(r"\begin{document}", 1)
    body = re.sub(r"[А-Яа-яЁё]{6,}", lambda m: hyphenator.inserted(m[0], hyphen=r"\-"), body)

    with tempfile.TemporaryDirectory(prefix="atlas_hardware_") as temp:
        work = Path(temp)
        fonts = work / "fonts"
        fonts.mkdir()
        for filename in ("SourceSerif4-Regular.otf", "SourceSerif4-Bold.otf", "SourceSerif4-It.otf"):
            shutil.copy(FONT_DIR / filename, fonts / filename)
        (work / "typeset.tex").write_text(start + r"\begin{document}" + body, encoding="utf-8")
        for _ in range(2):
            result = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "typeset.tex"],
                                    cwd=work, capture_output=True, text=True)
            if result.returncode:
                (HERE / "compile_failure.log").write_text(result.stdout, encoding="utf-8")
                (HERE / "compile_failure.tex").write_text((work / "typeset.tex").read_text(encoding="utf-8"), encoding="utf-8")
                raise RuntimeError(result.stdout[-6000:])
        print("\n".join(line for line in result.stdout.splitlines()
                        if "Overfull" in line or "Missing character" in line or "Output written" in line))
        shutil.copy(work / "typeset.pdf", TARGET)
    MARKDOWN.write_text("\n".join(md), encoding="utf-8")
    SOURCE_INDEX.write_text(json.dumps({
        "checked": "2026-09-27", "scope": "Official model card, manufacturer specifications, memory and PEFT documentation; QLoRA abstract. Build feasibility is an editorial inference awaiting a live test.",
        "sources": S,
        "sections": [{"title": c["title"], "sources": c["refs"]} for c in C],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Created", TARGET, "and", MARKDOWN, "with", len(C), "units")


if __name__ == "__main__":
    build()
