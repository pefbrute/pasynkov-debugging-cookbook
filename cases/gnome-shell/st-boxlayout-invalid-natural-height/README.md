# GNOME Shell St.BoxLayout Invalid Natural Height 4294967296 Collapses St.ScrollView to 1px

## Symptom

App launcher icons or custom extension grid items are instantiated, but remain completely invisible on screen. Inspecting actor geometry via debug logs reveals that the `St.ScrollView` container has collapsed to a height of 1px:

```
appsScroll=1
appsBox=1
status=4294967040
```

Even though children exist and report positive dimensions, the parent `St.ScrollView` refuses to allocate vertical space inside a vertical `St.BoxLayout`.

## Environment

- **OS**: Ubuntu 22.04 / 24.04 LTS (Linux x86_64 / AArch64)
- **Runtime**: GNOME Shell 42 / 45 / 46 (GJS, Clutter, St)
- **Display Server**: Wayland & X11

## Diagnostic Path

To locate the failing actor in the Clutter hierarchy:

1. Traverse the actor tree recursively and print `get_preferred_height(-1)` and `get_allocation_box()` for every container:

```javascript
function inspectActorTree(actor, depth = 0) {
    let [minH, natH] = actor.get_preferred_height(-1);
    let alloc = actor.get_allocation_box();
    let name = actor.get_name() || actor.constructor.name;
    console.log(`${' '.repeat(depth * 2)}${name}: minH=${minH}, natH=${natH}, allocH=${alloc.get_height()}`);
    
    actor.get_children().forEach(child => inspectActorTree(child, depth + 1));
}
```

2. The output reveals an integer overflow sentinel:
   - `ChildGridActor`: `minH=0`, `natH=4294967296`
   - `StScrollView`: `minH=1`, `natH=4294967296`, `allocH=1`

## Root Cause Analysis

In Clutter / St C library implementation, `-1` is used as an unconstrained or default size sentinel in preferred size queries.

When a custom child actor or CSS alignment rule creates an unconstrained layout state (e.g. conflicting `x_align`/`y_align` parameters combined with missing `min-width`/`min-height`), `get_preferred_height()` returns `-1` for `naturalHeight`.

When this value is cast or stored as an unsigned 32-bit integer (`uint32`) inside Clutter's layout calculation struct, `-1` wraps to:

$$\text{uint32}(-1) = 2^{32} - 1 = 4,294,967,295 \approx 4,294,967,296$$

During vertical allocation in `St.BoxLayout`, the algorithm sums natural heights across siblings to allocate proportional space. Seeing an astronomical natural height of $4,294,967,296\text{ px}$, `St.BoxLayout` determines that constraints cannot be satisfied, falls back to minimum height requirements, and collapses `St.ScrollView` to `1px`.

## Failed Approaches

- **Setting `y_align: Clutter.ActorAlign.FILL` without `min-height`**:
  *Result*: Does not prevent the child from returning `-1` sentinel natural height under unconstrained layout queries.
- **Calling `actor.queue_relayout()` during construction**:
  *Result*: Triggers a layout cycle while GObject properties are partially initialized, leading to empty `AppFavorites` grid race conditions on GNOME startup.
- **Multiple Geometry Owners**:
  *Result*: Assigning geometry parameters from both CSS (`stylesheet.css`) and JavaScript layout managers creates competing loops where actors continuously override allocation boxes.

## Correct Solution

1. **Remove conflicting alignment flags**: Keep `x_align` and `y_align` consistent across parent and child containers.
2. **Specify explicit `min-width` and `min-height`**: Ensure every custom grid or child container returns a non-negative minimum height.
3. **Avoid construct-time relayout**: Never call `queue_relayout()` inside `_init()` or constructors.
4. **Reset preferred size safely**: Use `set_height(-1)` only when clearing explicit overrides.
5. **Single Geometry Owner**: Maintain one primary owner for actor dimensions.

### Minimal Diff

```diff
- const grid = new St.Widget({ x_align: Clutter.ActorAlign.CENTER, y_align: Clutter.ActorAlign.FILL });
- grid.queue_relayout();
+ const grid = new St.Widget({
+     style_class: 'app-grid',
+     x_expand: true,
+     y_expand: true,
+ });
+ grid.set_size(200, 300);
```

## Related Edge Cases

1. **Empty `AppFavorites` on Startup**: `AppSystem` may not be initialized when extension loads; defer grid population to `app-state-changed` signal.
2. **Disposed `DockAppIcon` References**: Avoid retaining JS references to actors that GNOME Shell has destroyed.

## Verification

Run the verification script:
```bash
bash cases/gnome-shell/st-boxlayout-invalid-natural-height/verify.sh
```

Verify that `appsScroll` allocation height is $> 100\text{px}$ and `naturalHeight` is non-negative and $< 4294967296$.
