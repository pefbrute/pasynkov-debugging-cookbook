/* Minimal reproduction demonstrating St.ScrollView collapsing to 1px due to 4294967296 natural height */
const { St, Clutter } = imports.gi;
const Main = imports.ui.main;

class ReproExtension {
    constructor() {
        this._box = null;
    }

    enable() {
        this._box = new St.BoxLayout({
            vertical: true,
            x_expand: true,
            y_expand: true,
        });

        const scrollView = new St.ScrollView({
            hscrollbar_policy: St.PolicyType.NEVER,
            vscrollbar_policy: St.PolicyType.AUTOMATIC,
            x_expand: true,
            y_expand: true,
        });

        // Problematic child grid actor returning unconstrained preferred height (-1 -> uint32 4294967296)
        const gridActor = new St.Widget({
            x_align: Clutter.ActorAlign.FILL,
            y_align: Clutter.ActorAlign.FILL,
        });

        scrollView.add_actor(gridActor);
        this._box.add_child(scrollView);

        // Print diagnostic heights
        let [minH, natH] = gridActor.get_preferred_height(-1);
        console.log(`[Repro] GridPreferredHeight: min=${minH}, nat=${natH}`);
    }

    disable() {
        if (this._box) {
            this._box.destroy();
            this._box = null;
        }
    }
}

function init() {
    return new ReproExtension();
}
