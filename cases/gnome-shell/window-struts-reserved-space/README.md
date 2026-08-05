# Maximized windows extend under custom GNOME Shell panel

## Short answer

When adding a custom panel/dock actor to GNOME Shell, pass `affectsStruts: true` to `Main.layoutManager.addChrome()`. This instructs Mutter to create window struts (`_NET_WM_STRUT_PARTIAL`), automatically keeping maximized and tiled windows from sliding underneath the panel.

## Environment

- **OS**: Ubuntu 22.04 LTS / Ubuntu 24.04 LTS
- **Runtime**: GNOME Shell 42 / 45 / 46 (GJS, Mutter)
- **Session**: Wayland & X11

## Symptom

Maximized windows (Firefox, Terminal, Files) slide underneath the custom panel, hiding content or window controls behind the panel background.

## Root cause

Mutter does not automatically reserve screen margins for arbitrary `Clutter.Actor` instances added to `Main.uiGroup`. Unless `affectsStruts: true` is explicitly provided during Chrome registration, Mutter treats the entire monitor area as available work area (`Meta.Workspace.get_work_area_for_monitor`).

## Fix

In `extension.js`:
```javascript
Main.layoutManager.addChrome(this._dockContainer, {
    affectsInputRegion: true,
    affectsStruts: true,
    trackFullscreen: true,
});
```

When `disable()` is called:
```javascript
Main.layoutManager.removeChrome(this._dockContainer);
```

## Verification

1. Enable the extension panel.
2. Maximize any window.
3. Confirm that the window boundary stops cleanly at the edge of the panel without overlapping.
