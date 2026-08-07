# Public Distribution & Search Optimization Guide

This guide defines how cases investigated in the **Pasynkov Debugging Cookbook** should be published and syndicated across public platforms to maximize search engine indexability (Google, DuckDuckGo) and retrieval for AI agents (RAG, LLM pre-training corpora).

---

## 1. Core Principle: Search Fingerprints over Generic Titles

Knowledge is only useful if it can be retrieved when the failure reoccurs months or years later. A title such as *"Fix quick settings panel bug"* is impossible to find via search.

Every case title, headline, and article summary **must** include **Search Fingerprints**:
- **Exact Numeric Constants**: e.g., `4294967296`, `uint32(-1)`, exit code `137`.
- **Exact Error Messages & Log Tokens**: e.g., `Object DockAppIcon already disposed`, `status=4294967040`.
- **API & Type Names**: e.g., `St.BoxLayout`, `St.ScrollView`, `get_preferred_height`, `Clutter.Actor`.
- **Observable Mechanical Symptoms**: e.g., `collapses St.ScrollView to 1px`, `empty AppFavorites on startup`.

### Good vs. Bad Titles

| Bad Title | Search-Optimized Title (With Fingerprints) |
|---|---|
| Panel scroll view invisible bug | GNOME Shell St.BoxLayout returns invalid natural height 4294967296 and collapses St.ScrollView to 1px |
| Menu closes randomly | Context menu switches to adjacent items on hover due to shared PopupMenuManager |
| Extension preferences error | Extension preferences window fails to open or raises GDBus.Error.ServiceUnknown |

---

## 2. Multi-Platform Syndication Matrix

To ensure maximum reach without duplicate content penalties or fragmentation, follow this syndication matrix:

```
                  ┌───────────────────────────────────────────────┐
                  │    Canonical Home: Personal Site + GitHub     │
                  │ fedor-pasynkov.ru/blog/<case-slug>            │
                  │ github.com/.../cases/<stack>/<symptom-slug>/  │
                  └───────────────────────┬───────────────────────┘
                                          │
    ┌───────────────────┬─────────────────┼─────────────────┬───────────────────┐
    ▼                   ▼                 ▼                 ▼                   ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌───────────────────┐
│     Habr     │ │ DEV Community│ │Stack Overflow│ │GNOME Discourse│ │   Reddit / Social │
│  (RU Story)  │ │ (EN Article) │ │  (Q&A Pair)  │ │ (API Report) │ │ (Short Announcement)│
│  Narrative   │ │canonical_url │ │ Self-Answer  │ │ Minimal Repro│ │  With Log Snippet │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └───────────────────┘
```

### Platform-Specific Protocols

#### 1. Canonical Origin (Personal Website & GitHub)
- **Role**: Authoritative single source of truth containing raw logs, `case.yml` metadata, minimal reproductions in `reproduction/`, broken/fixed code diffs, and verification scripts.
- **URL Structure**: `https://fedor-pasynkov.ru/blog/<case-slug>` and GitHub repo `cases/<stack>/<symptom-slug>/`.

#### 2. Habr (Russian Language Narrative)
- **Format**: Detailed engineering narrative.
- **Structure**:
  1. *Symptom*: What was observed (e.g. 1px height, missing icons).
  2. *False Hypotheses*: Failed approaches and why they broke adjacent functionality.
  3. *Diagnostic Path*: Traversing the Clutter actor tree and logging `get_preferred_height()`.
  4. *Root Cause Analysis*: Explaining `uint32(-1)` sentinel overflow in container allocation.
  5. *Fix & Regression Protection*: Minimal code change and verification procedure.

#### 3. DEV.to / Medium / Hashnode (English Articles)
- **Format**: Full technical breakdown in English.
- **Requirement**: Always set the `canonical_url` header to point directly to the personal site canonical post (`canonical_url: https://fedor-pasynkov.ru/blog/...`).

#### 4. Stack Overflow / Stack Overflow на русском (Targeted Q&A)
- **Format**: Concise Question with Self-Answer (encouraged by SO for documenting solutions).
- **Question**: State the exact error message, versions, minimal actor layout, and log output.
- **Answer**: Provide the root cause explanation, minimal code fix, and a reference link to the full canonical investigation.

