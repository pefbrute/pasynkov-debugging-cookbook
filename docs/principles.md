# Pasynkov Debugging Cookbook principles

## Separate observations from hypotheses

"The menu switches on hover" is an observation. "The menu manager causes it"
is a hypothesis until a trace, minimal reproduction, or the relevant version's
source code confirms it.

## State the scope of every conclusion

A working solution for GNOME 45 on Wayland is not automatically a solution for
every GNOME release. Versions and environment are part of the result, not a
footnote.

## A negative result is still a result

Preserve failed approaches together with their failure mode and side effects.
This prevents other developers and agents from repeating plausible but
incorrect fixes.

## Verifiability matters more than confidence

A minimal reproduction, test, trace, or primary-source link is more valuable
than a long explanation without evidence.
