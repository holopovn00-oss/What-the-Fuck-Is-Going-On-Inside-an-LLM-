"""Build this issue with the approved Agents/Deep Research Atlas page design."""

from pathlib import Path
from tempfile import TemporaryDirectory
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = HERE / "hardware_issue.md"
TARGET = HERE / "hardware_issue.pdf"
TEMPLATE = ROOT / "archive/chapter_builds/agents/build_workspace.py"

LEADS = [
    "От паспорта нагрузки к измеримому решению о машине.",
    "Нижние оценки весов, KV-кэша и рабочих буферов.",
    "Почему полное обучение, LoRA и QLoRA требуют разных бюджетов.",
    "Prefill, decode, очередь, пропускная способность и задержка.",
    "Совместимость ускорителя, CPU, RAM, диска, платы и питания.",
    "Векторный индекс, корпус и генерация как раздельные бюджеты.",
    "От требований и измерений к обоснованной конфигурации.",
    "Опыты на реальной нагрузке и направления дальнейшего исследования.",
]
PAGES = {}
SIDES = {
    1: [r"\sidehead{Выпуск 01}26 сентября 2026. Учебная глава к блоку VII, темам 7.1–7.12. Формулы дают оценки; конкретные checkpoint и runtime проверяются опытом.\sidehead{Что читатель сможет}Разложить нагрузку на этапы.\par Посчитать веса, KV-кэш и индекс.\par Различить бюджеты обучения и инференса.\par Составить паспорт и измерить результат.\sidehead{Вопросы к машине}Что запускаем? Сколько контекста и активных запросов? Какую задержку считаем допустимой?"],
    2: [r"\sidehead{Перевод единиц}1 GB = $10^9$ байт.\par 1 GiB = $2^{30}$ байт.\sidehead{Три слоя оценки}Сырые веса; KV-кэш; буферы runtime и квантования.\sidehead{MoE}Различайте общие веса и активные параметры за токен."],
    3: [r"\sidehead{Память обучения}Веса, градиенты, оптимизатор, активации и временные тензоры.\sidehead{Выбор метода}Полное обновление; адаптеры LoRA; QLoRA поверх квантованной базы.\sidehead{Восстановление}Проверьте запуск после сбоя."],
    4: [r"\sidehead{Метрики сервиса}TTFT — до первого токена.\par ITL/TPOT — пауза между токенами.\par p95/p99 — хвостовые задержки.\sidehead{Равные условия}Модель, длины входа и ответа, частота запросов, batch, драйвер и backend."],
    5: [r"\sidehead{Совместимость}Точный checkpoint\par $\downarrow$\par Runtime и операции\par $\downarrow$\par ОС и драйвер\par $\downarrow$\par Конкретный GPU\sidehead{Кроме GPU}CPU, RAM, SSD, PCIe, плата, БП, охлаждение, сеть и резервные копии."],
    6: [r"\sidehead{Три бюджета}Исходники и копии.\par Индекс, текст и метаданные.\par Модели, KV-кэш и вычисления.\sidehead{Качество}Страница цитаты, права доступа, версия документа, recall и задержка."],
    7: [r"\sidehead{Паспорт}Checkpoint и ревизия.\par Активные запросы.\par Контекст и ответ.\par Корпус и индекс.\par Задержка, качество, полная стоимость.\sidehead{Решение}Измерить baseline, проверить совместимость, оценить память, испытать нагрузку, сохранить спецификацию."],
    8: [r"\sidehead{Четыре опыта}A. Память.\par B. Скорость CPU/GPU/offload.\par C. Индекс и поиск RAG.\par D. Обучение, LoRA, QLoRA.\sidehead{Сравнение}Одинаковые данные и качество; версии стека; p95 и цена задачи."],
}
RU = [
    "Руководство по программированию CUDA",
    "Roofline: наглядная модель пределов производительности",
    "FlashAttention: точное внимание с учётом обмена с памятью",
    "Стратегии кэширования ключей и значений",
    "Эффективное управление памятью при обслуживании LLM с PagedAttention",
    "Инференс больших моделей",
    "Начало работы с полностью шардированным параллелизмом данных",
    "ZeRO: оптимизация памяти для обучения крупных моделей",
    "QLoRA: эффективная адаптация квантованных LLM",
    "Квантование и адаптеры PEFT",
    "Интерфейс измерения производительности vLLM",
    "Документация vLLM",
    "llama.cpp: код и документация для локального инференса",
    "Матрица совместимости ROCm",
    "Вычислительные возможности GPU NVIDIA",
    "MLX: машинное обучение на Apple Silicon",
    "pgvector: индексация, точный и приближённый поиск",
    "Метрики экспортера DCGM",
]
REF = re.compile(r"(?m)^(\d+)\. (.+?), \*(.*?)\* \((.*?)\)\. (.*?) \*\*Читать:\*\* (.*?) \[(.*?)\]\((.*?)\)\.$")
GROUP = re.compile(r"(?m)^\*\*(Вводные работы|Специализированные работы|Фронтир исследований)\*\*$")


