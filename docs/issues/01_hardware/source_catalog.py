"""Primary-source catalog for the hardware issue.

Page text is LaTeX so equations, citations, and the narrow marginal notes remain
under direct editorial control. Sources are primary papers or maintainer docs.
"""

S = {}


def source(key, author, year, title, ru, url, kind, note, where, group):
    S[key] = dict(author=author, year=year, title=title, ru=ru, url=url,
                  kind=kind, note=note, where=where, group=group)


source('cuda', 'NVIDIA', 'документация, 2026', 'CUDA Programming Guide',
       'Руководство по программированию CUDA',
       'https://docs.nvidia.com/cuda/cuda-programming-guide/', 'Документация',
       'Описаны устройство вычислительных блоков, пространства памяти, запуск ядер и программная модель CUDA. Термины помогают отделить локальность данных от паспортного числа операций в секунду.',
       'Programming Model; Understanding Memory; Features and Technical Specifications. Нарисовать путь данных от RAM до регистров.', 'Вводные работы')
source('roof', 'Williams, S.; Waterman, A.; Patterson, D.', '2009',
       'Roofline: An Insightful Visual Performance Model for Floating-Point Programs and Multicore Architectures',
       'Roofline: модель верхних границ вычислений и обмена с памятью',
       'https://www2.eecs.berkeley.edu/Pubs/TechRpts/2008/EECS-2008-134.html', 'Исследовательская статья',
       'Связывает достижимую производительность ядра с арифметической интенсивностью, пиком вычислений и пропускной способностью памяти. Даёт язык для гипотезы об узком месте, но не прогнозирует задержку целого сервиса.',
       'Разделы о модели и operational intensity; построить две границы для одной операции, указать допущения.', 'Специализированные работы')
source('flash', 'Dao, T. и др.', '2022',
       'FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness',
       'FlashAttention: точное внимание с учётом обмена между уровнями памяти',
       'https://papers.nips.cc/paper_files/paper/2022/hash/67d57c32e20fd0a7a302cb81d36e40d5-Abstract-Conference.html', 'NeurIPS',
       'Разбиение вычисления attention на блоки уменьшает движение данных между HBM и быстрой памятью GPU. Это пример ускорения без изменения математической цели attention; эффект зависит от формы задачи и реализации.',
       'Постановка IO-aware attention и раздел Algorithm; объяснить, какие промежуточные данные перестают записываться в HBM.', 'Специализированные работы')
source('best', 'NVIDIA', 'документация, 2026', 'CUDA C++ Best Practices Guide',
       'Практическое руководство по производительности CUDA',
       'https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/', 'Документация',
       'Документация разбирает передачу данных, локальность, coalescing и профилирование. Полезна для понимания, почему фактическая пропускная способность ниже рекламируемой и когда загрузка GPU не означает эффективную работу.',
       'Data Transfer Between Host and Device; Memory Optimizations; Performance Metrics. Сравнить requested и actual bandwidth.', 'Вводные работы')
source('hf_cache', 'Hugging Face', 'документация, 2026', 'Caching',
       'Кэширование ключей и значений при генерации',
       'https://huggingface.co/docs/transformers/en/kv_cache', 'Документация',
       'Показаны варианты KV-кэша и ограничения отдельных реализаций: динамическое размещение, статический кэш и перенос. Документация помогает проверить, применяется ли простая формула полного кэша к выбранной архитектуре.',
       'Introduction; Cache Types; Offloaded Cache. Выписать поддерживаемый тип для конкретного checkpoint.', 'Вводные работы')
source('paged', 'Kwon, W. и др.', '2023', 'Efficient Memory Management for Large Language Model Serving with PagedAttention',
       'PagedAttention: управление памятью при обслуживании LLM',
       'https://doi.org/10.1145/3600006.3613165', 'SOSP',
       'Работа вводит блочное размещение KV-кэша и показывает, как фрагментация и совместное использование влияют на пропускную способность обслуживания. Логическое число токенов и реально занятая физическая память различаются.',
       '§2 о проблеме памяти; §3 PagedAttention; §4 механизм vLLM и эксперименты.', 'Специализированные работы')
