# Stack Overflow Ready-to-Paste Materials

Ниже приведены чистые тексты вопросов и ответов для англоязычной и русской версий Stack Overflow.

================================================================================
1. STACK OVERFLOW (ENGLISH)
================================================================================

--- QUESTION TITLE ---
Debugging a GNOME Shell layout collapse: how a 4,294,967,296 px preferred height collapsed St.ScrollView to 1 px

--- QUESTION TAGS ---
gnome-shell gjs clutter javascript c

--- QUESTION BODY ---
When developing a custom GNOME Shell extension / UI component in GJS (JavaScript), a custom grid widget inside an `St.ScrollView` within a vertical `St.BoxLayout` collapses to a height of 1px and becomes invisible on screen.

Inspect actor geometry via debug logs:

    appsScroll=1
    appsBox=1
    status=4294967040

Traverse the Clutter actor tree and log preferred heights:

```javascript
function inspectActorTree(actor, depth = 0) {
    // In get_preferred_height(-1), -1 represents an unconstrained width query (for_width = -1)
    let [minH, natH] = actor.get_preferred_height(-1);
    let alloc = actor.get_allocation_box();
    let name = actor.get_name() || actor.constructor.name;
    console.log(`${' '.repeat(depth * 2)}${name}: minH=${minH}, natH=${natH}, allocH=${alloc.get_height()}`);
    actor.get_children().forEach(child => inspectActorTree(child, depth + 1));
}
```

Output:

    StBoxLayout (parent): minH=0, natH=4294967296, allocH=600
      StScrollView: minH=1, natH=4294967296, allocH=1
        ChildGridActor: minH=0, natH=4294967296, allocH=0

`ChildGridActor` reports `naturalHeight = 4294967296`, causing `St.ScrollView` to allocate 1px height.

Why do these values near 2^32 appear in Clutter layout calculations, and how can this container collapse be resolved cleanly without breaking container responsiveness?

--- SELF-ANSWER BODY ---
### Working Hypothesis & Evidence

The observed failure is caused by an unconstrained preferred size query near the 2^32 boundary.

#### 1. Input Parameter `-1` (`for_width`)
In `get_preferred_height(-1)`, `-1` is the `for_width` input parameter representing an unconstrained query (`clutter_actor_get_preferred_height`). An unconstrained or invalid preferred size entered layout calculations when intermediate containers lacked explicit minimum dimensions or had conflicting alignment flags (`x_align`/`y_align`).

#### 2. Floating-Point (`gfloat`) Precision at 2^32
In Clutter (`clutter/clutter-box-layout.c`), layout size calculations use `gfloat` (32-bit IEEE 754 float). Near 2^32, float32 precision step is 256:
* 2^32 = 4,294,967,296
* 2^32 - 256 = 4,294,967,040

The values logged (4,294,967,296 and 4,294,967,040) match representable `gfloat` numbers near the 2^32 limit.

#### 3. Container Allocation Fallback
When vertical `ClutterBoxLayout` sums natural heights across siblings, an astronomical request of **4 billion pixels** (2^32 px) forces layout allocation to fail. A safety fallback triggers, allocating `St.ScrollView` its minimum baseline requirement — **1px**.

---

### Solution

1. **Diagnostic Workaround**: To verify size constraint sensitivity during debugging:
   ```javascript
   grid.set_size(200, 300); // Diagnostic check
   ```

2. **Adaptive Production Solution**:
   - Establish a single geometry owner (manage sizing in JS via Clutter actor flags).
   - Remove conflicting `x_align` and `y_align` parameters on intermediate child wrappers.
   - Use `x_expand: true` and `y_expand: true` so the parent layout manager handles dynamic resizing.

```diff
- const grid = new St.Widget({ 
-     x_align: Clutter.ActorAlign.CENTER, 
-     y_align: Clutter.ActorAlign.FILL 
- });
- grid.queue_relayout();

+ const grid = new St.Widget({
+     style_class: 'app-grid',
+     x_expand: true,
+     y_expand: true,
+ });
```

For full investigation logs and test scripts, see the [Pasynkov Debugging Cookbook case investigation](https://github.com/pefbrute/pasynkov-debugging-cookbook/tree/main/cases/gnome-shell/st-boxlayout-invalid-natural-height).


================================================================================
2. STACK OVERFLOW НА РУССКОМ
================================================================================

--- ЗАГОЛОВОК ВОПРОСА ---
Расследование бага GNOME Shell: как естественная высота 4294967296 px схлопнула St.ScrollView до 1 px

--- МЕТКИ ВОПРОСА ---
gnome-shell gjs clutter javascript c

--- ТЕКСТ ВОПРОСА ---
При разработке расширения для GNOME Shell на GJS (JavaScript) виджет сетки внутри `St.ScrollView` в вертикальном `St.BoxLayout` неожиданно схлопывается до высоты 1px и становится невидимым.

В логах отладки геометрия акторов выглядит так:

    appsScroll=1
    appsBox=1
    status=4294967040

Вызов `get_preferred_height(-1)` при дампе дерева акторов выдает:

    StBoxLayout (parent): minH=0, natH=4294967296, allocH=600
      StScrollView: minH=1, natH=4294967296, allocH=1
        ChildGridActor: minH=0, natH=4294967296, allocH=0

Почему появляются естественные высоты `4294967296` и `4294967040` и как правильно исправить схлопывание контейнера?

--- ТЕКСТ САМООТВЕТА ---
### Рабочая гипотеза и математические улики

Сбой вызван незамкнутым запросом предпочтительного размера вблизи границы 2^32.

1. **Параметр `-1` (for_width)**: Значение `-1` в `get_preferred_height(-1)` указывает на запрос незамкнутой ширины (`for_width = -1`). В расчёт попало сентинельное или незаданное значение при отсутствии `min-height` и конфликте флагов выравнивания.
2. **Точность `gfloat` при 2^32**: В C-коде Clutter (`clutter/clutter-box-layout.c`) размеры обрабатываются через `gfloat` (IEEE 754 float32). Возле 2^32 шаг дискретности float32 равен 256:
   - 2^32 = 4 294 967 296
   - 2^32 - 256 = 4 294 967 040
   Числа из логов (4 294 967 296 и 4 294 967 040) совпадают с представимыми `gfloat` значениями на границе 2^32.
3. **Фоллбек компоновки**: При расчете вертикального `ClutterBoxLayout` запрос на 4 миллиарда пикселей приводит к невозможности пропорционального распределения, и контейнер сбрасывается в минимум **1px**.

---

### Решение

1. **Диагностический костыль**: Для проверки гипотезы при отладке:
   ```javascript
   grid.set_size(200, 300);
   ```

2. **Адаптивный производственный фикс**:
   - Задавайте `x_expand: true` и `y_expand: true`.
   - Уберите конфликтующие `x_align` / `y_align` с промежуточных контейнеров.
   - Соблюдайте правило единого хозяина геометрии.

```diff
- const grid = new St.Widget({ 
-     x_align: Clutter.ActorAlign.CENTER, 
-     y_align: Clutter.ActorAlign.FILL 
- });
- grid.queue_relayout();

+ const grid = new St.Widget({
+     style_class: 'app-grid',
+     x_expand: true,
+     y_expand: true,
+ });
```

Подробный детективный разбор и репозиторий проекта доступны в [Pasynkov Debugging Cookbook](https://github.com/pefbrute/pasynkov-debugging-cookbook/tree/main/cases/gnome-shell/st-boxlayout-invalid-natural-height).
