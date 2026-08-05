# Custom PopupMenu stays open when clicking outside

## Short answer

To close custom `PopupMenu` instances when clicking outside without crashing Mutter's menu stack, attach a `captured-event` listener to `global.stage`. On `BUTTON_PRESS` outside the menu actor, schedule dismissal via `GLib.idle_add()` and return `Clutter.EVENT_PROPAGATE`.

## Environment

- **OS**: Ubuntu 22.04 LTS / Ubuntu 24.04 LTS
- **Runtime**: GNOME Shell 42 / 45 / 46 (GJS, Clutter)
- **Session**: Wayland & X11

## Fix

```javascript
_enableMenuDismissMonitor() {
    this._disableMenuDismissMonitor();
    this._stageCaptureId = global.stage.connect('captured-event', (stage, event) => {
        if (event.type() !== Clutter.EventType.BUTTON_PRESS) {
            return Clutter.EVENT_PROPAGATE;
        }
        if (!this._openMenus || this._openMenus.length === 0) {
            return Clutter.EVENT_PROPAGATE;
        }

        let [stageX, stageY] = event.get_coords();
        let clickedInsideAnyMenu = this._openMenus.some(menu => {
            if (!menu || !menu.isOpen || !menu.actor || menu.actor.is_finalized?.()) return false;
            let [x, y] = menu.actor.get_transformed_position();
            let [w, h] = menu.actor.get_transformed_size();
            return stageX >= x && stageX <= x + w && stageY >= y && stageY <= y + h;
        });

        if (!clickedInsideAnyMenu) {
            this._markMenuClosedThisTurn();
            GLib.idle_add(GLib.PRIORITY_DEFAULT, () => {
                this._closeTrackedMenus();
                return GLib.SOURCE_REMOVE;
            });
        }
        return Clutter.EVENT_PROPAGATE;
    });
}
```

## Verification

1. Right click to open dock menu.
2. Click anywhere on desktop or another window.
3. Confirm menu closes cleanly.
