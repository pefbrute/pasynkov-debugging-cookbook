# Hiding top panel with opacity=0 leaves invisible top dead zone

## Short answer

To completely remove GNOME Shell's default top panel from screen layout, use `Main.panel.hide()` and `Main.panel.reactive = false` instead of `Main.panel.opacity = 0`. Setting `opacity = 0` only makes the panel transparent while keeping its ~32px input region dead zone.

## Environment

- **OS**: Ubuntu 22.04.5 LTS (Linux x86_64, Kernel 6.8.0)
- **Runtime**: GNOME Shell 42.9 (GJS 1.72.4)
- **Hardware**: 13th Gen Intel Core i7-1355U / Intel Raptor Lake Graphics
- **Session**: Wayland & X11

## Symptom

The default GNOME Shell top panel appears hidden/transparent, but mouse clicks on the top 32px of the monitor fail to register on application windows beneath.

## Fix

### Hide panel completely
```javascript
Main.panel.hide();
Main.panel.reactive = false;
```

### Restore panel in disable()
```javascript
Main.panel.show();
Main.panel.opacity = 255;
Main.panel.reactive = true;
```

## Verification

1. Enable the extension.
2. Drag a window to the top edge of the monitor.
3. Click window tabs/controls at the top 10px; verify events register on the window.
