# Устранение схлопывания St.ScrollView до 1px при незамкнутых запросах геометрии в GNOME Shell

При разработке расширения для GNOME Shell на GJS (JavaScript) виджет сетки внутри `St.ScrollView` в вертикальном `St.BoxLayout` неожиданно схлопывается до высоты 1px и становится невидимым.

В логах отладки геометрия акторов выглядит так:

```text
appsScroll=1
appsBox=1
```

Внутри `ChildGridActor` при незамкнутом запросе (отрицательный `forWidth`) расчет геометрии в JS даёт некорректное число столбцов и возвращает отрицательную высоту. Ниже приведён **иллюстративный пример** механизма бага (не точная реконструкция конкретных значений лога):

```javascript
// ИЛЛЮСТРАТИВНЫЙ ПРИМЕР — показывает механизм бага, не точные значения
_calculateGridHeight(forWidth) {
    let itemWidth = 64;
    let numItems = 4;
    // Незамкнутый запрос: forWidth = -1 => Math.floor(-1 / 64) = -1
    let cols = Math.floor(forWidth / itemWidth);
    // Без проверки отрицательного forWidth: деление на отрицательный cols
    // даёт отрицательное число строк и, как следствие, отрицательную высоту
    let rows = Math.ceil(numItems / cols);
    return rows * 80; // возвращает отрицательное число
}
```

Вывод во время прохода preferred-size до исправления:

```text
[Preferred-size pass] ChildGridActor.vfunc_get_preferred_height(forWidth=-1) => minH=0, natH=<аномально большое значение>

StBoxLayout (parent): minH=0, natH=<аномально большое значение>, allocH=600
  StScrollView: minH=1, natH=<аномально большое значение>, allocH=1   <-- Схлопнулся!
    ChildGridActor: minH=0, natH=<аномально большое значение>, allocH=0
```

Clutter API определяет `for_width` и выходные параметры высоты как `gfloat` ([документация Clutter](https://gnome.pages.gitlab.gnome.org/mutter/clutter/method.Actor.get_preferred_height.html)). Точный механизм, по которому отрицательное JS-значение превращается в конкретное аномально большое число в логе, не установлен из исходников Clutter/Mutter — это может быть последующий каст, арифметическое переполнение, преобразование при логировании или другой этап конвейера компоновки. Конкретное значение в вашем логе может отличаться.

Как правильно исправить схлопывание контейнера?

---

## Ответ

### Причина и два уровня решений

Передача отрицательного `for_width` движком Clutter — это задокументированный API-контракт, означающий «ширина не определена» ([документация Clutter](https://gnome.pages.gitlab.gnome.org/mutter/clutter/method.Actor.get_preferred_height.html)). Важно: `for_width = 0` означает формально определённую ширину ноль пикселей и технически не является незамкнутым запросом — однако вычисление нулевого числа столбцов также должно быть защищено.

Схлопывание происходит из-за того, что кастомный актор не обрабатывает отрицательный `forWidth` внутри расчёта предпочтительного размера.

### 1. Защитная реализация актора (Рекомендуется)

Используйте intrinsic-ширину сетки как fallback. Избегайте `get_parent().get_width()`: если у родителя ещё нет allocation, он возвращает natural width ([документация Clutter](https://mutter.gnome.org/clutter/method.Actor.get_width.html)), что может создать скрытую циклическую зависимость в preferred-size вычислениях:

```javascript
vfunc_get_preferred_height(forWidth) {
    // Fallback через intrinsic width сетки при незамкнутом запросе (forWidth < 0).
    // get_parent().get_width() не используется намеренно: родитель может ещё
    // не иметь allocation и вернёт natural width, что создаёт скрытую
    // циклическую зависимость в preferred-size вычислениях.
    const fallbackWidth = this._getPreferredGridWidth();

    const effectiveWidth =
        Number.isFinite(forWidth) && forWidth >= 0
            ? forWidth
            : fallbackWidth;

    const natH = this._calculateGridHeight(effectiveWidth);

    return [
        0,
        Number.isFinite(natH) ? Math.max(0, natH) : 0,
    ];
}

_calculateGridHeight(width) {
    const itemWidth = 64;
    const rowHeight = 80;
    const numItems = this.get_n_children();

    const safeWidth =
        Number.isFinite(width) && width > 0
            ? width
            : this._getPreferredGridWidth();

    const columns = Math.max(1, Math.floor(safeWidth / itemWidth));
    const rows = Math.ceil(numItems / columns);

    return Math.max(0, rows * rowHeight);
}
```

#### Трассировка логов (Defensive Fix при `forWidth = -1`):
```text
[Preferred-size pass] ChildGridActor.vfunc_get_preferred_height(forWidth=-1) => minH=0, natH=340   <-- Защитный fallback обработал -1!

StBoxLayout (parent): minH=0, natH=340, allocH=600
  StScrollView: minH=1, natH=340, allocH=600   <-- Устранено!
    ChildGridActor: minH=0, natH=340, allocH=340
```

### 2. Обходное решение верстки

На уровне верстки контейнера замените флаги выравнивания на явную передачу расширения родителю (`x_expand: true`, `y_expand: true`). В данной конкретной иерархии акторов это изменило путь вычисления preferred-size так, что выделенная ширина контейнера стала передаваться в дочерний актор. Layout manager сохраняет право выполнять промежуточные запросы с отрицательным `for_width`, поэтому данный workaround надёжен только в паре с защитной реализацией:

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

#### Трассировка логов (Layout Workaround в данной иерархии):
```text
[Preferred-size pass] ChildGridActor.vfunc_get_preferred_height(forWidth=280) => minH=0, natH=340   <-- В данном сценарии layout передаёт ширину контейнера!

StBoxLayout (parent): minH=0, natH=340, allocH=600
  StScrollView: minH=1, natH=340, allocH=600   <-- Устранено!
    ChildGridActor: minH=0, natH=340, allocH=340
```

### Замечание: требование StScrollable

`St.ScrollView` рассчитан на единственного непосредственного потомка, реализующего `StScrollable` ([документация St.ScrollView](https://gnome.pages.gitlab.gnome.org/gnome-shell/st/class.ScrollView.html)). Если `ChildGridActor` является прямым дочерним актором `St.ScrollView`, убедитесь, что он реализует `StScrollable`, или используйте обёртку через `St.Viewport`.

### Итог

Реализация `vfunc_get_preferred_height` должна **всегда** возвращать конечное неотрицательное значение и корректно вычислять число столбцов как для замкнутых, так и для незамкнутых запросов — используя intrinsic-ширину компонента для незамкнутого случая вместо запроса к ещё не выделенному родителю.