def esc(s):
    s = s.replace("`", "")
    for c, v in [("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_"), ("$", r"\$")]:
        s = s.replace(c, v)
    return s


def md_tex(md):
    result = subprocess.run(["pandoc", "-f", "markdown+tex_math_dollars+raw_tex", "-t", "latex", "--wrap=none"],
                            input=md, text=True, capture_output=True, check=True)
    return result.stdout.strip()


def table_as_prose(block):
    rows = [[x.strip() for x in line.strip().strip("|").split("|")]
            for line in block.splitlines() if line.strip().startswith("|")]
    assert len(rows) >= 3
    labels = rows[0]
    output = []
    for row in rows[2:]:
        assert len(row) == len(labels)
        fields = "; ".join(f"{label.lower()}: {value}" for label, value in zip(labels[1:], row[1:]))
        output.append(f"**{row[0]}.** {fields}.")
    return "\n\n".join(output)


def parse():
    source = SOURCE.read_text(encoding="utf-8")
    matches = re.findall(r"(?ms)^## (\d+)\. ([^\n]+)\n(.*?)(?=^## |\Z)", source)
    assert len(matches) == 8
    topics, all_refs = [], []
    for number, title, raw in matches:
        marker = f"### Литература к разделу {number}"
        body, bibliography = raw.split(marker, 1) if marker in raw else (raw, "")
        if "\n---\n" in bibliography:
            bibliography, closing = bibliography.split("\n---\n", 1)
            body += "\n\n" + closing
        blocks = [b.strip() for b in re.split(r"\n\s*\n", body) if b.strip()]
        pieces = GROUP.split(bibliography)
        refs = []
        for group, segment in zip(pieces[1::2], pieces[2::2]):
            for m in REF.finditer(segment):
                n, author, name, year, note, where, label, url = m.groups()
                refs.append(dict(n=int(n), author=author, name=name, year=year, note=note,
                                 where=where, url=url, group=group))
        topics.append(dict(n=int(number), title=title, blocks=blocks, refs=refs))
        all_refs += refs
    assert [r["n"] for r in all_refs] == list(range(1, 19))
    return topics


def preamble():
    archived = TEMPLATE.read_text(encoding="utf-8")
    head = re.search(r"head=r'''(.*?)'''", archived, re.S).group(1)
    head = re.sub(r"(?m)^\\newfontfamily\\harding.*\n", "", head)
    head = head.replace("АГЕНТЫ", "ЖЕЛЕЗО")
    head = head.replace("Архитектура агентов", "Железо для ИИ")
    head = head.replace("\\begin{document}", "\\setmonofont{DejaVu Sans Mono}\\newfontfamily\\cyrillicfonttt{DejaVu Sans Mono}\n\\providecommand{\\tightlist}{\\setlength{\\itemsep}{0pt}\\setlength{\\parskip}{0pt}}\n\\begin{document}\\pagestyle{articlepage}")
    return head


def heading(topic):
    left = "VII. Вычислительное железо, инфраструктура и локальные модели" if topic["n"] == 1 else "Железо для ИИ"
    right = "" if topic["n"] == 1 else esc(topic["title"])
    return r"{\sffamily\fontsize{7.5}{9.5}\selectfont " + left + r"\hfill " + right + r"\par}\vspace{5pt}\thinrule\vspace{8pt}"


