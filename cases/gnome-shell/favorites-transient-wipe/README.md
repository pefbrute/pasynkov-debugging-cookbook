# Dock wipes favorite app icons during transient AppFavorites unreadiness

## Short answer

During GNOME Shell startup or desktop indexing, `AppFavorites.getAppFavorites().getFavorites()` can transiently return `[]` while `org.gnome.shell.favorite-apps` GSettings holds a list of IDs. Furthermore, `Shell.AppSystem.lookup_app(id)` returns `null` for custom `.desktop` files.

To prevent wiping favorite icon actors, implement a fallback lookup using `Shell.App.new_for_desktop_id(id)`, subscribe to `installed-changed` on `Shell.AppSystem`, and retain existing favorite icons if `favs` transiently returns `[]` while configured favorite IDs exist.

## Environment

- **OS**: Ubuntu 22.04 LTS / Ubuntu 24.04 LTS
- **Runtime**: GNOME Shell 42 / 45 / 46 (GJS, Shell)
- **Session**: Wayland & X11

## Fix

### 1. Robust `Shell.App` resolution with fallback

```javascript
let appSys = Shell.AppSystem.get_default();
let favIds = global.settings.get_strv('favorite-apps') || [];

let favApps = favIds.map(id => {
    if (!id) return null;
    let app = appSys ? appSys.lookup_app(id) : null;
    if (!app && typeof Shell.App.new_for_desktop_id === 'function') {
        try { app = Shell.App.new_for_desktop_id(id); } catch (_) {}
    }
    return app;
}).filter(app => app !== null && app !== undefined);
```

### 2. Transient unreadiness guard in `_syncApps()`

```javascript
// Detect transient unreadiness during startup
if (favIds.length > 0 && favApps.length === 0 && this._appIconMap.size > 0) {
    // Retain existing favorite icon actors and schedule retry
    this._scheduleInitialSyncRetry();
    return;
}
```

### 3. Subscribe to `installed-changed`

```javascript
this._installedChangedId = Shell.AppSystem.get_default().connect('installed-changed', () => {
    this._favorites.reload();
    this._syncApps();
});
```

## Verification

1. Add custom `.desktop` file (e.g. `antigravity.desktop`) to favorites.
2. Restart GNOME Shell (`Alt+F2+r` or restart session).
3. Verify favorite icons remain intact and do not get destroyed.