#### 5. Upstream Community (GNOME Discourse / GitLab)
- **GNOME Discourse**: Post technical inquiries for GNOME/GJS developers to discuss underlying Clutter/St layout contracts.
- **GNOME GitLab**: Open an upstream issue only when a minimal reproduction reproduces on currently supported GNOME releases (last 2 stable releases or main).

#### 6. Social & Community Aggregators (Reddit `r/gnome`, Linux forums)
- **Format**: Short text post summarizing the problem and root cause with key diagnostic snippets. Avoid raw link spamming; provide self-contained value in the post body.

---

## 3. Case Structure Checklist for Public Publishing

When preparing a case for publication:

1. [ ] **Title**: Contains exact API symbols, error strings, and numeric constants.
2. [ ] **Symptoms**: Lists raw terminal logs or measurable geometry values.
3. [ ] **Minimal Reproduction**: Contains a standalone runnable project isolated from production code.
4. [ ] **Root Cause**: Pinpoints the exact mechanism (e.g., unsigned integer wrap, race condition).
5. [ ] **Failed Approaches**: Explains why obvious workarounds failed or caused side effects.
6. [ ] **Verification**: Provides automated commands (`verify.sh`) or reproducible manual steps.
7. [ ] **Canonical Link**: Cross-posted versions point to the primary source.

---

## 4. Complete Habr Publishing Master Workflow (Полный воркфлоу настройки публикации на Хабре)

When publishing a technical case investigation from **Pasynkov Debugging Cookbook** on Habr, follow this field-by-field reference for the modal form:

---

### Step-by-Step Field Reference (Каждое поле формы по шагам)

#### 1. \* Тип публикации
- **Выбор**: `Статья`
- **Описание**: Первичный формат для инженерных расследований, кейсов, обзоров и туториалов.

#### 2. \* Язык публикации
- **Выбор**: `Русский` (для русскоязычной версии) или `Английский` (если пишете на английском).

#### 3. \* Целевая аудитория (Выберите 1 категорию)
Map your case to the exact Habr audience taxonomy:
- **`Разработка и инженерия`**:
  - `Фронтенд` — *(Default for GUI, Web UI, GJS, Clutter, St, React, Vue, Flutter UI)*
  - `Бэкенд` — *(Python, C/C++, Rust, Go, Node.js, Databases, Microservices)*
  - `Мобильная разработка` — *(Android, iOS, Flutter, React Native)*
  - `Геймдев` — *(Graphics, Game Engines, Rendering)*
  - `Тестирование` — *(QA, Verification scripts, Automated testing)*
  - `AI и ML` — *(Machine Learning, AI Agents)*
  - `Промышленная инженерия`
- **`Инфраструктура и данные`**:
  - `Системное администрирование` — *(Linux kernel, Systemd, Wayland, Mutter, K8s, Docker)*
  - `Информационная безопасность` — *(Vulnerabilities, Audits, Memory safety)*
  - `Системный и бизнес-анализ`
  - `Техническая поддержка`
- **`Управление`**: `Менеджмент`, `Топ-менеджмент`, `HR`
- **`Креатив и продвижение`**: `Дизайн`, `Маркетинг и контент`
- **`Наука и жизнь`**: `Железо и гаджеты`, `DIY`, `Научпоп`, `Здоровье`
- **`Другое`**

#### 4. \* Хабы (Выберите от 1 до 5 хабов)
Match hubs to the case tech stack:
- **Рекомендуемые хабы для отладки**: `Отладка`, `Качество кода`, `Ненормальное программирование`, `Проектирование и рефакторинг`, `Bug hunters`
- **Рекомендуемые хабы для Linux/C/GJS**: `Linux`, `*nix`, `Настройка Linux`, `Графические оболочки`, `Оболочки`, `GTK+`, `Системное программирование`, `C`, `C++`, `JavaScript`, `Интерфейсы`, `Веб-разработка`

<details>
<summary><b>Показать полный список всех хабов Хабра (нажмите для разворачивания)</b></summary>

