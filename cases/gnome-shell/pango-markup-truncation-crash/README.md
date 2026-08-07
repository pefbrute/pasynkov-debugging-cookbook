# Truncating app or window title causes Pango markup syntax exception

## Short answer

Calling `.substring(0, N)` on a string *after* escaping Pango entities cuts XML entities mid-sequence (e.g., `&amp;` cut to `&am`), causing `St.Label` to throw `Error: Entity did not end with a semicolon`. Always truncate plain text **first**, and then pass the truncated string to `GLib.markup_escape_text()`.

## Environment

- **OS**: Ubuntu 22.04 LTS / Ubuntu 24.04 LTS
- **Runtime**: GNOME Shell 42 / 45 / 46 (GJS, St, GLib)
- **Session**: Wayland & X11

## Fix

### Incorrect Order (Causes Exception)

```javascript
// ❌ WRONG: Escaping before truncating cuts &amp; into &am
let escaped = GLib.markup_escape_text(rawTitle, -1);
let winTitle = escaped.length > 24 ? escaped.substring(0, 21) + '...' : escaped;
label.clutter_text.set_markup(winTitle);
```

### Correct Order

```javascript
// ✅ CORRECT: Truncate plain text first, then escape Pango entities
let rawTitle = win.get_title() || app.get_name() || '';
if (rawTitle.length > 24) {
    rawTitle = rawTitle.substring(0, 21) + '...';
}
let winTitle = GLib.markup_escape_text(rawTitle, -1);
label.clutter_text.set_markup(winTitle);
```

## Verification

1. Open a browser window with title `Research & Development - Deep Dive (2026)`.
2. Hover icon to trigger tooltip or window preview label.
3. Confirm title renders as `Research & Developm...` without Pango errors.
