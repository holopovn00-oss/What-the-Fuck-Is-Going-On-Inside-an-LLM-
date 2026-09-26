"""Typeset this issue with Pandoc, XeLaTeX and the repository font."""

from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FONT = ROOT / "assets/fonts"
SOURCE = HERE / "hardware_issue.md"
TARGET = HERE / "hardware_issue.pdf"


def main():
    with TemporaryDirectory() as directory:
        temp = Path(directory)
        header = temp / "header.tex"
        header.write_text(r"""
\usepackage{fontspec}
\setmainfont{SourceSerif4-Regular.otf}[Path=FONTDIR/,BoldFont=SourceSerif4-Bold.otf,ItalicFont=SourceSerif4-It.otf]
\setmonofont{DejaVu Sans Mono}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{needspace}
\titleformat{\section}[block]{\normalfont\bfseries\fontsize{23}{27}\selectfont}{}{0pt}{}
\titlespacing*{\section}{0pt}{0pt}{11pt}
\pagestyle{fancy}
\fancyhf{}
\fancyfoot[L]{\small АТЛАС / ЖЕЛЕЗО · 01}
\fancyfoot[R]{\thepage}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0.3pt}
\setlength{\footskip}{20pt}
\AtBeginDocument{\hypersetup{hidelinks,pdftitle={What the Fuck Is Going On Inside an LLM? — Железо для ИИ}}}
""".replace("FONTDIR", str(FONT)), encoding="utf-8")

        # The web version uses plain bold labels; the PDF centers bibliography groups.
        body = SOURCE.read_text(encoding="utf-8")
        for label in ("Вводные работы", "Специализированные работы", "Фронтир исследований"):
            body = body.replace(f"**{label}**", "\\Needspace{6\\baselineskip}\n\n\\begin{center}\\small " + label + "\\end{center}")
        body = body.replace("**Модель ограничений.**", "\\Needspace{8\\baselineskip}\n\n**Модель ограничений.**")
        body = body.replace("| Поле | Пример записи |", "\\Needspace{18\\baselineskip}\n\n| Поле | Пример записи |")
        body = body.replace("### Литература к разделу", "\\Needspace{9\\baselineskip}\n\n### Литература к разделу")
        temporary_md = temp / "issue.md"
        temporary_md.write_text(body, encoding="utf-8")
        command = [
            "pandoc", str(temporary_md), "--from=markdown+tex_math_dollars+raw_tex",
            "--pdf-engine=xelatex",
            "-V", "documentclass=article", "-V", "fontsize=11pt",
            "-V", "papersize=a4",
            "-V", "geometry:left=22mm,right=20mm,top=20mm,bottom=20mm",
            "-V", "lang=ru-RU", "-V", "colorlinks=false",
            "-H", str(header), "-o", str(TARGET),
        ]
        subprocess.run(command, check=True, cwd=HERE)
    print(TARGET)


if __name__ == "__main__":
    main()
