# Cluttered top control button stack & dock background context menu (MILESTONE-09)

## Short answer

To provide a native context menu when right-clicking panel background without interfering with child actors, attach a `button-press-event` listener to `_appsScrollView`. Check `event.get_button() === 3` and verify event target isn't marked with `_blocksDockContextMenu`. Display a `PopupMenu.PopupMenu` instance.

## Environment

- **OS**: Ubuntu 22.04.5 LTS (Linux x86_64, Kernel 6.8.0)
- **Runtime**: GNOME Shell 42.9 (GJS 1.72.4)
- **Hardware**: 13th Gen Intel Core i7-1355U / Intel Raptor Lake Graphics
- **Session**: Wayland & X11

## Fix

```javascript
this._appsScrollView.connect('button-press-event', (actor, event) => {
    if (event.get_button() !== 3) return Clutter.EVENT_PROPAGATE;

    let source = event.get_source();
    if (source && source._blocksDockContextMenu) {
        return Clutter.EVENT_PROPAGATE;
    }

    this._showDockContextMenu(event);
    return Clutter.EVENT_STOP;
});
```

## Verification

1. Right click on dock background or separator.
2. Confirm native `PopupMenu` appears with Panel Settings, Workspaces, and App Grid items.
