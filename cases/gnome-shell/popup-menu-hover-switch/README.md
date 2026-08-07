# Context menu switches to an adjacent item on hover in GNOME Shell Extensions

## Short answer

Do **not** register custom extension `PopupMenu` instances or stolen tray indicators into `Main.panel.menuManager` (or a shared `PopupMenuManager`). GNOME Shell's `PopupMenuManager` implements active-menu hover cycling (designed for top menu bars like File → Edit → View), which automatically closes the active menu and opens the menu of any registered actor the pointer hovers over. Furthermore, do **not** bind right-click listeners to the root container (`_dockContainer`); place them on specific content children (`_appsScrollView`) to prevent Clutter event bubbling from tray children.

## Environment

- **OS**: Ubuntu 22.04.5 LTS (Linux x86_64, Kernel 6.8.0)
- **Runtime**: GNOME Shell 42.9 (GJS 1.72.4)
- **Hardware**: 13th Gen Intel Core i7-1355U / Intel Raptor Lake Graphics
- **Session**: Wayland & X11

## Symptom

1. After right-clicking a tray icon (such as Telegram) or an app icon, moving the mouse pointer across adjacent icons immediately closes the active menu and opens the context menu of whatever icon the pointer hovers over without pressing any mouse button.
2. Moving the mouse pointer down to select a lower item in a tray popup menu causes the dock panel context menu ("⚙️ Настройки панели...") to pop up over the tray menu.

## Reproduction

1. In a GNOME Shell extension, register multiple app icon menus or stolen indicator menus with `Main.panel.menuManager.addMenu(menu)`.
2. Attach a `button-press-event` right-click handler to the outer dock container (`_dockContainer`).
3. Right-click an icon to open its context menu.
4. Without pressing any mouse button, move the mouse cursor across adjacent icons in the dock/tray.
5. Observe that the context menu switches automatically on hover.

## Root cause

1. **PopupMenuManager Hover Cycling**: `Main.panel.menuManager` tracks active menu state. When any registered menu is open, `PopupMenuManager` attaches pointer enter/motion listeners to all registered actors. Hovering over another registered actor closes the current menu and opens the hovered actor's menu.
2. **Clutter Event Bubble Phase**: `button-press-event` on a root container (`_dockContainer`) receives events bubbling up from child actors (`_trayBox`). If the root container intercepts right-click events with `Clutter.EVENT_STOP`, Clutter cancels pointer grab for target children and suppresses subsequent `button-release-event` and `clicked` signals.

## Failed approaches

### 1. Returning `Clutter.EVENT_STOP` on root container `button-press-event`
Returning `EVENT_STOP` on the parent container when right-clicking near tray items prevented event propagation, but also canceled Clutter's pointer grab for child tray icons, rendering them completely unresponsive to clicks.

### 2. Checking `_isMenuActive()` inside root container click handler
Interception of all clicks when any menu was open caused `EVENT_STOP` to fire on legitimate left-clicks on tray icons whenever an indicator menu was active.

## Fix

### Step 1: Remove menus from `Main.panel.menuManager`
When stealing status area indicators, explicitly unregister them from `Main.panel.menuManager`:
```javascript
if (indicatorObj && indicatorObj.menu) {
    if (Main.panel.menuManager) {
        try { Main.panel.menuManager.removeMenu(indicatorObj.menu); } catch (_) {}
    }
}
```
Do not call `Main.panel.menuManager.addMenu(menu)` on custom app icons or dock context menus.

### Step 2: Move right-click listener from root container to `_appsScrollView`
Attach `button-press-event` ONLY to the scrollable content area, separating the system tray (`_trayBox`) in the Clutter actor tree:
```javascript
this._appsScrollView.connect('button-press-event', (actor, event) => {
    return this._onDockBackgroundPress(actor, event);
});
```

### Step 3: Mark interactive items and check background source
```javascript
actor._blocksDockContextMenu = true;

_isDockBackgroundSource(source) {
    if (!source || source.is_finalized?.()) return false;
    for (let current = source; current && current !== this._appsScrollView; current = current.get_parent()) {
        if (current._blocksDockContextMenu) return false;
    }
    return source === this._appsScrollView || source === this._appsBox;
}
```

### Step 4: Single-turn menu dismissal debouncing
Set `_menuClosedThisTurn = true` upon closing any tracked menu, and reset it via `GLib.idle_add(GLib.PRIORITY_DEFAULT_IDLE, ...)` to prevent a single physical click from closing one menu and opening another on the same mainloop iteration.

## Verification and regression coverage

1. Run `python3 tools/validate_cases.py` to confirm case schema validity.
2. Validate JavaScript syntax with `node --check extension.js`.
3. Test right-clicking an app icon or tray icon and moving the mouse cursor over neighboring icons; verify no menu switches on hover.
4. Verify that left-click, right-click, and click-outside dismissal work cleanly across all tray icons and app icons.

## Sources

- [GNOME JavaScript Popup Menu Guide](https://gjs.guide/extensions/topics/popup-menu.html)
- [Clutter.Actor API Reference](https://gnome.pages.gitlab.gnome.org/mutter/clutter/class.Actor.html)
