# Stolen statusArea indicators distorted or misaligned in custom grid

## Short answer

When stealing indicators from `Main.panel._rightBox` or `Main.panel.statusArea`, save original actor state (`x_align`, `y_align`, `style`), recursively constrain child actor sizes (`constrainActorRecursive`), wrap each in a `TrayIconWrapper` slot (`32x32px`), and apply CSS resets (`-natural-hpadding: 0; margin: 0; padding: 0;`).

## Environment

- **OS**: Ubuntu 22.04.5 LTS (Linux x86_64, Kernel 6.8.0)
- **Runtime**: GNOME Shell 42.9 (GJS 1.72.4)
- **Hardware**: 13th Gen Intel Core i7-1355U / Intel Raptor Lake Graphics
- **Session**: Wayland & X11

## Fix

### 1. State Preservation & Stealing
```javascript
saveActorState(actor) {
    return {
        actor: actor,
        originalParent: actor.get_parent(),
        x_align: actor.x_align,
        y_align: actor.y_align,
        style: actor.get_style?.() || null,
    };
}
```

### 2. Wrapper Slot Creation
```javascript
class TrayIconWrapper extends St.Bin {
    constructor(actor) {
        super({
            style_class: 'right-dock-tray-icon-slot',
            width: 32,
            height: 32,
            x_align: Clutter.ActorAlign.CENTER,
            y_align: Clutter.ActorAlign.CENTER,
            clip_to_allocation: false,
        });
        actor.x_align = Clutter.ActorAlign.CENTER;
        actor.y_align = Clutter.ActorAlign.CENTER;
        this.set_child(actor);
    }
}
```

### 3. CSS Resets
In `stylesheet.css`:
```css
.right-dock-tray-icon-slot {
    width: 32px;
    height: 32px;
    margin: 0;
    padding: 0;
}
.right-dock-tray-icon-slot * {
    -natural-hpadding: 0px !important;
    -minimum-hpadding: 0px !important;
    margin: 0px !important;
    padding: 0px !important;
}
```

## Verification

1. Launch applications with indicators (Telegram, Steam, Discord).
2. Confirm icons fit neatly into 32x32px slots without overflow.
3. Disable extension to confirm clean restoration to top panel.