def bibliography(topic):
    parts = [r"\clearpage\bibpagetrue\pagestyle{bibliopage}\pdfbookmark[1]{Библиография: " + esc(topic["title"]) + r"}{bib" + str(topic["n"]) + r"}",
             r"\begingroup\setlength{\parskip}{0pt}\setlength{\emergencystretch}{3em}\begin{adjustwidth}{3mm}{3mm}\vspace*{0pt}",
             r"{\centering\fontsize{14}{18}\selectfont\addfontfeatures{LetterSpace=3}БИБЛИОГРАФИЯ\par}\vspace{8pt}{\centering\rule{.72\linewidth}{.35pt}\par}\vspace{6pt}"]
    last = None
    for r in topic["refs"]:
        if r["group"] != last:
            parts.append(r"\Needspace{130pt}\vspace{6pt}{\centering\fontsize{9.5}{12}\selectfont\addfontfeatures{LetterSpace=4}" + r["group"].upper() + r"\par}\vspace{6pt}")
            last = r["group"]
        n = r["n"]
        kind = "Исследовательская статья" if n in {2, 3, 5, 8, 9} else "Код и документация" if n in {13, 16, 17} else "Документация"
        original = (f'{n}.\\enspace {esc(r["author"])} ({esc(r["year"])}), ' + r"\href{" + r["url"] + r"}{\textit{" + esc(r["name"]) + r"}}. " + kind + ".")
        parts.append(r"\begin{minipage}[t]{\linewidth}\vspace{0pt}\fontsize{10.5}{12.8}\selectfont{\hangindent=1.4em\hangafter=1 " + original + r"\par}\vspace{4pt}{\leftskip=1.4em " + esc(RU[n-1]) + r"\par\vspace{6pt}" + esc(r["note"]) + r"\par\vspace{5pt}\textit{Что читать.} " + esc(r["where"]) + r"\par}\end{minipage}\par\vspace{6pt}")
    parts.append(r"\end{adjustwidth}\endgroup\clearpage\bibpagefalse\pagestyle{articlepage}")
    return "\n".join(parts)


def build():
    parts = [preamble()]
    for index, topic in enumerate(parse()):
        n = topic["n"]
        pages = PAGES.get(n, [list(range(len(topic["blocks"])))])
        assert sorted(j for page in pages for j in page) == list(range(len(topic["blocks"])))
        for j, indices in enumerate(pages):
            if index or j:
                parts.append(r"\clearpage")
            if not j:
                parts.append(r"\hypertarget{topic" + str(n) + r"}{}\pdfbookmark[0]{" + esc(topic["title"]) + r"}{topic" + str(n) + r"}")
            parts.append(heading(topic))
            if not j:
                title = "Железо для ИИ" if n == 1 else f'{n}. {topic["title"]}'
                size = "25}{28}" if n == 1 else "21}{24}"
                display_title = esc(title)
                if n == 5:
                    display_title = r"5. Компоненты локальной машины\\[3pt]и совместимость"
                parts.append(r"{\fontsize{" + size + r"\selectfont " + display_title + r"\par}\vspace{8pt}")
                parts.append(r"{\fontsize{11.5}{14.5}\selectfont " + esc(LEADS[index]) + r"\par}\vspace{7pt}\thinrule")
            body = []
            if n == 1 and not j:
                body += [r"\subhead{1. Машину выбирают под работу}", md_tex("**Цель выпуска.** Рассчитать проверяемое требование к машине для обучения, инференса, локальных моделей и RAG. Числа в примерах учебные; совместимость и скорость подтверждаются опытом на точной модели.")]
            for block_index in indices:
                block = topic["blocks"][block_index]
                body.append(md_tex(table_as_prose(block) if block.startswith("|") else block))
            side = SIDES[n][min(j, len(SIDES[n])-1)]
            parts.append(r"\columns{" + "\n\n".join(body) + r"}{" + side + r"}")
        if topic["refs"]:
            parts.append(bibliography(topic))
    parts.append(r"\end{document}")
    return "\n".join(parts)


def main():
    import pyphen

    tex = build()
    prefix, body = tex.split(r"\begin{document}", 1)
    dictionary = pyphen.Pyphen(lang="ru_RU")
    body = re.sub(r"[А-Яа-яЁё]{6,}", lambda m: dictionary.inserted(m.group(), hyphen=r"\-"), body)
    tex = prefix + r"\begin{document}" + body
    with TemporaryDirectory() as path:
        temp = Path(path)
        (temp / "fonts").mkdir()
        for name in ("SourceSerif4-Regular.otf", "SourceSerif4-Bold.otf", "SourceSerif4-It.otf"):
            shutil.copy(ROOT / "assets/fonts" / name, temp / "fonts" / name)
        (temp / "typeset.tex").write_text(tex, encoding="utf-8")
        for _ in range(2):
            result = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "typeset.tex"], cwd=temp, capture_output=True, text=True)
            if result.returncode:
                raise RuntimeError(result.stdout[-5000:])
            warnings = [line for line in result.stdout.splitlines() if "Overfull" in line or "Missing character" in line]
            if warnings:
                raise RuntimeError("Typesetting: " + "; ".join(warnings[:12]))
        shutil.copy(temp / "typeset.pdf", TARGET)
    print(TARGET)


if __name__ == "__main__":
    main()
