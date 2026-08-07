/* Fixed Implementation: Explicit sizing & consistent expansion flags */
const { St, Clutter } = imports.gi;

function buildFixedLayout() {
    const box = new St.BoxLayout({
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

    const grid = new St.Widget({
        style_class: 'app-grid',
        x_expand: true,
        y_expand: true,
    });

    // Provide explicit minimum height to avoid -1 / 4294967296 sentinel overflow
    grid.set_size(200, 300);

    scrollView.add_actor(grid);
    box.add_child(scrollView);
    return box;
}