- **A–Z**: `$mol`, `*nix`, `.NET`, `1С`, `1С-Битрикс`, `3D-графика`, `3D-принтеры`, `Accessibility`, `Action Script`, `Adobe Flash`, `Agile`, `Ajax`, `Amazon Web Services`, `Android`, `Angular`, `Apache`, `Apache Flex`, `AR и VR`, `Arduino`, `ASP`, `Assembler`, `Asterisk`, `Atlassian`, `Bada`, `Big Data`, `Brainfuck`, `Bug hunters`, `C`, `C#`, `C++`, `CAD/CAM`, `CakePHP`, `Canvas`, `CGI (графика)`, `Cisco`, `Clojure`, `CMS`, `Cobol`, `Cocoa`, `CodeIgniter`, `CoffeeScript`, `Creative Commons`, `CRM-системы`, `CSS`, `CTF`, `Cubrid`, `D`, `Dart`, `Data Engineering`, `Data Mining`, `Delphi`, `Derby.js`, `Developer Relations`, `DevOps`, `DIY или Сделай сам`, `Django`, `DNS`, `Doctrine ORM`, `Drupal`, `Eclipse`, `ECM/СЭД`, `Elixir/Phoenix`, `Elm`, `Emacs`, `Email-маркетинг`, `Ember.js`, `Erlang/OTP`, `ERP-системы`, `F#`, `Facebook API`, `Fidonet`, `Firebird/Interbase`, `Firefox`, `Flask`, `Flutter`, `Forth`, `Fortran`, `FPGA`, `Git`, `GitHub`, `Go`, `Godot`, `Google API`, `Google App Engine`, `Google Chrome`, `Google Cloud Platform`, `Google Cloud Vision API`, `Google Web Toolkit`, `Google Таблицы`, `GPGPU`, `Gradle`, `GreaseMonkey`, `Groovy & Grails`, `Growth Hacking`, `GTD`, `GTK+`, `Habr`, `Hadoop`, `Haskell`, `Haxe`, `Help Desk Software`, `HTML`, `htmx`, `I2P`, `IIS`, `INFOLUST`, `Internet Explorer`, `iOS`, `IPFS`, `IPTV`, `IPv6`, `IT-инфраструктура`, `IT-компании`, `IT-стандарты`, `IT-эмиграция`, `Java`, `Java ME`, `JavaScript`, `Jetpack Compose`, `Joomla`, `jQuery`, `Julia`, `Kohana`, `Kotlin`, `Kubernetes`, `LabVIEW`, `Laravel`, `LaTeX`, `Linux`, `Lisp`, `LiveStreet`, `Lua`, `macOS`, `Magento`, `Maps API`, `Matlab`, `Mercurial`, `Mesh-сети`, `Meteor.JS`, `Microsoft Access`, `Microsoft Azure`, `Microsoft Edge`, `Microsoft Excel`, `Microsoft SQL Server`, `MODX`, `MongoDB`, `Mono и Moonlight`, `MooTools`, `MySQL`, `Natural Language Processing`, `NestJS`, `Nginx`, `Node.JS`, `NoSQL`, `Nx`, `Objective C`, `Office 365`, `Open source`, `Openshift`, `OpenStreetMap`, `Opera`, `Oracle`, `PDF`, `Perl`, `Phalcon`, `PHP`, `PostgreSQL`, `PowerShell`, `Processing`, `Prolog`, `Puppet`, `Python`, `Qt`, `R`, `Raspberry Pi`, `React Native`, `ReactJS`, `Ruby`, `Ruby on Rails`, `Rust`, `SaaS / S+S`, `Safari`, `Sailfish OS`, `SAN`, `SCADA`, `Scala`, `Serverless`, `Service Desk`, `SharePoint`, `Silverlight`, `Small Basic`, `Smalltalk`, `Solidity`, `Sphinx`, `SQL`, `SQLite`, `SvelteJS`, `Swift`, `Symfony`, `Tarantool`, `TDD`, `TensorFlow`, `Tizen`, `Twisted`, `TypeScript`, `TYPO3`, `UEFI`, `UML Design`, `Unity`, `Unreal Engine`, `Usability`, `VIM`, `Visual Basic for Applications`, `Visual Studio`, `VK API`, `VueJS`, `WebAssembly`, `WebGL`, `Wiki-проекты`, `Windows`, `Windows Phone`, `WordPress`, `X API`, `Xamarin`, `Xcode`, `XML`, `XSLT`, `Yii`, `Zend Framework`, `Zig`
- **А–Я**: `Автомобильные гаджеты`, `Алгоритмы`, `Анализ и проектирование систем`, `Аналитика мобильных приложений`, `Антивирусная защита`, `Астрономия`, `Базы данных`, `Беспроводные технологии`, `Библиотека ExtJS/Sencha`, `Бизнес-модели`, `Биллинговые системы`, `Биографии гиков`, `Биология`, `Биотехнологии`, `Браузеры`, `Брендинг`, `Будущее здесь`, `Веб-аналитика`, `Веб-дизайн`, `Веб-разработка`, `Векторная графика`, `Венчурные инвестиции`, `Верстка писем`, `Видеокарты`, `Видеоконференцсвязь`, `Видеотехника`, `Визуализация данных`, `Визуальное программирование`, `Виртуализация`, `Восстановление данных`, `Высоконагруженные системы`, `Гаджеты`, `Геоинформационные сервисы`, `Говнокод`, `Голосовые интерфейсы`, `Графические оболочки`, `Графический дизайн`, `Демосцена`, `Децентрализованные сети`, `Дизайн`, `Дизайн игр`, `Дизайн мобильных приложений`, `Доменные имена`, `Законодательство в IT`, `Занимательные задачки`, `Звук`, `Здоровье`, `Игры и игровые консоли`, `Изучение языков`, `Иконки`, `Инженерные системы`, `Интервью`, `Интернет вещей`, `Интернет-маркетинг`, `Интерфейсы`, `Инфографика`, `Информационная безопасность`, `Искусственный интеллект`, `Исследования и прогнозы в IT`, `История IT`, `Карьера в IT-индустрии`, `Качество кода`, `Квантовые технологии`, `Киберпанк`, `Киберспорт`, `Клиентская оптимизация`, `Компиляторы`, `Компьютерная анимация`, `Компьютерное железо`, `Контекстная реклама`, `Контент и копирайтинг`, `Конференции`, `Копирайт`, `Космонавтика`, `Краудсорсинг`, `Криптовалюты`, `Криптография`, `Лазеры`, `Лайфхаки для гиков`, `Логические игры`, `Локализация продуктов`, `Любительская радиосвязь`, `Математика`, `Машинное обучение`, `Медгаджеты`, `Медийная реклама`, `Мессенджеры`, `Микросервисы`, `Микроформаты`, `Мозг`, `Монетизация IT-систем`, `Монетизация веб-сервисов`, `Монетизация игр`, `Монетизация мобильных приложений`, `Мониторы и ТВ`, `Мультикоптеры`, `Накопители`, `Нанотехнологии`, `Настольные компьютеры`, `Настройка Linux`, `Научная фантастика`, `Научно-популярное`, `Ненормальное программирование`, `Носимая электроника`, `Ноутбуки`, `Облачные вычисления`, `Облачные сервисы`, `Оболочки`, `Обработка изображений`, `Образование за рубежом`, `ООП`, `Операционные системы`, `Открытые данные`, `Отладка`, `Офисы IT-компаний`, `Параллельное программирование`, `Патентование`, `Периферия`, `Планшеты`, `Платежные системы`, `Повышение конверсии`, `Подготовка технической документации`, `Поисковая оптимизация`, `Поисковые технологии`, `Презентации`, `Программирование`, `Программирование микроконтроллеров`, `Продвижение игр`, `Проектирование API`, `Проектирование и рефакторинг`, `Производство и разработка электроники`, `Промышленное программирование`, `Прототипирование`, `Профессиональная литература`, `Процессоры`, `Работа с видео`, `Развитие стартапа`, `Разработка игр`, `Разработка мобильных приложений`, `Разработка под e-commerce`, `Разработка публичных облаков`, `Распределённые системы`, `Расширения для браузеров`, `Реверс-инжиниринг`, `Регулярные выражения`, `Резервное копирование`, `Робототехника`, `Семантические сети`, `Серверная оптимизация`, `Серверное администрирование`, `Сетевое оборудование`, `Сетевые технологии`, `Сжатие данных`, `Системное администрирование`, `Системное программирование`, `Системы сборки`, `Системы связи`, `Системы управления версиями`, `Смартфоны`, `Сотовая связь`, `Софт`, `Социальные сети`, `Спам и антиспам`, `Спортивное программирование`, `Спутниковые системы навигации`, `Стандарты связи`, `Старое железо`, `Статистика в IT`, `Суперкомпьютеры`, `Схемотехника`, `Текстовые редакторы и IDE`, `Телемедицина`, `Терминология IT`, `Тестирование IT-систем`, `Тестирование веб-сервисов`, `Тестирование игр`, `Тестирование мобильных приложений`, `Типографика`, `Транспорт`, `Удалённая работа`, `Умный дом`, `Управление e-commerce`, `Управление медиа`, `Управление персоналом`, `Управление продажами`, `Управление продуктом`, `Управление проектами`, `Управление разработкой`, `Управление сообществом`, `Урбанизм`, `Учебный процесс в IT`, `Физика`, `Финансы в IT`, `Фототехника`, `Фриланс`, `Функциональное программирование`, `Хакатоны`, `Химия`, `Хостинг`, `Хранение данных`, `Читальный зал`, `Экология`, `Электроника для начинающих`, `Энергия и элементы питания`, `Яндекс API`

