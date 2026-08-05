# Dock extension fails to hide over fullscreen games during Alt+Tab

## Short answer

To reliably hide a GNOME Shell extension panel/dock over fullscreen games, do **not** rely solely on window-level `in-fullscreen-changed` signals or CSS transitions. Listen to `global.display` signals (`notify::focus-window`, `in-fullscreen-changed`, `restacked`) wrapped in `GLib.idle_add()`. When fullscreen is detected on the monitor, physically disable the dock via `actor.hide()`, `actor.reactive = false`, and destroy `PressureBarrier` instances.

## Environment

- **OS**: Ubuntu 22.04 LTS / Ubuntu 24.04 LTS
- **Runtime**: GNOME Shell 42 / 45 / 46 (GJS, Clutter, St)
- **Session**: Wayland & X11

## Symptom

1. The dock panel remains visible over fullscreen 3D games or videos when navigating between windows using Alt+Tab.
2. Background mouse polling timers or `raise_top()` calls pull the dock back onto the screen during active gameplay.

## Root cause

1. **Alt+Tab Focus Traversal**: Swapping focus to an already-fullscreen window does not fire `in-fullscreen-changed` on the window object because its fullscreen property has not changed.
2. **Mutter Stacking Timing**: Window stack state in Mutter updates asynchronously. Checking window properties synchronously during signal firing yields stale window stack data.
3. **Mouse Polling & Pressure Barriers**: Moving the dock off-screen via CSS coordinates is overridden by periodic mouse polling loops (`_pollMousePosition`) or Meta pressure barrier triggers.

## Failed approaches

- **Window-only signals**: Subscribing only to `window.connect('in-fullscreen-changed')`. Missed window focus changes on Alt+Tab.
- **Off-screen position shifts**: Using `ease({ x: monitor.x + monitor.width })`. The periodic 100ms mouse poll timer moved the actor back onto the screen.

## Fix

### Step 1: Create FullscreenController with display-wide signals
```javascript
class FullscreenController {
    constructor(autohideManager) {
        this._am = autohideManager;
        this._blocked = false;
        this._signals = [
            [global.display, global.display.connect('notify::focus-window', () => this._queueUpdate())],
            [global.display, global.display.connect('in-fullscreen-changed', () => this._queueUpdate())],
            [global.display, global.display.connect('restacked', () => this._queueUpdate())],
        ];
        this._queueUpdate();
    }

    _queueUpdate() {
        if (this._updateIdleId) return;
        this._updateIdleId = GLib.idle_add(GLib.PRIORITY_DEFAULT, () => {
            this._updateIdleId = 0;
            this._update();
            return GLib.SOURCE_REMOVE;
        });
    }

    _update() {
        let ext = this._am._extension;
        if (!ext) return;
        let monitor = ext._getMonitor();
        if (!monitor) return;
        let monitorIndex = monitor.index ?? 0;

        let focusWindow = global.display.get_focus_window();
        let focusedFullscreen = focusWindow !== null &&
            focusWindow.is_fullscreen() &&
            focusWindow.get_monitor() === monitorIndex;

        let monitorFullscreen = false;
        try {
            monitorFullscreen = global.display.get_monitor_in_fullscreen(monitorIndex);
        } catch (_) {}

        let blocked = focusedFullscreen || monitorFullscreen;
        if (blocked === this._blocked) return;
        this._blocked = blocked;

        if (blocked) {
            this._am._onFullscreenEnter();
        } else {
            this._am._onFullscreenExit();
        }
    }
}
```

### Step 2: Enforce hard actor hiding & barrier destruction
```javascript
_onFullscreenEnter() {
    this._dockContainer.remove_all_transitions();
    this._dockContainer.hide();
    this._dockContainer.reactive = false;
    this._destroyBarrier();
}

_onFullscreenExit() {
    this._dockContainer.show();
    this._dockContainer.reactive = true;
    this._createBarrier();
}
```

## Verification

1. Launch a fullscreen game (Steam / Native).
2. Press Alt+Tab to switch focus away and back to the game.
3. Verify that the dock remains completely hidden (`actor.visible == false`) and pointer events do not hit the dock edge.

## Sources

- [Meta.Display API Reference](https://gnome.pages.gitlab.gnome.org/mutter/meta/class.Display.html)
