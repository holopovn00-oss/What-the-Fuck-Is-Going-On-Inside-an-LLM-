# Выпуск 01: железо для ИИ

- [Глава Markdown](hardware_issue.md)
- [PDF](hardware_issue.pdf)
- [Шаблон нагрузки](workload_example.json)
- [Калькулятор нижних оценок](calculator.py)
- [Журнал проверки](review_log.md)

Из этой папки запустите `python3 calculator.py workload_example.json`. Поменяйте параметры на характеристики точной архитектуры и нагрузки; результат не является тестом совместимости. Сопоставьте прогноз с реальными измерениями.

PDF пересобирается командой `python3 build_pdf.py` при наличии Pandoc, XeLaTeX, стандартных пакетов TeX и DejaVu Sans Mono. Основной шрифт берётся из `assets/fonts/` репозитория.
