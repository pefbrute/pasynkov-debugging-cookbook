# Context menu switches on hover

## Short answer

This case is still a draft. The behavior was observed in a GNOME Shell
extension, but the Shell version, Wayland/X11 session, minimal reproduction,
and root cause have not been recorded. A connection to the shared
`PopupMenuManager` is a hypothesis, not an established fact.

## Environment

The GNOME Shell version, distribution, Wayland/X11 session, and extension
version still need to be recorded.

## Symptom

After opening one tray icon's context menu, moving the pointer across adjacent
icons may switch the open menu without another click.

## Reproduction

1. Right-click the target icon to open its context menu.
2. Without pressing any button, move the pointer across adjacent icons.
3. Record whether an adjacent icon's menu opens.

Expected: an adjacent menu does not open without an explicit user action.

## Root cause

Not established. Compare behavior with and without registering the menu in the
shared manager, then inspect the implementation of the exact installed GNOME
Shell version.

## Failed approaches

Stopping the right-button event with `Clutter.EVENT_STOP` was considered as a
fix, but may disrupt later release/click events. A minimal example must confirm
the event sequence.

## Fix

Not established. Do not use this case as a ready-made recommendation.

## Verification and regression coverage

Test right and left clicks, menu dismissal, movement across every relevant icon
type, and the absence of menu switching during hover alone.

## Sources

Add sources after identifying the exact version and inspecting its source code.
