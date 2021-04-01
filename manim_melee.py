from manim import *
import stick_and_di
import melee_physics

MONOSPACE_FONT = 'monospace'


class KnockbackTrajectory(CubicBezier):
    def __add__(self, mobject):
        CubicBezier.__add__(self, mobject)

    def __iadd__(self, mobject):
        CubicBezier.__iadd__(self, mobject)

    def __sub__(self, mobject):
        CubicBezier.__sub__(self, mobject)

    def __isub__(self, mobject):
        CubicBezier.__isub__(self, mobject)

    def align_points_with_larger(self, larger_mobject):
        CubicBezier.align_points_with_larger(self, larger_mobject)

    def __init__(
            self,
            dmg_before_hit=50,
            kb_angle=45, attack_dmg=10, bkb=50, kbg=50,
            weight=100, fall_speed=1.8, gravity=0.1,
            di=(0, 0), **kwargs
    ):
        self.dmg_before_hit = dmg_before_hit
        self.kb_angle = kb_angle
        self.attack_dmg = attack_dmg
        self.bkb = bkb
        self.kbg = kbg
        self.weight = weight
        self.fall_speed = fall_speed
        self.gravity = gravity
        self.di = di
        self.path_complex = []
        self.path = np.zeros(1)
        self.recalculate_path(dmg_before_hit,
                              kb_angle, attack_dmg, bkb, kbg,
                              weight, fall_speed, gravity,
                              di)
        CubicBezier.__init__(self, self.path, **kwargs)

    def recalculate_path(
            self,
            dmg_before_hit,
            kb_angle, attack_dmg, bkb, kbg,
            weight, fall_speed, gravity,
            di
    ):
        self.dmg_before_hit = dmg_before_hit
        self.kb_angle = kb_angle
        self.attack_dmg = attack_dmg
        self.bkb = bkb
        self.kbg = kbg
        self.weight = weight
        self.fall_speed = fall_speed
        self.gravity = gravity
        self.di = di
        self.path_complex = melee_physics.get_path_from_hitbox_char(
            dmg_before_hit, kb_angle, attack_dmg, bkb, kbg, weight, fall_speed, gravity, di)
        self.path = np.array([np.array([p.real, p.imag, 0]) for p in self.path_complex])
        self.set_points(self.path)

    def set_dmg_before_hit(self, dmg_before_hit):
        self.dmg_before_hit = dmg_before_hit
        self.recalculate_path(self.dmg_before_hit,
                              self.kb_angle, self.attack_dmg, self.bkb, self.kbg,
                              self.weight, self.fall_speed, self.gravity,
                              self.di)

    def set_hitbox(self, **hitbox):
        if 'kb_angle' in hitbox.keys():
            self.kb_angle = hitbox['kb_angle']
        if 'attack_dmg' in hitbox.keys():
            self.attack_dmg = hitbox['attack_dmg']
        if 'bkb' in hitbox.keys():
            self.bkb = hitbox['bkb']
        if 'kbg' in hitbox.keys():
            self.kbg = hitbox['kbg']
        self.recalculate_path(self.dmg_before_hit,
                              self.kb_angle, self.attack_dmg, self.bkb, self.kbg,
                              self.weight, self.fall_speed, self.gravity,
                              self.di)

    def set_character(self, **character):
        if 'weight' in character.keys():
            self.weight = character['weight']
        if 'fall_speed' in character.keys():
            self.fall_speed = character['fall_speed']
        if 'gravity' in character.keys():
            self.gravity = character['gravity']
        self.recalculate_path(self.dmg_before_hit,
                              self.kb_angle, self.attack_dmg, self.bkb, self.kbg,
                              self.weight, self.fall_speed, self.gravity,
                              self.di)

    def set_di(self, di):
        self.di = di
        self.recalculate_path(self.dmg_before_hit,
                              self.kb_angle, self.attack_dmg, self.bkb, self.kbg,
                              self.weight, self.fall_speed, self.gravity,
                              self.di)


