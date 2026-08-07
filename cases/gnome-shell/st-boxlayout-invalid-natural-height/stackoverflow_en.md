# Fixing a GNOME Shell St.ScrollView 1px layout collapse under unconstrained sizing queries

When developing a custom GNOME Shell extension or UI component in GJS (JavaScript), a custom grid widget inside an `St.ScrollView` within a vertical `St.BoxLayout` collapses to a height of 1px and becomes invisible on screen.

Inspect actor geometry via debug logs:

```text
appsScroll=1
appsBox=1
```

Inside `ChildGridActor`, natural height calculation under unconstrained queries (negative `forWidth`) produces invalid column counts and returns a negative height. The following is an **illustrative example** of the bug mechanism — not a byte-for-byte reproduction of specific log values:

```javascript
// ILLUSTRATIVE EXAMPLE — demonstrates the bug mechanism, not exact log numbers
_calculateGridHeight(forWidth) {
    let itemWidth = 64;
    let numItems = 4;
    // Negative unconstrained query: forWidth = -1 => Math.floor(-1 / 64) = -1
    let cols = Math.floor(forWidth / itemWidth);
    // Without a guard for negative forWidth: dividing by negative cols
    // yields negative rows, and then a negative height
    let rows = Math.ceil(numItems / cols);
    return rows * 80; // returns a negative number
}
```

Output during the live preferred-size pass before fix:

```text
[Preferred-size pass] ChildGridActor.vfunc_get_preferred_height(forWidth=-1) => minH=0, natH=<large anomalous value>

StBoxLayout (parent): minH=0, natH=<large anomalous value>, allocH=600
  StScrollView: minH=1, natH=<large anomalous value>, allocH=1   <-- Collapsed!
    ChildGridActor: minH=0, natH=<large anomalous value>, allocH=0
```

The Clutter API defines `for_width` and the height output parameters as `gfloat` ([Clutter docs](https://gnome.pages.gitlab.gnome.org/mutter/clutter/method.Actor.get_preferred_height.html)). The exact mechanism by which a negative GJS return value becomes the specific large anomalous value visible in logs has not been confirmed from Clutter/Mutter source — it may result from a later cast, arithmetic overflow, a logging conversion, or another pipeline stage. The exact value in your log may differ.

How can this container collapse be resolved cleanly?

---

## Answer

### Root Cause & Two Resolution Levels

Passing a negative `for_width` by Clutter is a **documented API contract** meaning "no width is defined" ([Clutter docs](https://gnome.pages.gitlab.gnome.org/mutter/clutter/method.Actor.get_preferred_height.html)). Note: `for_width = 0` is a formally defined width of zero pixels, not an unconstrained query — but zero column counts must also be guarded.

The 1px collapse occurs when a custom child actor fails to handle negative `forWidth` defensively inside its preferred-size implementation.

### 1. Defensive Component Fix (Recommended)

Use the grid's own intrinsic preferred width as a fallback. Avoid `get_parent().get_width()`: when the parent has no allocation yet, it returns its natural width ([Clutter docs](https://mutter.gnome.org/clutter/method.Actor.get_width.html)), which can introduce a hidden circular dependency in preferred-size calculations:

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

#### Log Trace (Defensive Fix under `forWidth = -1`):
```text
[Preferred-size pass] ChildGridActor.vfunc_get_preferred_height(forWidth=-1) => minH=0, natH=340   <-- Defensive fallback handles -1!

StBoxLayout (parent): minH=0, natH=340, allocH=600
  StScrollView: minH=1, natH=340, allocH=600   <-- Resolved!
    ChildGridActor: minH=0, natH=340, allocH=340
```

### 2. Layout Workaround

At the container level, replace non-expanding alignment flags with explicit expansion delegation (`x_expand: true`, `y_expand: true`). In this specific actor hierarchy, enabling expansion changed the preferred-size path so that the allocated width was subsequently supplied to the grid. The layout manager retains the right to issue intermediate queries with negative `for_width`, so this workaround is only reliable when paired with a defensive implementation:

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

#### Log Trace (Layout Workaround in this hierarchy):
```text
[Preferred-size pass] ChildGridActor.vfunc_get_preferred_height(forWidth=280) => minH=0, natH=340   <-- In this scenario, layout passes container width!

StBoxLayout (parent): minH=0, natH=340, allocH=600
  StScrollView: minH=1, natH=340, allocH=600   <-- Resolved!
    ChildGridActor: minH=0, natH=340, allocH=340
```

### Note: StScrollable Requirement

`St.ScrollView` is a single-child container for actors implementing `StScrollable` ([St.ScrollView docs](https://gnome.pages.gitlab.gnome.org/gnome-shell/st/class.ScrollView.html)). If `ChildGridActor` is a direct child of `St.ScrollView`, ensure it implements `StScrollable`, or wrap it via `St.Viewport`.

### Conclusion

The preferred-size implementation must always return finite, non-negative values and compute a valid column count for both constrained and unconstrained queries. Use intrinsic component sizing for the unconstrained case rather than querying an unallocated parent.
