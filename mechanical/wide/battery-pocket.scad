// Separate rear-shell insert study. Coordinates are PCB X/Y, in mm.
// Put the open lip at Z=0 locally; assembly Z depends on bottom-side part heights.
profile = "flat"; // [flat,compact]
assert(profile == "flat" || profile == "compact");
pack_max = profile == "flat" ? [114, 67, 10.8] : [69, 56.5, 19];
pocket_center = profile == "flat" ? [0, -10.5] : [0, 0];

// Provisional allowances, subject to measured pack growth and enclosure fit.
side_gap = 1;
depth_gap = 2;
wall = 1.5;
floor_thickness = 1.5;
lead_opening = 12;
lead_y = 0;
$fn = 48;

module rounded_slab(size, r, height) {
    linear_extrude(height=height)
        offset(r=r) square([size[0]-2*r, size[1]-2*r], center=true);
}

module battery_pocket(pack, center) {
    inside = [pack[0]+2*side_gap, pack[1]+2*side_gap];
    outside = [inside[0]+2*wall, inside[1]+2*wall];
    depth = pack[2]+depth_gap;
    translate([center[0], center[1], 0]) difference() {
        translate([0,0,-depth-floor_thickness])
            rounded_slab(outside, 1+wall, depth+floor_thickness);
        translate([0,0,-depth])
            rounded_slab(inside, 1, depth+0.1);
        // An open-top slot allows the harness to drop in without threading its plug.
        translate([inside[0]/2-0.1, lead_y-lead_opening/2, -depth])
            cube([wall+0.2, lead_opening, depth+0.1]);
    }
}

battery_pocket(pack_max, pocket_center);
