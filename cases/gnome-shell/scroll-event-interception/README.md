# Mouse wheel scrolling blocked by child actor event interception (MILESTONE-02)

## Short answer

To allow `St.ScrollView` to scroll when mouse wheeling over interactive child actors, child actors must return `Clutter.EVENT_PROPAGATE` on standard `scroll-event` passes. To hide the scrollbar completely, apply strict CSS rules (`width: 0px !important; opacity: 0 !important;`) on `StScrollBar`.

## Environment

- **OS**: Ubuntu 22.04.5 LTS (Linux x86_64, Kernel 6.8.0)
- **Runtime**: GNOME Shell 42.9 (GJS 1.72.4)
- **Hardware**: 13th Gen Intel Core i7-1355U / Intel Raptor Lake Graphics
- **Session**: Wayland & X11

## Fix

### JavaScript (`appIcon.js`)

```javascript
this.actor.connect('scroll-event', (actor, event) => {
    let state = event.get_state();
    let isShift = (state & Clutter.ModifierType.SHIFT_MASK) !== 0;

    if (isShift) {
        // Reserve Shift + Scroll for active window cycling
        this._cycleWindows(event.get_scroll_direction());
        return Clutter.EVENT_STOP;
    }

    // Propagate normal wheel scroll to parent St.ScrollView
    return Clutter.EVENT_PROPAGATE;
});
```

### CSS (`stylesheet.css`)

```css
StScrollView StScrollBar {
    min-width: 0px !important;
    width: 0px !important;
    opacity: 0 !important;
}

StScrollView StScrollBar StButton {
    min-width: 0px !important;
    width: 0px !important;
    opacity: 0 !important;
}
```

## Verification

1. Move mouse cursor over application icon list inside `St.ScrollView`.
2. Scroll mouse wheel up and down.
3. Verify list scrolls smoothly without visible scrollbar.