</details>

#### 5. \* Ключевые слова (Обязательное поле)
- **Правило**: Введите от 1 до 10 точных ключевых слов через запятую.
- **Содержание**: Имена API (`St.BoxLayout`), точности типов (`uint32`), константы ошибок (`4294967296`), имя фреймворка (`GNOME Shell`, `GJS`, `Clutter`), стек (`Linux`, `C`).

#### 6. Форматы публикаций
- **Выбор**: `Кейс` (для разбора реального бага из практики) или `Туториал` (для пошаговых гайдов).

#### 7. Переведённый материал
- **Чекбокс**: Снимите галочку (наши кейсы являются оригинальными авторскими расследованиями).

#### 8. Уровень сложности
- **`Простой`**: Без тяжелого кода, пошаговые туториалы, истории.
- **`Средний`**: Техническая практика, работа с окружением.
- **`Сложный`** *(Рекомендуется для большинства кейсов)*: Низкоуровневая отладка, C/C++ выкладки, переполнение типов, алгоритмика.

#### 9. Отображение публикации в ленте
- **Обложка (780×440px)**: Загрузите PNG/JPG/WebP файл 780×440.
- **Анонс / Лид в ленту (100–3000 символов)**: Скопируйте вводный блок (от начала статьи до первого раздела), чтобы завлечь читателя в ленте.

