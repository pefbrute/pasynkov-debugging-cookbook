# GNOME Shell St.ScrollView Collapse Caused by Invalid Natural Height 4294967296

## Symptom

App launcher icons or custom extension grid items are instantiated, but remain completely invisible on screen. Inspecting actor geometry via debug logs reveals that the `St.ScrollView` container has collapsed to a height of 1px:

```text
appsScroll=1
appsBox=1
status=4294967040
```

Even though children exist and report positive dimensions, the parent `St.ScrollView` refuses to allocate vertical space inside a vertical `St.BoxLayout`.

## Environment

- **OS**: Ubuntu 22.04.5 LTS (Linux x86_64)
- **Runtime**: GNOME Shell 42.9 (GJS 1.72.4)
- **Dependencies**: Mutter >= 42.0
- **Display Server**: Wayland & X11

## Diagnostic Path

To locate the failing actor in the Clutter hierarchy:

1. Traverse the actor tree recursively and print `get_preferred_height(-1)` (where `-1` specifies an unconstrained width query) and `get_allocation_box()` for every container:

```javascript
function inspectActorTree(actor, depth = 0) {
    let [minH, natH] = actor.get_preferred_height(-1);
    let alloc = actor.get_allocation_box();
    let name = actor.get_name() || actor.constructor.name;
    console.log(`${' '.repeat(depth * 2)}${name}: minH=${minH}, natH=${natH}, allocH=${alloc.get_height()}`);
    
    actor.get_children().forEach(child => inspectActorTree(child, depth + 1));
}
```

2. The output reveals an unconstrained layout value near the $2^{32}$ boundary:
   - `ChildGridActor`: `minH=0`, `natH=4294967296`
   - `StScrollView`: `minH=1`, `natH=4294967296`, `allocH=1`

## Working Hypothesis & Mathematical Evidence

The observed failure is real: a child actor reported an enormous preferred height near the 32-bit unsigned boundary ($2^{32} = 4,294,967,296$), after which `St.ScrollView` received only a 1px allocation.

### 1. The $-1$ Unconstrained Query Parameter
In `get_preferred_height(-1)`, `-1` is the input parameter `for_width`, representing an unconstrained width query in Clutter (`clutter_actor_get_preferred_height`). One working hypothesis is that an unconstrained or sentinel preferred size entered the layout calculation when intermediate containers lacked explicit minimum dimensions or had conflicting `x_align`/`y_align` flags.

### 2. Floating-Point (`gfloat`) Precision at $2^{32}$
In Clutter and Mutter C layout implementations (`clutter/clutter-box-layout.c`), layout sizes are calculated using `gfloat` (32-bit IEEE 754 single-precision floating point numbers).

Near $2^{32}$, single-precision floats lose unit precision:
- $2^{32} = 4,294,967,296$
- $2^{32} - 256 = 4,294,967,040$

The values observed in logs ($4,294,967,296$ and $4,294,967,040$) match representable values in `gfloat` arithmetic for numbers near the $2^{32}$ limit.

> **Note on Root Cause Boundaries**: The exact integer-to-unsigned/float conversion point in Mutter or St has not yet been isolated to a specific line in C source. The arithmetic alignment near $2^{32}$ remains a working hypothesis based on empirical logs.

### 3. Container Allocation Fallback
When vertical `ClutterBoxLayout` sums natural heights across siblings, an astronomical value near $4\,294\,967\,296\text{ px}$ causes proportional space allocation to fail. Clutter triggers a fallback, granting `St.ScrollView` its minimum requirement — **1px**.

## Failed Approaches

- **Setting `y_align: Clutter.ActorAlign.FILL` without `min-height`**:
  *Result*: Does not prevent the child from returning an unconstrained preferred size.
- **Calling `actor.queue_relayout()` during construction**:
  *Result*: Triggers a layout cycle while GObject properties are partially initialized, leading to empty `AppFavorites` grid race conditions on GNOME startup.
- **Multiple Geometry Owners**:
  *Result*: Assigning geometry parameters from both CSS (`stylesheet.css`) and JavaScript layout managers creates competing loops where actors continuously override allocation boxes.

## Correct Solution

1. **Single Geometry Owner**: Manage dimensions and expansion in one location (JS via Clutter actor flags).
2. **Align Container Constraints**: Remove conflicting `x_align` and `y_align` parameters from intermediate wrappers.
3. **Use Expansion Flags**: Use `x_expand: true` and `y_expand: true` so the parent layout manager handles dynamic resizing.

### Diagnostic Workaround vs Adaptive Solution

As a diagnostic workaround to confirm preferred size behavior, setting explicit bounds restores allocation:
```javascript
grid.set_size(200, 300); // Workaround for testing size constraints
```

For the adaptive production fix:
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

## Illustrative Layout Structure

The snippet in `reproduction/` provides an illustrative layout structure demonstrating container hierarchy rather than a standalone containerized GNOME Shell process.

## Verification

### 1. Repository Validation
Run `bash verify.sh` to check JS syntax across `reproduction/`, `broken/`, and `fixed/`, verify file structure, and run `tools/validate_cases.py`.

### 2. Runtime Verification in GNOME Shell
1. Install and enable the extension in a GNOME Shell 42.9 session.
2. Open the side panel or dock containing `St.ScrollView`.
3. Confirm `appsScroll` allocation height is $> 100\text{px}$ and icons render properly.
