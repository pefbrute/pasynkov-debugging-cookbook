# Устранение схлопывания St.ScrollView до 1px при незамкнутых запросах геометрии в GNOME Shell

> **Проверено на окружении**:
> - **ОС**: Ubuntu 22.04.5 LTS (Linux x86_64)
> - **Среда**: GNOME Shell 42.9 (GJS 1.72.4), Mutter 42.0+
> - **Сессия**: Wayland и X11

Представьте ситуацию: вы пишете расширение или компонент интерфейса для рабочей среды GNOME Shell на JavaScript (GJS). Код выполняется без единой ошибки в консоли, все объекты успешно создаются, иконки инстанциируются, но на экране... **абсолютная пустота**.

Вы начинаете дампать геометрию контейнера в лог и видите странную картину:

```text
appsScroll=1
appsBox=1
```

Контейнер `St.ScrollView` внезапно схлопнулся до высоты **1px**. Добавив логирование геометрии актора, вы обнаруживаете, что дочерний элемент возвращает аномально большую высоту — порядка нескольких миллиардов пикселей.

---

## 1. Диагностика: Трассировка виртуального метода `vfunc_get_preferred_height`

Чтобы точно отследить, какое значение ширины `forWidth` передает движок Clutter в дочерний актор во время реального цикла компоновки, переопределим виртуальный метод:

```javascript
vfunc_get_preferred_height(forWidth) {
    let [minH, natH] = super.vfunc_get_preferred_height(forWidth);
    console.log(`[Preferred-size pass] ChildGridActor.vfunc_get_preferred_height(forWidth=${forWidth}) => minH=${minH}, natH=${natH}`);
    return [minH, natH];
}
```

Вывод во время реального цикла компоновки:

```text
[Preferred-size pass] ChildGridActor.vfunc_get_preferred_height(forWidth=-1) => minH=0, natH=<аномально большое значение>

StBoxLayout (parent): minH=0, natH=<аномально большое значение>, allocH=600
  StScrollView: minH=1, natH=<аномально большое значение>, allocH=1   <-- Схлопнулся!
    ChildGridActor: minH=0, natH=<аномально большое значение>, allocH=0
```

Дочерний элемент `ChildGridActor` при отрицательном значении `forWidth` (незамкнутый запрос) возвращает аномальное значение естественной высоты. Из-за этого родительский `St.ScrollView` сжимается до 1px.

---

## 2. Анализ: Откуда берётся аномальная высота

### Механизм в коде актора

Типичная причина — отсутствие защитной проверки на отрицательное входное значение `forWidth`. Вот иллюстративный пример такого бага (цифры подобраны для наглядности механизма, а не как точная реконструкция конкретного лога):

```javascript
// ИЛЛЮСТРАТИВНЫЙ ПРИМЕР — показывает механизм бага, не точные значения
_calculateGridHeight(forWidth) {
    let itemWidth = 64;
    let numItems = this._items.length;

    // При forWidth = -1: Math.floor(-1 / 64) = -1
    let cols = Math.floor(forWidth / itemWidth);

    // Без проверки отрицательного forWidth: деление на отрицательный cols
    // даёт отрицательное число строк и, как следствие, отрицательную высоту
    let rows = Math.ceil(numItems / cols);
    return rows * 80; // возвращает отрицательное число
}
```

### Аномально большое значение в логе