class ControlStick(VGroup):
    def __init__(self):
        square_edge = stick_and_di.INPUT_SIZE
        input_origin = stick_and_di.ORIGIN
        dead_zone_outside = stick_and_di.DEAD_ZONE  # First value outside dead zone
        dead_zone = dead_zone_outside - 1  # Last value inside dead zone
        circle_radius = stick_and_di.MAX_MAGNITUDE
        circle_dz = 76  # Maximum other coordinate inside dead zone and circle
        flared_dz = 38  # Maximum coordinate inside dead zone at edge of square
        dz_colour_x = BLUE
        dz_colour_y = PINK

        self.gate = RegularPolygon(n=8, z_index=0)
        # self.gate.scale(1.2)
        self.circle = Circle(radius=circle_radius, color=WHITE, fill_opacity=1, stroke_opacity=0, z_index=0)
        self.square = Square(square_edge, stroke_opacity=0, color=WHITE)
        self.gcc = SVGMobject('GCController_Layout_Modified.svg').scale(5.2)
        self.gccStickPos = self.gcc.get_center() - self.gcc.submobjects[20].get_center()
        self.set_gcc_colours()

        self.backdrops = VGroup(self.gate, self.circle, self.square, self.gcc)
        self.dead_zone_xp = DashedLine(dead_zone * RIGHT + 2 * UP, dead_zone * RIGHT + 2 * DOWN, color=DARK_GREY)
        self.dead_zone_xn = DashedLine(dead_zone * LEFT + 2 * UP, dead_zone * LEFT + 2 * DOWN, color=DARK_GREY)
        self.dead_zone_yp = DashedLine(dead_zone * UP + 2 * LEFT, dead_zone * UP + 2 * RIGHT, color=DARK_GREY)
        self.dead_zone_yn = DashedLine(dead_zone * DOWN + 2 * LEFT, dead_zone * DOWN + 2 * RIGHT, color=DARK_GREY)
        self.dead_zone_lines = VGroup(self.dead_zone_xp, self.dead_zone_xn, self.dead_zone_yp, self.dead_zone_yn)

        self.dead_zone_x = ArcPolygon(
            dead_zone * LEFT + circle_dz * UP,
            dead_zone * LEFT + circle_dz * DOWN,
            dead_zone * RIGHT + circle_dz * DOWN,
            dead_zone * RIGHT + circle_dz * UP,
            arc_config=[{'angle': 0}, {'radius': circle_radius}, {'angle': 0}, {'radius': circle_radius}], z_index=1
        )
        self.dead_zone_x.set_color(dz_colour_x)
        self.dead_zone_x.set_opacity(0.6)
        self.dead_zone_x.set_stroke(opacity=0)

        self.flared_dz_x = Polygon(dead_zone * LEFT + circle_dz * UP,
                                   dead_zone * LEFT + circle_dz * DOWN,
                                   flared_dz * LEFT + input_origin * DOWN,
                                   flared_dz * RIGHT + input_origin * DOWN,
                                   dead_zone * RIGHT + circle_dz * DOWN,
                                   dead_zone * RIGHT + circle_dz * UP,
                                   flared_dz * RIGHT + input_origin * UP,
                                   flared_dz * LEFT + input_origin * UP,
                                   fill_color=dz_colour_x, fill_opacity=0.65, stroke_opacity=0, z_index=1
                                   )
        self.flared_dz_y = self.flared_dz_x.copy().rotate(TAU / 4)
        self.flared_dz_y.set_color(dz_colour_y)
        self.dead_zone_y = self.dead_zone_x.copy().rotate(TAU / 4)
        self.dead_zone_y.set_color(dz_colour_y)
        self.dead_zone_xy = Rectangle(color=YELLOW, height=dead_zone * 2, width=dead_zone * 2)
        self.dead_zone_group = VGroup(self.dead_zone_x, self.dead_zone_y, self.flared_dz_x, self.flared_dz_y,
                                      self.dead_zone_xy)

        VGroup.__init__(self, self.backdrops, self.dead_zone_lines, self.dead_zone_group)

    def set_gcc_colours(self, main_colour=PURPLE_D):
        colours = []
        colours += [GREY, LIGHT_GREY] * 2  # L and R
        colours += [DARK_BLUE, BLUE]  # Z
        colours += [BLACK, main_colour] * 6  # CASING Centre, left, right, behind stick,
        colours += [BLACK, GREY, BLACK]  # GATE
        colours += [LIGHT_GREY, GREY] * 3  # STICK
        colours += [LIGHT_GREY]  # more stick
        colours += [BLACK, YELLOW] * 2  # C STICK
        colours += [BLACK, main_colour]  # D PAD OUTLINE
        colours += [GREY, LIGHT_GREY]  # D PAD
        colours += [GREY] * 5  # D PAD ARROWS
        colours += [GREY, LIGHT_GREY]  # START
        colours += [BLACK, main_colour]  # BEHIND BUTTONS
        colours += [BLACK, GREEN]  # A
        colours += [BLACK, RED]  # B
        colours += [BLACK, LIGHT_GREY]  # X
        colours += [BLACK, LIGHT_GREY]  # Y
        for s, c in zip(self.gcc.submobjects, colours):
            s.set_color(c)

    def align_points_with_larger(self, larger_mobject):
        VGroup.align_points_with_larger(self, larger_mobject)


class TestScene(ZoomedScene):
    def __init__(self, **kwargs):
        ZoomedScene.__init__(
            self,
            zoom_factor=0.3,
            zoomed_display_height=1,
            zoomed_display_width=6,
            image_frame_stroke_width=20,
            zoomed_camera_config={
                "default_frame_stroke_width": 3,
                },
            **kwargs
        )

    def construct(self):
        control_stick = ControlStick()

        self.add(control_stick)
        self.wait(2)
