---
title: "Fixing a GNOME Shell St.ScrollView 1px layout collapse under unconstrained sizing queries"
published: true
description: "How to debug and resolve a 1px St.ScrollView layout collapse caused by a custom child actor failing to handle unconstrained preferred-size queries in GNOME Shell extensions."
tags: linux, javascript, c, debugging
canonical_url: https://fedor-pasynkov.ru/blog/gnome-shell-st-boxlayout-invalid-natural-height
---

# Fixing a GNOME Shell St.ScrollView 1px layout collapse under unconstrained sizing queries

> **Tested Environment**:
> - **OS**: Ubuntu 22.04.5 LTS (Linux x86_64)
> - **Runtime**: GNOME Shell 42.9 (GJS 1.72.4), Mutter 42.0+
> - **Session**: Wayland & X11

Imagine this scenario: you are developing an extension or desktop UI component for GNOME Shell using JavaScript (GJS). The extension loads cleanly with zero errors in `journalctl`. All GObjects are instantiated, icons are built, but on the screen... **absolute void**.

When you log the actor geometry to the console, you see an unusual output:

```text
appsScroll=1
appsBox=1
```

The parent `St.ScrollView` container has collapsed to a height of **1px**. Adding geometry logging reveals the child actor is reporting an anomalously large natural height — in the billions of pixels range.

---

## 1. Diagnostics: Tracing `vfunc_get_preferred_height`

To trace the exact `forWidth` parameter passed by Clutter's layout manager **from within the live layout pass**, override the virtual method inside `ChildGridActor`:

```javascript
vfunc_get_preferred_height(forWidth) {
    let [minH, natH] = super.vfunc_get_preferred_height(forWidth);
    console.log(`[Preferred-size pass] ChildGridActor.vfunc_get_preferred_height(forWidth=${forWidth}) => minH=${minH}, natH=${natH}`);
    return [minH, natH];
}
```

Console output during the live layout pass:

```text
[Preferred-size pass] ChildGridActor.vfunc_get_preferred_height(forWidth=-1) => minH=0, natH=<large anomalous value>

StBoxLayout (parent): minH=0, natH=<large anomalous value>, allocH=600
  StScrollView: minH=1, natH=<large anomalous value>, allocH=1   <-- Collapsed!
    ChildGridActor: minH=0, natH=<large anomalous value>, allocH=0
```

`ChildGridActor` receives a negative `forWidth` from the parent container and returns an anomalous natural height, causing `St.ScrollView` to collapse to 1px.

---

## 2. Analysis: Where the Anomalous Height Comes From

### The Bug in Actor Code

The typical cause is missing a defensive guard for negative `forWidth` values. The following is an **illustrative example** showing the bug mechanism — not a byte-for-byte reproduction of any specific log value:

```javascript
// ILLUSTRATIVE EXAMPLE — demonstrates the bug mechanism, not exact log numbers
_calculateGridHeight(forWidth) {
    let itemWidth = 64;
    let numItems = this._items.length;

    // When forWidth = -1: Math.floor(-1 / 64) = -1
    let cols = Math.floor(forWidth / itemWidth);

    // Without a guard for negative forWidth: dividing by negative cols
    // yields negative rows, and then a negative height
    let rows = Math.ceil(numItems / cols);
    return rows * 80; // returns a negative number
}
```

### The Anomalous Value in Logs

