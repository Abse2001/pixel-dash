// Pixel Dash case datum in mm. Insert through the existing slot from inside.
// The two ears engage the fixed switch frame after the nominal 0.2 mm stroke.
module prism(x0, x1, y0, y1, z0, z1) {
    translate([x0, y0, z0]) cube([x1-x0, y1-y0, z1-z0]);
}

union() {
    // Thumb surface and guides clear the rounded corners of the slider slot.
    prism(-30.35, -23.35, 42.35, 46.75, 3.15, 5.25);
    // Internal flange retains the cap when the enclosure is assembled.
    prism(-31.95, -21.95, 41.95, 42.72, 3.15, 5.25);
    // Nose and shoulders share a transverse rib behind the board edge.
    prism(-27.35, -23.35, 41.30, 42.40, 2.25, 3.95);
    prism(-25.95, -24.75, 40.95, 41.65, 2.25, 3.10);
    prism(-27.32, -26.56, 40.35, 41.65, 2.25, 3.10);
    prism(-24.14, -23.38, 40.35, 41.65, 2.25, 3.10);
}
