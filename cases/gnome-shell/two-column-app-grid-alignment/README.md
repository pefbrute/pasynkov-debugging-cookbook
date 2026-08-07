# 2-column app icon grid aligns to left edge instead of centering (MILESTONE-04)

## Short answer

To center a multi-column row grid symmetrically inside a vertical `St.BoxLayout`, wrap each row pair inside an `St.Bin` container configured with `x_expand: true`, `x_align: Clutter.ActorAlign.CENTER`, and `y_align: Clutter.ActorAlign.CENTER`.

## Environment

- **OS**: Ubuntu 22.04 LTS / Ubuntu 24.04 LTS
- **Runtime**: GNOME Shell 42 / 45 / 46 (GJS, Clutter, St)
- **Session**: Wayland & X11

## Fix

```javascript
let rowFrame = new St.Bin({
    style_class: 'right-dock-app-row-frame',
    x_expand: true,
    y_expand: false,
    x_align: Clutter.ActorAlign.CENTER,
    y_align: Clutter.ActorAlign.CENTER,
});

let rowBox = new St.BoxLayout({
    style_class: 'right-dock-app-row-2col',
    vertical: false,
    x_expand: false,
    y_expand: false,
    spacing: 12,
});

rowBox.add_child(icon1.actor);
rowBox.add_child(icon2.actor);
rowFrame.set_child(rowBox);

this._appsBox.add_child(rowFrame);
```

## Verification

1. Open dock panel containing multiple app icons.
2. Confirm 2-column icon rows are centered symmetrically with equal side padding.
