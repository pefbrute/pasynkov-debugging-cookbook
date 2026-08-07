/* Broken Implementation: Unconstrained alignment causes uint32(-1) overflow */
const { St, Clutter } = imports.gi;

function buildBrokenLayout() {
    const box = new St.BoxLayout({ vertical: true });
    const scrollView = new St.ScrollView();

    const grid = new St.Widget({
        x_align: Clutter.ActorAlign.CENTER,
        y_align: Clutter.ActorAlign.FILL,
    });
    // Triggers relayout during construct state
    grid.queue_relayout();

    scrollView.add_actor(grid);
    box.add_child(scrollView);
    return box;
}