source('accelerate', 'Hugging Face', 'документация, 2026', 'Big Model Inference',
       'Инференс моделей, не помещающихся целиком в ускоритель',
       'https://huggingface.co/docs/accelerate/usage_guides/big_modeling', 'Документация',
       'Разъясняет dispatch весов между GPU, RAM и диском. Такая выгрузка может сделать запуск возможным, но пропускная способность пути передачи меняет практическую скорость.',
       'Big Model Inference и описание device map; различить факт загрузки и измеренную скорость.', 'Вводные работы')
source('llama_quant', 'ggml-org', 'документация, 2026', 'Quantizing models in llama.cpp',
       'Квантование моделей в llama.cpp',
       'https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md', 'Документация и код',
       'Документирует превращение GGUF-файла с весами высокой точности в конкретный тип квантования и способы оценки потерь качества. Обозначение Q4 не определяет в одиночку ни точный размер, ни применимость результата к собственной задаче.',
       'Вводный раздел и таблица типов квантования; сравнить размер двух файлов одного checkpoint и результат на отложенных вопросах.', 'Специализированные работы')
source('fsdp', 'PyTorch', 'документация, 2026', 'Getting Started with Fully Sharded Data Parallel (FSDP2)',
       'Полное шардирование параметров, градиентов и оптимизатора',
       'https://docs.pytorch.org/tutorials/intermediate/FSDP_tutorial.html', 'Документация',
       'Разделяет репликацию модели и шардирование состояний обучения. Описаны коллективные операции, временное восстановление весов и компромисс между памятью и коммуникацией.',
       'Overview; How FSDP2 works; all-gather и reduce-scatter. Схематично изобразить один шаг на двух GPU.', 'Вводные работы')
source('zero', 'Rajbhandari, S. и др.', '2020',
       'ZeRO: Memory Optimizations Toward Training Trillion Parameter Models',
       'ZeRO: уменьшение памяти обучения разделением состояний',
       'https://sc20.supercomputing.org/proceedings/tech_paper/tech_paper_pages/pap379.html', 'SC20',
       'Авторы разбирают память оптимизатора, градиентов и параметров и этапы их разделения между процессами. Выигрыш памяти оплачивается обменом данными и зависит от топологии кластера.',
       '§2 о памяти состояний; §3 этапы ZeRO; проверить, что именно шардируется на каждом этапе.', 'Специализированные работы')
source('qlora', 'Dettmers, T. и др.', '2023', 'QLoRA: Efficient Finetuning of Quantized LLMs',
       'QLoRA: эффективное дообучение квантованных LLM',
       'https://proceedings.neurips.cc/paper_files/paper/2023/hash/1feb87871436031bdc0f2beaa62a049b-Abstract-Conference.html', 'NeurIPS',
       'Замороженная квантованная база сочетается с обучаемыми низкоранговыми адаптерами. Работа объясняет экономию памяти и цену активаций; число параметров адаптера само по себе не определяет весь пик VRAM.',
       '§3 QLoRA, quantization и paged optimizers; §4 эксперименты. Восстановить состав памяти для одного шага.', 'Специализированные работы')
source('nccl', 'NVIDIA', 'документация, 2026', 'NCCL Developer Guide',
       'Коллективные операции NCCL при распределённом обучении',
       'https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/overview.html', 'Документация',
       'Показывает коллективные операции и коммуникационные топологии между GPU. Для multi-GPU конфигурации скорость межсоединения и доступный набор маршрутов важны наряду с суммой VRAM.',
       'Overview и Collective Operations; сравнить all-reduce, all-gather и reduce-scatter для градиентов.', 'Вводные работы')
source('vllm', 'vLLM', 'документация, 2026', 'vLLM Documentation',
       'Сервер инференса vLLM и его планировщик',
       'https://docs.vllm.ai/en/stable/', 'Документация и код',
       'Объединяет планирование запросов, управление KV-памятью и запуск сервера. Конкретные параметры зависят от версии; исходный runtime необходимо фиксировать вместе с измерениями.',
       'Serving и Configuration; проследить вход запроса до выделения KV-блоков и ответа.', 'Вводные работы')
source('benchmark', 'vLLM', 'документация, 2026', 'Benchmark CLI',
       'Измерение времени первого токена и времени между токенами',
       'https://docs.vllm.ai/en/latest/benchmarking/cli/', 'Документация',
       'Документирует параметры генератора нагрузки и метрики TTFT, TPOT, throughput и задержки. Сопоставление машин требует одинаковой модели, распределения длин и интенсивности поступления запросов.',
       'Benchmark Serving и определения метрик; составить команду опыта с воспроизводимыми входными длинами.', 'Вводные работы')