Clutter API определяет `for_width` и выходные значения высоты (`min_height_p`, `natural_height_p`) как `gfloat` ([документация Clutter](https://gnome.pages.gitlab.gnome.org/mutter/clutter/method.Actor.get_preferred_height.html)). Точный механизм, по которому отрицательное возвращаемое значение из GJS превращается в аномально большое число, наблюдаемое в логах, не установлен из исходников Clutter/Mutter — это может быть последующий каст, арифметическое переполнение, преобразование при логировании или другой этап конвейера компоновки. Конкретное значение в вашем логе может отличаться.

---

## 3. Контракт API Clutter: отрицательный `for_width` — это штатный незамкнутый запрос

Передача отрицательного значения `for_width` движком Clutter — это **задокументированный API-контракт**: «a negative value to indicate that no width is defined» ([документация Clutter](https://gnome.pages.gitlab.gnome.org/mutter/clutter/method.Actor.get_preferred_height.html)).

Ноль (`for_width = 0`) означает формально определённую ширину в ноль пикселей и технически не является незамкнутым запросом, хотя деление на ноль столбцов также должно быть защищено.

* **`ClutterBoxLayout`**: при выравнивании без флага расширения (`align` при `expand: false`) запрашивает предпочтительную высоту с отрицательным `for_width` (незамкнутый запрос).
* **`ChildGridActor`**: ответственность за корректный ответ лежит на его реализации `vfunc_get_preferred_height` — она обязана корректно обрабатывать как отрицательные значения `forWidth`, так и малые значения вроде нуля, защищая вычисление числа столбцов от деления на ноль или на отрицательное число.

---

## 4. Два уровня решений и экспериментальные трассировки

### Решение 1. Защитная реализация актора (Defensive Fix — Рекомендуется)

Используйте собственную предпочтительную ширину сетки в качестве fallback при отрицательном `forWidth` — это безопаснее, чем запрашивать ширину у родителя, который на момент запроса предпочтительного размера может ещё не иметь allocation и вернёт свою natural width ([документация Clutter](https://mutter.gnome.org/clutter/method.Actor.get_width.html)):

```javascript
vfunc_get_preferred_height(forWidth) {
    // Fallback через intrinsic width сетки при незамкнутом запросе (forWidth < 0)
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

#### Экспериментальная трассировка Решения 1 (Defensive Fix при `forWidth = -1`):
```text
[Preferred-size pass] ChildGridActor.vfunc_get_preferred_height(forWidth=-1) => minH=0, natH=340   <-- Защитный fallback обработал -1!

StBoxLayout (parent): minH=0, natH=340, allocH=600
  StScrollView: minH=1, natH=340, allocH=600   <-- Баг устранён!
    ChildGridActor: minH=0, natH=340, allocH=340
```

---

### Решение 2. Конфигурация верстки (Layout Workaround)

Если доступ к исходному коду кастомного актора ограничен, на уровне верстки можно передать флаги расширения (`x_expand: true`, `y_expand: true`). В данной конкретной иерархии акторов это изменило путь вычисления preferred-size так, что выделенная ширина контейнера стала передаваться в дочерний актор. Обратите внимание: layout manager сохраняет право выполнять промежуточные запросы с отрицательными значениями, поэтому данный workaround надёжен только в паре с защитной реализацией:

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

#### Экспериментальная трассировка Решения 2 (Layout Workaround в данной иерархии):
```text
[Preferred-size pass] ChildGridActor.vfunc_get_preferred_height(forWidth=280) => minH=0, natH=340   <-- В данном сценарии layout передаёт ширину контейнера!

StBoxLayout (parent): minH=0, natH=340, allocH=600
  StScrollView: minH=1, natH=340, allocH=600   <-- Баг устранён!
    ChildGridActor: minH=0, natH=340, allocH=340
```

---

## 5. Замечание: требование StScrollable

`St.ScrollView` рассчитан на единственного непосредственного потомка, реализующего интерфейс `StScrollable` ([документация St.ScrollView](https://gnome.pages.gitlab.gnome.org/gnome-shell/st/class.ScrollView.html)). Если `ChildGridActor` является прямым дочерним актором `St.ScrollView`, убедитесь, что он реализует `StScrollable`, или используйте обёртку через `St.Viewport`.

---

## 6. Ошибочные гипотезы и неудачные решения

### ❌ Неудачный подход №1: Фиксированный `min-height` в CSS
```css
.my-scroll-view {
    min-height: 300px;
}
```
* **Почему провалилось**: Схлопывание прекратилось, но `ScrollView` потерял отзывчивость: он перестал динамически подстраиваться под размер панели на разных мониторах и начал обрезать контент.

### ❌ Неудачный подход №2: Вызов `actor.queue_relayout()` в конструкторе
```javascript
_init() {
    super._init();
    this.queue_relayout(); 
}
```
* **Почему провалилось**: Вызов `queue_relayout()` во время `_init()`, когда GObject-свойства ещё не до конца инициализированы, вызвал рекурсивную гонку обновлений на старте GNOME Shell.

### ❌ Неудачный подход №3: Конфликт нескольких «хозяев геометрии»
Задание геометрии одновременно из JavaScript (`actor.set_width(...)`) и из CSS (`stylesheet.css`) привело к зацикливанию перерисовки.

---

## 7. Проверка и верификация

```bash
bash cases/gnome-shell/st-boxlayout-invalid-natural-height/verify.sh
```

1. Установите и включите тестовый модуль расширения в сессии GNOME Shell 42.9 (Ubuntu 22.04.5 LTS).
2. Откройте боковую панель с `St.ScrollView`.
3. Убедитесь, что высота `appsScroll` больше 100px и иконки рендерятся без схлопывания.

---

## Выводы

Схлопывание `St.ScrollView` до 1px происходит из-за того, что кастомный актор при незамкнутом запросе (отрицательный `forWidth`) возвращает отрицательное или иначе аномальное значение высоты, что приводит к некорректному preferred-size, видимому в логах как аномально большое число.

Правильное решение: реализация `vfunc_get_preferred_height` должна **всегда** возвращать конечное неотрицательное значение и корректно вычислять число столбцов как для замкнутых, так и для незамкнутых запросов, используя intrinsic-ширину компонента для незамкнутого случая вместо запроса к ещё не выделенному родителю.
