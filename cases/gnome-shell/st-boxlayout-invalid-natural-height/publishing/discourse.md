# Post Draft for GNOME Discourse (https://discourse.gnome.org/)

**Category**: Platform > Extensions  
**Title**: `[St/Clutter] St.ScrollView collapses to 1px when sibling returns unconstrained preferred height (-1 -> ~4.29e9 natH)`  
**Tags**: `gjs`, `gnome-shell`, `st`, `clutter`, `extensions`, `layout`

---

## Post Body

Hi everyone,

While developing a GNOME Shell extension layout (a vertical `St.BoxLayout` containing an `St.ScrollView` and a custom child container), we encountered a layout geometry issue where `St.ScrollView` unexpectedly collapsed to `1px` height.

We tracked down the diagnostic behavior and would like to share our empirical observations, as well as ask the maintainers about sentinel handling in `St.BoxLayout` / `Clutter.Actor`.

---

### Observed Symptom

In GNOME Shell 42.9 (Ubuntu 22.04 LTS):
- An actor hierarchy constructed with a vertical `St.BoxLayout` contains:
  1. `St.ScrollView` (with `y_expand = true`).
  2. A child widget container inside or adjacent to the ScrollView.
- The `St.ScrollView` allocated geometry collapses to `height = 1px`, rendering all items inside invisible.

Diagnostic log output:
```text
# Anomalous allocation status observed during early execution pass:
appsScroll=1
appsBox=1
status=4294967040
```

---

### Diagnostic Trace & Empirical Findings

By recursively traversing the actor tree and querying `get_preferred_height(-1)`:

```javascript
let [minH, natH] = actor.get_preferred_height(-1);
console.log(`${actor.constructor.name}: minH=${minH}, natH=${natH}`);
```

We observed the following return values:
- `ChildGridWidget`: `minH = 0`, `natH = 4294967296`
- `StScrollView`: `minH = 1`, `natH = 4294967296`, `allocH = 1`

#### Analysis of the `4294967296` Sentinel

- **Confirmed API Contract**: In Clutter C layout code, passing a negative value like `-1` to `get_preferred_height()` indicates an unconstrained height query (see [Clutter.Actor docs](https://gnome.pages.gitlab.gnome.org/mutter/clutter/method.Actor.get_preferred_height.html)).
- **Observed Behavior**: When a custom child widget with filled alignment (`y_align: FILL`) receives an unconstrained query (`for_width = -1`) and does not sanitize the input inside `vfunc_get_preferred_height`, the returned preferred height manifests in GJS as `natH = 4294967296` ($2^{32}$).
- **Unconfirmed Pipeline Mechanism (Hypothesis)**: Official signatures use [`gfloat*`](https://gnome.pages.gitlab.gnome.org/mutter/clutter/method.Actor.get_preferred_height.html) rather than `guint`, so the exact internal C/GJS pipeline stage converting the negative sentinel to $2^{32}$ is unconfirmed from source.
- **Layout Consequence**: During vertical space allocation in `St.BoxLayout`, summing sibling natural heights containing $4.29 \times 10^9\text{ px}$ causes container allocation math to saturate, forcing the sibling `St.ScrollView` down to its minimum required allocation of `1px`.

---

### Minimal Reproduction Code

```javascript
const { St, Clutter } = imports.gi;

const box = new St.BoxLayout({ vertical: true, x_expand: true, y_expand: true });
const scrollView = new St.ScrollView({
    hscrollbar_policy: St.PolicyType.NEVER,
    vscrollbar_policy: St.PolicyType.AUTOMATIC,
    x_expand: true,
    y_expand: true,
});

// Child widget without explicit min-size and filled alignment
const childGrid = new St.Widget({
    x_align: Clutter.ActorAlign.FILL,
    y_align: Clutter.ActorAlign.FILL,
});

scrollView.add_actor(childGrid);
box.add_child(scrollView);

// Query preferred height
let [minH, natH] = childGrid.get_preferred_height(-1);
console.log(`minH=${minH}, natH=${natH}`); // natH outputs 4294967296
```

---

### Workaround for Extension Developers

1. **Defensive `vfunc_get_preferred_height` Handling**: Ensure to check if `forWidth < 0` (unconstrained query) and return explicit fallback dimensions.
2. **Explicit Minimum Sizing**: Provide explicit minimum size constraints (`set_size(w, h)` or CSS `min-height`) on custom containers.
3. **Consistent Expansion Flags**: Set `x_expand: true` and `y_expand: true` explicitly across layout containers.

---

### Questions for GNOME / St Maintainers

1. Has anyone traced the exact internal C/GJS pipeline stage where an unconstrained negative preferred size sentinel registers as $2^{32}$ (`4294967296`)?
2. Should `St.BoxLayout` clamp or sanitize negative/sentinel preferred sizes before calculating sibling layout space distribution?

---

*Full Case Investigation*: [README.md on GitHub](https://github.com/pefbrute/pasynkov-debugging-cookbook/blob/main/cases/gnome-shell/st-boxlayout-invalid-natural-height/README.md)  
*Reproduction Code & Verification*: [reproduction/extension.js](https://github.com/pefbrute/pasynkov-debugging-cookbook/blob/main/cases/gnome-shell/st-boxlayout-invalid-natural-height/reproduction/extension.js) | [verify.sh](https://github.com/pefbrute/pasynkov-debugging-cookbook/blob/main/cases/gnome-shell/st-boxlayout-invalid-natural-height/verify.sh)