source('distserve', 'Zhong, Y. и др.', '2024',
       'DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving',
       'DistServe: раздельное исполнение prefill и decode',
       'https://www.usenix.org/conference/osdi24/presentation/zhong-yinmin', 'OSDI',
       'Предлагается разместить фазы prefill и decode на разных группах GPU, чтобы уменьшить помехи и отдельно выбирать их параллелизм. Передача KV-состояния тоже имеет цену, поэтому результат зависит от нагрузки и сети.',
       '§2 анализ помех; §3 архитектура; §4 оптимизация размещения и измерения goodput.', 'Фронтир исследований')
source('pgvector', 'pgvector', 'документация, 2026', 'pgvector: Open-source vector similarity search for Postgres',
       'Векторный поиск в PostgreSQL',
       'https://github.com/pgvector/pgvector', 'Документация и код',
       'Описаны точный поиск, HNSW и IVFFlat, типы векторов, индексы и SQL-фильтрация. Выбор индекса отражается на RAM, размере диска, времени построения и качестве поиска.',
       'Exact Search; HNSW; IVFFlat; Filtering. Замерить recall относительно точной выдачи после фильтра.', 'Вводные работы')
source('hnsw', 'Malkov, Y. A.; Yashunin, D. A.', '2016',
       'Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs',
       'HNSW: приближённый поиск по иерархическому графу близости',
       'https://arxiv.org/abs/1603.09320', 'Исследовательская статья',
       'Иерархический граф позволяет быстро находить кандидатов, меняя время и память на достигаемую полноту. Векторный индекс хранит связи между точками помимо самих чисел вектора.',
       '§3 построение и поиск; §4 эксперименты. Сравнить стоимость индекса и recall с точным поиском.', 'Специализированные работы')
source('pitr', 'PostgreSQL Global Development Group', 'документация, 2026',
       'Continuous Archiving and Point-in-Time Recovery (PITR)',
       'Непрерывное архивирование и восстановление базы на момент времени',
       'https://www.postgresql.org/docs/current/continuous-archiving.html', 'Документация',
       'Резервная копия и журнал WAL позволяют восстановить согласованное состояние. Для RAG надо также согласовать версию исходного документа, фрагментов, эмбеддингов и индекса.',
       'Setting Up WAL Archiving; Making a Base Backup; Recovering. Провести пробное восстановление на отдельном узле.', 'Специализированные работы')
source('irbook', 'Manning, C. D.; Raghavan, P.; Schütze, H.', '2008',
       'Introduction to Information Retrieval', 'Введение в информационный поиск',
       'https://nlp.stanford.edu/IR-book/', 'Учебник',
       'Объясняет инвертированные индексы, ранжирование и оценку поиска. Качество RAG начинается с выбора релевантных фрагментов, а не с объёма VRAM генератора.',
       'Главы 1, 6 и 8: индекс, ранжирование и оценка; задать тестовый набор запросов.', 'Вводные работы')
source('llama', 'ggml-org', 'документация, 2026', 'llama.cpp',
       'llama.cpp: локальный запуск и сервер моделей',
       'https://github.com/ggml-org/llama.cpp', 'Документация и код',
       'Проект показывает локальный запуск CPU/GPU, частичную выгрузку слоёв, сервер и параметры контекста. Поддержка backend не гарантирует, что точный checkpoint корректно загрузится или достигнет нужной скорости. Запишите команду, ревизию весов и число фактически выгруженных на GPU слоёв.',
       'README, build instructions и server README; запустить выбранный checkpoint на CPU и GPU, сравнить размещение, первый токен и устойчивую генерацию.', 'Вводные работы')
source('mlx', 'Apple ML Explore', 'документация, 2026', 'MLX',
       'MLX: вычисления на Apple Silicon',
       'https://github.com/ml-explore/mlx', 'Документация и код',
       'Описывает стек для CPU и GPU Apple Silicon с общей памятью и собственным API. Общая память облегчает обмен данными, но приложения и система делят конечную ёмкость; bandwidth и тепловой режим также ограничивают длительную выдачу. Указание поддержки MLX само по себе не проверяет конкретную модель.',
       'README и документация о device/arrays; проверить формат выбранных весов, пик общей памяти и скорость генерации после прогрева.', 'Специализированные работы')
