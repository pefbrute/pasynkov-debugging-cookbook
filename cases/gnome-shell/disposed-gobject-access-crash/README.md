# GJS throws fatal error accessing already disposed C/Clutter objects

## Short answer

When a Clutter container is destroyed, C-level GObject actors are disposed, but JavaScript wrapper references remain intact in JS `Map` or array structures. Accessing any method on a disposed GObject wrapper throws `Error: Object has been already disposed`. To fix this, remove JS references **before** destroying C objects, connect a `destroy` signal listener to clear JS references on disposal, and guard property access with `try/catch` or `is_finalized`.

## Environment

- **OS**: Ubuntu 22.04 LTS / Ubuntu 24.04 LTS
- **Runtime**: GNOME Shell 42 / 45 / 46 (GJS, Clutter, St)
- **Session**: Wayland & X11

## Fix

### 1. Remove reference from JS Map before `destroy()`

```javascript
// Remove JS map entry BEFORE calling C destroy()
let item = this._appIconMap.get(appId);
if (item) {
    this._appIconMap.delete(appId);
    if (item.actor && !item.actor.is_finalized?.()) {
        item.actor.destroy();
    }
}
```

### 2. Connect `destroy` signal listener on actor creation

```javascript
class DockAppIcon {
    constructor(app) {
        this.actor = new St.Button({ reactive: true });
        
        // Ensure JS reference cleanup if destroyed upstream by Clutter
        this._destroyId = this.actor.connect('destroy', () => {
            this._cleanup();
        });
    }

    _cleanup() {
        if (this._destroyId) {
            this.actor.disconnect(this._destroyId);
            this._destroyId = 0;
        }
        // Nullify sub-references
        this.menu = null;
    }
}
```

### 3. Safe GObject method invocation guard

```javascript
updateState() {
    if (!this.actor || this.actor.is_finalized?.()) return;
    try {
        let parent = this.actor.get_parent();
        if (!parent) return;
        this.actor.add_style_pseudo_class('active');
    } catch (e) {
        // Suppress disposed C object access exceptions cleanly
    }
}
```

## Verification

1. Enable extension.
2. Trigger rapid extension reloading (`Alt+F2+r` or CLI disable/enable loop).
3. Confirm no `already disposed` errors appear in `journalctl -f -o cat /usr/bin/gnome-shell`.