#### 10. \* Текст кнопки «Читать далее»
- **Значение**: `Читать далее` (по умолчанию) или кастомное `Разобрать баг` (до 30 символов).

---

### Official Habr Author Rules & Formatting Guidelines

1. **Изображения**: Иллюстрации в статье загружайте строго на **Habrastorage** (не используйте посторонние хостинги).
2. **Формулы (MathJax / LaTeX)**: Для формул используйте LaTeX через кнопку `Σ` (строчная формула внутри абзаца или блочная с новой строки).
3. **Лимит публикаций**: Не более 3 публикаций за 24 часа.
4. **Запрет рекламы и кликбейта**: Не используйте реферальные ссылки, кликбейтные заголовки или рекламу.

#### Habr Author Codex (Кодекс авторов Хабра — http://habr.com/ru/docs/authors/codex/)

<details>
<summary><b>Показать Кодекс авторов Хабра (нажмите для разворачивания)</b></summary>

- Я создаю авторские материалы и не перепечатываю с других сайтов.
- Публикуя материалы других авторов, я всегда привожу ссылки на источники.
- Я не создаю глупых комментариев типа «+1», «ф топку», «афтар жжот».
- Я не матерюсь и не оскорбляю других на страницах Хабра.
- Я стараюсь, чтобы в моих текстах не было ошибок.
- Я уважаю администрацию и пользователей ресурса, не унижаю и не оскорбляю их — я здесь не для этого.
- В споре я стараюсь не раздувать конфликт, а решить проблему в личной переписке.
- Если мне не удалось разрешить конфликт, я не призываю других к активному противодействию.
- Я лично решаю: публиковать контент на Хабре или нет, и не требую за это денег.
- Если нужно, я помогаю новичкам.
- Я пользуюсь поиском, чтобы уточнить, нет ли уже на сайте похожего материала. Если так вышло, я дополню его в комментариях.
- Каждым своим действием на ресурсе я стремлюсь добавить порядка, а не внести хаоса.
- Своими действиями я не хочу разрушить или дискредитировать сообщество.
- Я не клянчу карму и отношусь к изменениям рейтинга спокойно.
- Я стараюсь учесть конструктивную критику и пожелания.
- Я на позитиве. Из самой сложной ситуации всегда есть выход.
- Я понимаю, что Хабр — это сообщество людей с разными интересами. Если какая-то тема мне не интересна, я не мешаю другим ее обсуждать.

