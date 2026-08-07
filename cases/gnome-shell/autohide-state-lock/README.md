# Autohide dock panel stuck hidden off-screen or fails to slide out on hover

## Short answer

If `AutohideManager` initializes `_state = 'shown'`, calling `showDock()` evaluates `if (this._state === 'shown') return` and returns early without resetting `actor.translation_x = 0`. If the actor was translated off-screen during layout setup, the dock stays locked off-screen. To fix this, initialize `_state = 'hidden'`, force reset `showDock(true)` on `enable()`, and guard `hideDock()` against mode `0` (Always Visible).

## Environment

- **OS**: Ubuntu 22.04 LTS / Ubuntu 24.04 LTS
- **Runtime**: GNOME Shell 42 / 45 / 46 (GJS, Clutter, Mutter)
- **Session**: Wayland & X11

## Fix

### 1. `AutohideManager` constructor and state initialization

```javascript
class AutohideManager {
    constructor(ext) {
        this._ext = ext;
        // Start in 'hidden' state so initial showDock(true) forces translation reset
        this._state = 'hidden';
    }

    showDock(force = false) {
        if (this._state === 'shown' && !force && this._slider.translation_x === 0) {
            return;
        }

        this._state = 'shown';
        this._slider.remove_all_transitions();
        this._slider.ease({
            translation_x: 0,
            duration: 150,
            mode: Clutter.AnimationMode.EASE_OUT_QUAD,
        });
    }

    hideDock(force = false) {
        // Prevent hiding if panel mode is set to Always Visible (mode 0)
        if (this._ext._autohideMode === 0 && !force) {
            return;
        }

        if (this._state === 'hidden' && !force) return;

        this._state = 'hidden';
        let targetX = this._ext._dockWidth - 2; // Keep 2px edge hover zone
        this._slider.remove_all_transitions();
        this._slider.ease({
            translation_x: targetX,
            duration: 200,
            mode: Clutter.AnimationMode.EASE_IN_QUAD,
        });
    }
}
```

### 2. Extension `enable()` invocation

```javascript
enable() {
    // Build container hierarchy FIRST...
    this._buildLayout();
    
    // Force show dock panel on enable pass
    this._autohideManager.showDock(true);
}
```

## Verification

1. Enable extension with autohide disabled or enabled.
2. Confirm dock panel immediately appears on screen at position X = 0.
3. Switch between autohide modes and verify smooth slide-in / slide-out behavior.
