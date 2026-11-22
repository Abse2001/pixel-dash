// Wide rear carrier in board coordinates; PCB midplane is Z=0 mm.
// Access apertures, front-shell fastening and final pack retention are pending.
use <battery-pocket.scad>
$fn = 72;
mounts = [[-70,-29],[70,-29],[-60,31],[60,31]];
pcb_seat = -0.8;
pocket_lip = -6;
outside_floor = pocket_lip - 14.3;
floor_thickness = 1.5;
boss_diameter = 8.2;
shank_diameter = 3.3;
head_diameter = 6.2;
seat_thickness = 2.2;

difference() {
    union() {
        translate([0,0,outside_floor])
            linear_extrude(height=floor_thickness)
                offset(r=8) square([239-16,102-16], center=true);
        translate([0,0,pocket_lip]) battery_pocket([114,67,10.8], [0,-10.5]);
        for (p=mounts)
            translate([p.x,p.y,outside_floor])
                cylinder(d=boss_diameter, h=pcb_seat-outside_floor);
    }
    for (p=mounts) {
        translate([p.x,p.y,outside_floor-0.01])
            cylinder(d=shank_diameter, h=pcb_seat-outside_floor+0.02);
        translate([p.x,p.y,outside_floor-0.01])
            cylinder(d=head_diameter, h=pcb_seat-seat_thickness-outside_floor+0.01);
    }
}