</details>

---

### Example Habr Teaser (Анонс для ленты)

```text
Представьте ситуацию: вы пишете расширение или компонент интерфейса для рабочей среды GNOME Shell на JavaScript (GJS). Код выполняется без единой ошибки в консоли, все объекты успешно создаются, иконки инстанциируются, но на экране… абсолютная пустота.

Вы начинаете дампать геометрию контейнера в лог и видите странную картину:
appsScroll=1, appsBox=1, status=4294967040

Контейнер St.ScrollView внезапно схлопнулся до высоты 1px, превратив ваш интерфейс в невидимую нитку. При этом его дочерний элемент утверждает, что его естественная высота равна 4 294 967 296 пикселям!

В этой статье мы разберем детективную историю отладки этого бага: от рекурсивного дампа дерева акторов Clutter до анализа точности чисел gfloat и каста типов на границе 2^32.
```

---

## 5. Technical Investigation & Article Workflow (Официальный регламент отладочных статей)

При составлении статей по материалам кейсов AI-агенты и авторы обязаны строго соблюдать этот 8-этапный регламент расследования:

### 1. Фиксация сырых доказательств (Raw Evidence First)
До любых теоретических объяснений фиксируются:
- Точные версии ОС, системного окружения, графического сервера, рантайма и зависимостей;
- Минимальный реальный код, вызывающий сбой;
- Неотредактированный лог вывода консоли / `journalctl`;
- Состояние системы до и после исправления;
- Скрипты и команды запуска.

### 2. Четыре уровня уверенности (Confidence Levels Matrix)
Каждое утверждение в тексте статьи должно быть строго классифицировано:
```text
- OBSERVED: реально увидели в логах или консоли
- REPRODUCED: стабильно воспроизвели в изолированном окружении
- INFERRED: логический вывод на основе подтверждённых фактов
- HYPOTHESIS: рабочая гипотеза или потенциальное объяснение
- UNKNOWN: открытый вопрос или локация, не доказанная на 100%
```

### 3. Требование доказательств для причинно-следственных связей
На любое утверждение типа «X произошло из-за Y» отвечать на вопрос *«Откуда я это знаю?»*:
- **Допустимо**: Ссылка на строку Си-кода, стектрейс отладчика (`gdb`), микро-эксперимент с изменением 1 переменной, официальная документация API.
- **Недопустимо**: «Звучит логично», «ИИ так сказал», «После изменения заработало (значит это была причина)».

### 4. Честный Minimal Reproducer vs Illustrative Example
- Если код запускается, использует системный рантайм, воспроизводит симптом и проверяется — помечать как `Minimal reproduction`.
- Если код показывает лишь структуру акторов/контейнеров без запуска приложения — помечать как `Illustrative layout structure`.

### 5. Изолированная проверка кода статьи
Перед публикацией код из статьи извлекается в отдельную директорию и выполняется в сухой среде. Код в статье должен соответствовать файлам в репозитории на 100%.

### 6. Арифметика типов и градиенты чисел
Для нетипичных чисел (например, $4294967296$, $4294967040$, $4294967295$) составляется явная матрица представлений (unsigned int vs float32/gfloat precision step). Цепочки преобразований не публикуются без доказательства каждого каста.

### 7. Злой рецензент (Aggressive Technical Peer-Review)
Перед финальной публикацией запускается критик с промптом:
> *"Проведи агрессивное техническое ревью статьи. Для каждого утверждения укажи: подтверждено ли оно фактами, существует ли API, сходится ли арифметика типов, воспроизводит ли пример симптом, не выдам ли факт за доказанную первопричину."*

### 8. Безопасная структура статьи
```text
1. Symptom (Симптом и наблюдаемый сбой)
2. Environment (Точные версии окружения)
3. Raw evidence (Сырые логи и улики)
4. Minimal reproduction / Illustrative structure
5. Experiments (Проведенные опыты)
6. Failed approaches (Опровергнутые гипотезы)
7. Confirmed findings (Подтверждённые наблюдения)
8. Working hypothesis (Рабочая гипотеза)
9. Practical fix & Workarounds (Практический фикс)
10. Remaining unknowns (Открытые вопросы)
11. Verification (Проверка и верификация)
```
Раздел `Root Cause` пишется только тогда, когда первопричина полностью доказана.