source('rocm', 'AMD', 'документация, 2026', 'ROCm Compatibility Matrix',
       'Матрица совместимости ROCm',
       'https://rocm.docs.amd.com/en/latest/compatibility/compatibility-matrix.html', 'Документация',
       'Матрица сопоставляет конкретные устройства, ОС, версии ROCm и поддерживаемые фреймворки. Проверка только серии GPU оставляет неопределёнными сборку runtime и требуемые операции модели. Сохраните выбранную строку матрицы рядом с протоколом фактического запуска.',
       'GPU, OS and framework support именно своей версии; отметить подтверждённые и неизвестные сочетания до установки стека.', 'Вводные работы')
source('cards', 'Hugging Face', 'документация, 2026', 'Model Cards',
       'Карточки моделей: лицензия, назначение и ограничения',
       'https://huggingface.co/docs/hub/model-cards', 'Документация',
       'Карточка связывает веса с задачей, происхождением, условиями использования и известными ограничениями. Это начало проверки, а не измерение пригодности на собственных документах. Для воспроизводимого запуска отдельно зафиксируйте ревизию checkpoint, tokenizer, шаблон диалога и лицензию.',
       'Overview и metadata; прочитать карточку выбранной ревизии, затем сверить конфигурацию tokenizer и провести задачу на отложенных примерах.', 'Вводные работы')
source('cap', 'NVIDIA', 'документация, 2026', 'CUDA GPU Compute Capability',
       'Вычислительные возможности GPU NVIDIA',
       'https://docs.nvidia.com/cuda/cuda-programming-guide/05-appendices/compute-capabilities.html', 'Документация',
       'Возможности чипа связаны с набором операций и поддержкой численных форматов. Два ускорителя с одинаковой VRAM могут по-разному исполнять нужные ядра. Соответствие чипа таблице ещё не проверяет версии драйвера, сборку приложения и конкретный checkpoint.',
       'Таблицы compute capability и feature support; проверить точную архитектуру GPU, затем подтвердить её пробным запуском нужного runtime.', 'Вводные работы')
source('prof', 'PyTorch', 'документация, 2026', 'PyTorch Profiler',
       'Профилирование вычислений и памяти в PyTorch',
       'https://docs.pytorch.org/tutorials/recipes/recipes/profiler_recipe.html', 'Документация',
       'Профайлер показывает время операций, активность CPU/GPU и часть выделений памяти. Он позволяет проверить гипотезу об узком месте, например сравнить токенизацию с исполнением ядер, но собственные метрики сервера и поиск надо измерять отдельно.',
       'Profiler API и trace; измерить одинаковые запросы после прогрева, сопоставить CPU с GPU, затем добавить серверные TTFT и p95.', 'Вводные работы')
source('memory', 'PyTorch', 'документация, 2026', 'Understanding CUDA Memory Usage',
       'Понимание расхода памяти CUDA',
       'https://docs.pytorch.org/docs/stable/torch_cuda_memory', 'Документация',
       'Snapshot и статистика allocator позволяют отделить память активных тензоров, резерв и пик во времени. Это помогает понять, почему нижняя оценка весов и KV не равна занятой VRAM. Аллокации вне видимости PyTorch надо учитывать иными средствами.',
       'Recording memory history и Visualizing snapshots; отметить, какие расходы инструмент не видит, и сравнить пик с расчётом главы.', 'Вводные работы')
source('mlperf', 'MLCommons', 'документация, 2026', 'MLPerf Inference',
       'MLPerf Inference: сценарии и сопоставимые измерения',
       'https://mlcommons.org/benchmarks/inference-datacenter/', 'Бенчмарк и правила',
       'Набор задаёт сценарии, пороги точности и правила сравнения систем. Публичная цифра throughput полезна как внешний ориентир только после сверки модели, входных данных, ограничений задержки и настроек. Для закупки по документному RAG нужен собственный поток запросов и проверка качества ссылок.',
       'Scenarios, rules and results; выписать несовпадения со своей нагрузкой и разработать парный опыт на точном checkpoint.', 'Специализированные работы')
