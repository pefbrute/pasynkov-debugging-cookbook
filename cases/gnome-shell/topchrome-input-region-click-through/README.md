# Custom popover is visible but mouse clicks pass through to background

## Short answer

Floating popovers and preview cards added via `Main.uiGroup.add_actor()` render visually, but Mutter ignores their pointer events unless registered in the input region. Register floating popovers with `Main.layoutManager.addTopChrome(popup, { affectsInputRegion: true, trackFullscreen: true })` and unregister via `removeChrome(popup)` when hidden/destroyed.

## Environment

- **OS**: Ubuntu 22.04 LTS / Ubuntu 24.04 LTS
- **Runtime**: GNOME Shell 42 / 45 / 46 (GJS, Clutter, St)
- **Session**: Wayland & X11

## Symptom

Preview cards or popovers appear on screen when hovering app icons, but clicking buttons inside the popover fails; clicks pass through to windows beneath.

## Root cause

Mutter maintains an **input region mask** for GNOME Shell UI. Visual rendering (`add_actor`) is independent of input region tracking (`addTopChrome`). Without `affectsInputRegion: true`, Mutter discards pointer events over the popover.

## Fix

### 1. TopChrome Registration
```javascript
if (typeof Main.layoutManager.addTopChrome === 'function') {
    Main.layoutManager.addTopChrome(popup, {
        affectsInputRegion: true,
        trackFullscreen: true,
    });
} else {
    Main.layoutManager.addChrome(popup, {
        affectsInputRegion: true,
        trackFullscreen: true,
    });
}
```

### 2. Cleanup on Hide
```javascript
if (Main.layoutManager.isTracked(popup)) {
    Main.layoutManager.removeChrome(popup);
}
popup.destroy();
```

### 3. Explicit Button Mask on Children
Ensure `St.Button` children capture primary clicks:
```javascript
let btn = new St.Button({
    reactive: true,
    can_focus: true,
    track_hover: true,
    button_mask: St.ButtonMask.ONE,
});
```

## Verification

1. Hover an app icon with running windows to show window previews.
2. Click close `✕` or maximize `🗖`.
3. Confirm button action triggers cleanly without activating background windows.