---

### Практический чек-лист составления первого черновика (Порядок 6 ➔ 1):

Пишите материал строго в порядке **от 6 к 1 (Bottom-Up)**:

1. **[6] Сначала — лог изнутри реального прохода (Passive Logging)**:
   Логируйте методы изнутри живого цикла выполнения системы до и после единственного изменения. Не используйте ручной внешний вызов как доказательство.
2. **[5] Точная инженерная терминология**:
   Не используйте эмоциональные термины вроде «конфликт флагов», если реальный механизм — незамкнутый запрос (`for_width = -1`). Заменяйте на точные формулировки («unresolved», «triggers», «exposes unhandled edge-case»).
3. **[4] Исключение неработающих декораций**:
   Любое красивое число или факт либо наглядно участвует в цепочке до/после, либо убирается из текста.
4. **[3] Единая причинно-следственная цепочка**:
   Показывайтеbefore/after одного и того же показателя (`forWidth: -1 ➔ 280`, `natH: 4294967296 ➔ 340px`, `allocH: 1 ➔ 600px`).
5. **[2] Подтверждение логом перед утверждением «почему»**:
   Если объяснение можно заменить на слово «предположительно» без потери смысла — это ещё не доказанная причина, дособерите лог.
6. **[1] Заголовок и рамка статьи — в самом конце**:
   Формулируйте заголовок в последнюю очередь, под уже полученное и доказанное экспериментальное решение. Заголовок должен обещать ровно то, что подтверждено.

---

### Правила точности утверждений (Правила 7–12):

Дополняют порядок 6 ➔ 1 — применяются при написании и ревью любого технического материала в репозитории.

**[7] Любой тип, маршалинг, API-контракт — сначала в официальную документацию, потом в текст.**
Если пишешь «функция принимает/возвращает тип X», найди declaration в официальных доках до того, как формулируешь гипотезу вокруг этого типа. Пример: «GJS → guint» звучало правдоподобно — оказалось `gfloat*`. Гипотеза вокруг `guint` пережила два раунда правок.

**[8] Формулируй причинность на уровне уверенности, который реально есть — и не выше.**
«X causes Y» (общее правило) ≠ «in this specific hierarchy, X preceded Y» (наблюдение). Слово-маркер: если можешь написать «may vary depending on...» без потери смысла — пиши именно так, а не «always» / «causes». Это касается и `align causes -1`, и `expand makes Clutter pass width`, и `guint marshaling`.

**[9] Читай граничные условия API буквально — не по интуиции.**
`for_width < 0` ≠ `for_width <= 0`. Документация говорит «a negative value» — ноль является формально валидной шириной. Off-by-one-по-смыслу в guard-условиях пролезают незаметно, потому что код выглядит рабочим. Для любого числового condition в фиксе — сверяйся с точной формулировкой контракта.

**[10] Не читай производные значения состояния из объекта, у которого состояние может быть ещё не установлено.**
`parent.get_width()` до allocation — источник скрытого preferred-size цикла. Если объект появляется в контексте «ещё не allocated / не realized / не mapped», не используй его производные значения как fallback — бери intrinsic/собственные данные компонента.

**[11] Каждая переменная в блоке вывода/лога — либо объяснена, либо убрана. Без исключений.**
`status=4294967040` провисела восемь итераций именно потому, что казалась «второстепенной деталью». Правило: перед публикацией пройдись по каждому токену в блоках вывода и спроси «откуда это число и что оно доказывает» — если ответа нет, убирай.

**[12] Если пример кода использует stdlib/framework-класс, проверь requirements к использованию, а не только API методов.**
`St.ScrollView` ожидает child, реализующий `StScrollable` — это не всплывает при синтаксическом ревью, потому что код «выглядит» правильным. Для любого внешнего класса в примере — быстрая сверка с одним абзацем документации про requirements к использованию.

---

**Суммарный принцип всех двенадцати правил:**
> Каждое число, тип и причинная связь в тексте должны иметь источник — либо собственный эксперимент с логом изнутри реального прохода, либо официальная документация. Если источника нет, это либо не идёт в текст, либо идёт с явным disclaimer.


