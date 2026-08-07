# Extension preferences window fails to open or doesn't raise to front

## Short answer

Before launching extension preferences, iterate active windows using `global.display.get_tab_list()`. If the prefs window is already open, unminimize, switch to its workspace, and call `Main.activateWindow()`. If not open, launch using `Main.extensionManager.openExtensionPrefs()` with a fallback to `Util.spawn(['gnome-extensions', 'prefs', uuid])`.

## Environment

- **OS**: Ubuntu 22.04.5 LTS (Linux x86_64, Kernel 6.8.0)
- **Runtime**: GNOME Shell 42.9 (GJS 1.72.4)
- **Hardware**: 13th Gen Intel Core i7-1355U / Intel Raptor Lake Graphics
- **Session**: Wayland & X11

## Fix

```javascript
_openPrefsWindow() {
    let windows = global.display.get_tab_list(Meta.TabList.NORMAL, null);
    for (let win of windows) {
        if (!win || win.is_finalized?.()) continue;
        let wmClass = win.get_wm_class() || '';
        let title = win.get_title() || '';
        if (wmClass.includes('org.gnome.Shell.Extensions') ||
            wmClass.includes('gnome-extensions-prefs') ||
            title.includes(Me.metadata.name)) {
            
            if (win.minimized) win.unminimize();
            let ws = win.get_workspace();
            if (ws) ws.activate(global.get_current_time());
            Main.activateWindow(win);
            return;
        }
    }

    try {
        if (Main.extensionManager && typeof Main.extensionManager.openExtensionPrefs === 'function') {
            Main.extensionManager.openExtensionPrefs(Me.uuid, '', {});
            return;
        }
    } catch (_) {}

    try {
        Util.spawn(['gnome-extensions', 'prefs', Me.uuid]);
    } catch (e) {
        logError(e, '[RightDock] Failed to spawn extension prefs');
    }
}
```

## Verification

1. Click settings icon in dock panel.
2. Verify prefs window opens.
3. Minimize prefs window, then click settings icon again.
4. Verify existing prefs window unminimizes and receives focus.