The Clutter API defines `for_width` and the height output parameters (`min_height_p`, `natural_height_p`) as `gfloat` ([Clutter docs](https://gnome.pages.gitlab.gnome.org/mutter/clutter/method.Actor.get_preferred_height.html)). The exact mechanism by which a negative GJS return value becomes the specific large anomalous number visible in logs has not been confirmed from Clutter/Mutter source — it may result from a later cast, arithmetic overflow, a logging conversion, or another stage of the layout pipeline. The exact value in your log may differ.

---

## 3. Clutter API Contract: Negative `for_width` is a Valid Unconstrained Query

Passing a negative `for_width` by Clutter is a **documented API contract**: «a negative value to indicate that no width is defined» ([Clutter docs](https://gnome.pages.gitlab.gnome.org/mutter/clutter/method.Actor.get_preferred_height.html)).

`for_width = 0` means a formally defined width of zero pixels and is technically not an unconstrained query — though division by zero columns must also be guarded.

* **`ClutterBoxLayout`**: Under non-expanding alignment (`align` with `expand: false`), queries height with a negative `for_width` (unconstrained query).
* **`ChildGridActor`**: The responsibility lies with the custom implementation — `vfunc_get_preferred_height` must handle negative `forWidth` correctly, and also guard zero or very small widths against invalid column calculations.

---

## 4. Two Resolution Levels & Independent Empirical Traces

### Solution 1: Defensive Component Fix (Recommended)

Use the grid's own intrinsic preferred width as a fallback for negative `forWidth` — this is safer than calling `get_parent().get_width()`, which returns the parent's natural width when the parent has no allocation yet ([Clutter docs](https://mutter.gnome.org/clutter/method.Actor.get_width.html)), potentially creating a hidden circular dependency in preferred-size calculations:

```javascript
vfunc_get_preferred_height(forWidth) {
    // Use intrinsic grid width as fallback for unconstrained queries (forWidth < 0).
    // Deliberately avoid get_parent().get_width(): the parent may not yet have an
    // allocation and would return its natural width, introducing a hidden circular
    // dependency in preferred-size calculations.
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

#### Empirical Log Trace (Defensive Fix under `forWidth = -1`):
```text
[Preferred-size pass] ChildGridActor.vfunc_get_preferred_height(forWidth=-1) => minH=0, natH=340   <-- Defensive fallback handles -1 gracefully!

StBoxLayout (parent): minH=0, natH=340, allocH=600
  StScrollView: minH=1, natH=340, allocH=600   <-- Resolved!
    ChildGridActor: minH=0, natH=340, allocH=340
```

---

### Solution 2: Layout Configuration Workaround

If editing the custom widget code is restricted, passing explicit expansion flags at the container level (`x_expand: true`, `y_expand: true`) may help. In this specific actor hierarchy, enabling expansion changed the preferred-size path so that the allocated width was subsequently supplied to the grid. Note that the layout manager retains the right to issue intermediate queries with a negative `for_width`, so this workaround is only reliable when paired with a defensive implementation:

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

#### Empirical Log Trace (Layout Workaround in this hierarchy):
```text
[Preferred-size pass] ChildGridActor.vfunc_get_preferred_height(forWidth=280) => minH=0, natH=340   <-- In this scenario, layout passes container width!

StBoxLayout (parent): minH=0, natH=340, allocH=600
  StScrollView: minH=1, natH=340, allocH=600   <-- Resolved!
    ChildGridActor: minH=0, natH=340, allocH=340
```

---

## 5. Note: StScrollable Requirement

`St.ScrollView` is a single-child container for actors that implement `StScrollable` ([St.ScrollView docs](https://gnome.pages.gitlab.gnome.org/gnome-shell/st/class.ScrollView.html)). If `ChildGridActor` is a direct child of `St.ScrollView`, ensure it implements `StScrollable`, or wrap it via `St.Viewport`.

---

## 6. Disproven Workarounds (Failed Approaches)

### ❌ Failed Approach #1: Hardcoding `min-height` in CSS
```css
.my-scroll-view {
    min-height: 300px;
}
```
* **Why it failed**: The 1px collapse stopped, but `ScrollView` lost responsiveness: it stopped adapting dynamically to screen resolution changes and clipped overflowing content.

### ❌ Failed Approach #2: Invoking `actor.queue_relayout()` in Constructor
```javascript
_init() {
    super._init();
    this.queue_relayout(); 
}
```
* **Why it failed**: Calling `queue_relayout()` inside `_init()` while GObject properties were partially initialized triggered a recursive layout cycle during startup.

### ❌ Failed Approach #3: Competing Geometry Owners
Setting actor geometry simultaneously from JavaScript (`actor.set_width(...)`) and CSS (`stylesheet.css`) created conflicting layout loops.

---

## 7. Verification

```bash
bash cases/gnome-shell/st-boxlayout-invalid-natural-height/verify.sh
```

1. Install and enable the extension in a GNOME Shell 42.9 session (Ubuntu 22.04.5 LTS).
2. Open the side panel containing `St.ScrollView`.
3. Confirm `appsScroll` allocation height is $> 100\text{px}$ and icons render cleanly.

---

## Conclusion

An `St.ScrollView` 1px collapse occurs when a custom child actor returns a negative or otherwise invalid height under unconstrained queries (negative `forWidth`), which results in an anomalously large value visible in logs.

A complete resolution ensures that `vfunc_get_preferred_height` always returns finite, non-negative values and computes a valid column count for both constrained and unconstrained queries — using intrinsic component sizing for the unconstrained case rather than querying an unallocated parent.
