import gdsfactory as gf

from hhi import cells, tech


@gf.cell
def sample_route_bundle_dc():
    c = gf.Component()
    d1 = c << cells.HHI_DFB()
    p1 = c << cells.pad()
    p1.movey(150)
    p1.movex(-200)
    _ = tech.route_bundle_dc(
        c,
        [d1.ports["e1"]],
        [p1.ports["e1"]],
        auto_taper=False,
        start_straight_length=50,
        end_straight_length=50,
    )
    return c


@gf.cell
def sample_route_bundle_dc_corner():
    c = gf.Component()
    d1 = c << cells.HHI_DFB()
    p1 = c << cells.pad()
    p1.movey(150)
    p1.movex(-200)
    _ = tech.route_bundle_dc_corner(
        c,
        [d1.ports["e1"]],
        [p1.ports["e1"]],
        start_straight_length=50,
        end_straight_length=50,
        auto_taper=False,
    )
    return c


if __name__ == "__main__":
    c = sample_route_bundle_dc_corner()
    c.show()
