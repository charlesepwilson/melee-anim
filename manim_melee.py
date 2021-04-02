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

        input_gate_diameter = 183  # max(stick_and_di.GATE_YS) - min(stick_and_di.GATE_YS)
        input_gate_diameter_mm = 10.9  # stick_and_di.GATE_DIAMETER_MM - stick_and_di.STICK_STEM_DIAMETER_MM
        mm_to_input = 16.8  # 183 / 10.9
        physical_diameter_as_input = 361  # stick_and_di.GATE_DIAMETER_MM * mm_to_input
        gcc_svg_init_scale = 4.6  # This scale will make the gate on the gcc svg have unit radius

        self.square = Square(square_edge, stroke_opacity=0, color=WHITE, fill_opacity=1)
        self.circle = Circle(radius=circle_radius, color=WHITE, fill_opacity=1, stroke_opacity=0)
        self.gcc = SVGMobject(
            r'C:\Users\charl\Documents\Python_Projects\manim\GCController_Layout_Modified.svg'
        ).scale(gcc_svg_init_scale * physical_diameter_as_input / 2)
        self.gcc_stick_pos = self.gcc.get_center() - self.gcc.submobjects[20].get_center()
        self.gcc.shift(self.gcc_stick_pos)
        self.set_gcc_colours()
        self.gate = RegularPolygon(n=8, color=YELLOW, stroke_opacity=1, stroke_width=100).scale(input_gate_diameter / 2)

        gate_points = [np.array([x - 128, y - 128, 0]) for x, y in zip(stick_and_di.GATE_XS, stick_and_di.GATE_YS)]
        self.gate = ArcPolygon(*gate_points, radius=-300, color=YELLOW, stroke_opacity=1, stroke_width=100)

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


class TestScene(MovingCameraScene):
    def __init__(self, **kwargs):
        MovingCameraScene.__init__(self, **kwargs)

    def construct(self):
        text_scaling = 50
        x_colour = RED
        y_colour = PURPLE
        frame_height = stick_and_di.INPUT_SIZE * 1.5
        self.camera.frame.set(height=frame_height)
        control_stick = ControlStick()
        self.add(control_stick.gcc)
        self.camera.frame.set(
            height=control_stick.gcc.height * 1.5).move_to(control_stick.gcc.get_center())
        self.wait()
        background = Rectangle(height=frame_height, width=frame_height * 2, fill_opacity=1, fill_color=BLACK)
        self.play(self.camera.frame.animate.move_to(ORIGIN).set(height=frame_height))
        self.wait()
        self.play(FadeIn(background))

        raw_x = 30  # np.random.randint(255)  # Varies 0-255
        raw_x_tracker = ValueTracker(raw_x)

        def int2bin(n):
            return "{:b}".format(int(n))

        bin_x = int2bin(raw_x)
        raw_y = 0
        raw_y_tracker = ValueTracker(raw_y)
        # TODO Sort out binary display. Should be right aligned and monospaced, possibly show all leading 0s
        bin_x_display = Integer(int(bin_x), color=x_colour).scale(text_scaling)
        bin_x_display.add_updater(lambda m: m.set_value(int(int2bin(raw_x_tracker.get_value()))))

        equals_display = MathTex('   =   ', color=x_colour).scale(text_scaling).next_to(
            bin_x_display[-1])
        raw_x_display = Integer(raw_x, color=x_colour).scale(text_scaling).next_to(equals_display)
        raw_x_display.add_updater(lambda m: m.set_value(raw_x_tracker.get_value()))

        raw_y_display = Integer(raw_y, color=y_colour).scale(text_scaling)
        raw_y_display.add_updater(lambda m: m.set_value(raw_y_tracker.get_value()))

        for i in range(8):
            self.play(Write(bin_x_display[i]))
        self.play(Write(raw_x_display), Write(equals_display))

        self.play(raw_x_tracker.animate.set_value(200))

        self.wait()
        self.play(FadeIn(control_stick.square))
        self.add(control_stick.circle)
        self.wait()
        self.play(ShowCreation(control_stick.gate))
        self.wait()
        self.play(control_stick.square.animate.set_fill(LIGHT_GREY))
        self.wait(2)
