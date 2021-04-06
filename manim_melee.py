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
        gate_colour = DARK_GREY
        line_width = 100

        input_gate_diameter = stick_and_di.input_gate_diameter  # max(stick_and_di.GATE_YS) - min(stick_and_di.GATE_YS)
        physical_diameter_as_input = stick_and_di.physical_diameter_as_input
        gcc_svg_init_scale = 4.6  # This scale will make the gate on the gcc svg have unit radius
        gate_arc_radius = 1.15 * input_gate_diameter

        self.square = Square(square_edge, stroke_opacity=0, color=WHITE, fill_opacity=1)
        self.circle = Circle(radius=circle_radius, color=WHITE, fill_opacity=1, stroke_opacity=0)
        data_color = stick_and_di.possible_inputs_colour()
        self.blocky_circle = ImageMobject(data_color, height=square_edge)
        self.gcc = SVGMobject(
            r'C:\Users\charl\Documents\Python_Projects\manim\GCController_Layout_Modified.svg'
        ).scale(gcc_svg_init_scale * physical_diameter_as_input / 2)
        self.gcc_stick_pos = self.gcc.get_center() - self.gcc.submobjects[20].get_center()
        self.gcc.shift(self.gcc_stick_pos)
        self.set_gcc_colours()
        nice_gate_points = compass_directions(8) * input_gate_diameter / 2
        self.nice_gate = ArcPolygon(*nice_gate_points,
                                    radius=gate_arc_radius,
                                    color=gate_colour,
                                    stroke_opacity=1, stroke_width=line_width
                                    )

        gate_points = [np.array([x - 128, y - 128, 0]) for x, y in zip(stick_and_di.GATE_XS, stick_and_di.GATE_YS)]
        gate_points = gate_points[::-1]
        self.gate = ArcPolygon(*gate_points,
                               radius=gate_arc_radius,
                               color=gate_colour,
                               stroke_opacity=1,
                               stroke_width=line_width)

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


class InputScene(MovingCameraScene):
    def __init__(self, **kwargs):
        MovingCameraScene.__init__(self, **kwargs)

    def construct(self):
        text_scaling = 50
        text_buff = 10
        x_colour = RED
        y_colour = PURPLE
        raw_colour = GREY
        melee_colour = YELLOW

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

        raw_x = 128  # np.random.randint(255)  # Varies 0-255
        raw_x_tracker = ValueTracker(raw_x)

        def int2bin(n):
            return format(int(n), "0=08b") + "="

        sideways_stick_points = [np.array([-5.3, 0, 0]),
                                 np.array([-5.3, 3.6, 0]),
                                 np.array([-8.15, 3.6, 0]),
                                 np.array([8.15, 3.6, 0]),
                                 np.array([5.3, 3.6, 0]),
                                 np.array([5.3, 0, 0])
                                 ]
        sideways_stick_arcs = [{'angle': 0},
                               {'angle': 0},
                               {'radius': -23},
                               {'angle': 0},
                               {'angle': 0},
                               {'angle': 0}
                               ]

        sideways_stick = ArcPolygon(*sideways_stick_points,
                                    arc_config=sideways_stick_arcs,
                                    fill_color=LIGHT_GREY, fill_opacity=1
                                    ).shift(50 * UP).scale(stick_and_di.mm_to_input)

        def mag(vec):
            return sum(vec ** 2) ** 0.5

        rotate_about = DOWN * 100
        s_stick_radius = mag(sideways_stick.get_center_of_mass() - rotate_about)

        angle_squeeze = 66/180

        def get_stick_angle_change():
            target_angle = TAU * (0.25 + angle_squeeze * (0.25 - (raw_x_tracker.get_value() / 510)))
            current_angle = np.arccos(
                (sideways_stick.get_center_of_mass() - rotate_about)[0]
                / s_stick_radius)
            return target_angle - current_angle

        sideways_stick.add_updater(lambda s: s.rotate(get_stick_angle_change(), about_point=rotate_about))
        self.play(FadeIn(sideways_stick))

        def get_binary_display():
            return Text(
                int2bin(raw_x_tracker.get_value()),
                font=MONOSPACE_FONT,
                color=x_colour).scale(text_scaling).shift(DOWN * 100 + LEFT * 30)

        def become_binary_display(mobject):
            mobject.become(get_binary_display())

        bin_x_display = get_binary_display()
        bin_x_display.add_updater(become_binary_display)

        raw_x_display = Integer(raw_x, color=x_colour).scale(text_scaling).next_to(bin_x_display, buff=text_buff)
        raw_x_display.add_updater(lambda m: m.set_value(raw_x_tracker.get_value()))
        raw_x_label = MathTex('x=', color=x_colour).scale(text_scaling).next_to(
            raw_x_display, LEFT, buff=text_buff)

        x_stuff = VGroup(raw_x_display, bin_x_display)

        self.play(Write(bin_x_display), Write(raw_x_display))

        tilt = 100
        self.play(raw_x_tracker.animate.set_value(128 + tilt), rate_func=there_and_back, run_time=2)
        self.play(raw_x_tracker.animate.set_value(128 - tilt), rate_func=there_and_back, run_time=2)
        self.play(Uncreate(sideways_stick))

        bin_x_display.remove_updater(become_binary_display)

        self.play(Transform(bin_x_display, raw_x_label))

        self.play(x_stuff.animate.move_to(np.array([220, 100, 0])))

        raw_y = 128
        raw_y_tracker = ValueTracker(raw_y)
        raw_y_label = MathTex('y=',
                              color=y_colour
                              ).scale(text_scaling
                                      ).next_to(bin_x_display, DOWN, buff=text_buff).align_to(bin_x_display, LEFT)
        raw_y_display = Integer(raw_y, color=y_colour).scale(text_scaling).next_to(raw_y_label, RIGHT, buff=text_buff)
        raw_y_display.add_updater(lambda m: m.set_value(raw_y_tracker.get_value()))
        y_stuff = VGroup(raw_y_label, raw_y_display)

        raw_input_dot = Dot(radius=3, color=DARK_GREY, fill_opacity=1)
        raw_input_dot.add_updater(
            lambda m: m.move_to(np.array([
                raw_x_tracker.get_value() - 128,
                raw_y_tracker.get_value() - 128,
                0])))

        self.play(FadeIn(control_stick.square), FadeInFrom(raw_y_display, UP), FadeInFrom(raw_y_label, UP))
        control_stick.blocky_circle.set(height=stick_and_di.INPUT_SIZE)
        self.add(control_stick.blocky_circle)
        self.play(ShowCreation(raw_input_dot))

        def animate_xy(x=128, y=128, random=False):
            target_x = x if not random else np.random.randint(255)
            target_y = y if not random else np.random.randint(255)
            self.play(
                raw_x_tracker.animate.set_value(target_x),
                raw_y_tracker.animate.set_value(target_y))

        for _ in range(3):
            animate_xy(random=True)
        animate_xy()
        coordinates_bg_rect = SurroundingRectangle(VGroup(raw_x_display, raw_y_display, raw_y_label),
                                                   fill_color=BLACK, fill_opacity=0.6, buff=text_buff)
        self.add(coordinates_bg_rect)
        self.bring_to_front(raw_x_display, raw_y_display, bin_x_display, raw_y_label)
        self.play(FadeOut(background))
        self.wait()
        self.play(ShowCreation(control_stick.gate))
        self.wait()
        self.play(FadeOut(control_stick.gcc))
        self.wait()
        self.play(control_stick.square.animate.set_fill(LIGHT_GREY))
        self.wait(3)
        self.play(FadeIn(control_stick.circle), control_stick.blocky_circle.animate.set_opacity(0))
        self.remove(control_stick.blocky_circle)
        self.bring_to_front(raw_input_dot)
        self.wait()
        self.play(Transform(control_stick.gate, control_stick.nice_gate))
        self.wait()
        raw_label = Tex('Raw Input',
                        color=raw_colour
                        ).scale(text_scaling).next_to(bin_x_display, UP, buff=text_buff)
        raw_label.move_to(raw_label.get_center()[1] * UP + y_stuff.get_center()[0] * RIGHT)
        label_gap = 90
        melee_label = Tex(r'Processed\\Input',
                          color=melee_colour).scale(text_scaling).next_to(raw_label, DOWN, buff=label_gap)

        def get_melee_input():
            m_x, m_y = stick_and_di.raw_to_melee(raw_x_tracker.get_value(), raw_y_tracker.get_value())
            return np.array([m_x, m_y, 0])

        melee_input_dot = Dot(radius=3, color=melee_colour, fill_opacity=0)
        melee_input_dot.add_updater(lambda m: m.move_to(get_melee_input()))

        melee_label_x = MathTex('x =',
                                color=x_colour
                                ).scale(text_scaling
                                        ).next_to(melee_label, DOWN, buff=text_buff).align_to(raw_y_label, LEFT)
        melee_input_display_x = Integer(color=x_colour, include_sign=True
                                        ).scale(text_scaling
                                                ).next_to(melee_label_x, RIGHT, buff=text_buff)
        melee_label_y = MathTex('y =',
                                color=y_colour).scale(text_scaling).next_to(melee_label_x, DOWN, text_buff)
        melee_input_display_y = Integer(color=y_colour, include_sign=True
                                        ).scale(text_scaling).next_to(melee_label_y, RIGHT, buff=text_buff)
        melee_input_display_x.add_updater(mxu := lambda m: m.set_value(melee_input_dot.get_center()[0]))
        melee_input_display_y.add_updater(myu := lambda m: m.set_value(melee_input_dot.get_center()[1]))

        self.play(Write(VGroup(raw_label, melee_label,
                               melee_label_x, melee_input_display_x,
                               melee_label_y, melee_input_display_y,
                               melee_input_dot)))
        animate_xy(164, 99)
        self.wait()
        animate_xy()

        self.wait(2)
        raw_input_line = Line(start=ORIGIN, end=raw_input_dot.get_center(),
                              color=DARK_GREY, stroke_width=100, stroke_opacity=1)
        raw_input_line.add_updater(lambda m: m.put_start_and_end_on(ORIGIN, 0.01 * UP + raw_input_dot.get_center()))

        animate_xy(200, 150)
        self.play(ShowCreation(raw_input_line))
        self.bring_to_front(melee_input_dot)
        self.play(FadeIn(melee_input_dot))
        melee_input_dot.set_fill(color=melee_colour, opacity=1)
        self.wait()
        animate_xy(244, 15)
        self.play(ApplyWave(raw_input_line, amplitude=5))
        self.play(CircleIndicate(melee_input_dot,
                                 rate_func=there_and_back_with_pause,
                                 circle_config={'color': PINK, 'stroke_width': 100}),
                  run_time=3)
        self.wait(3)

        divide80_display = MathTex(r'\divisionsymbol 80'
                                   ).scale(text_scaling).next_to(melee_input_display_y, DOWN, buff=text_buff)
        divide80_display_copy = divide80_display.copy()
        unit_melee_display_x = DecimalNumber(0, color=x_colour, num_decimal_places=4, include_sign=True
                                             ).scale(text_scaling).next_to(melee_label_x, buff=text_buff)
        unit_melee_display_y = DecimalNumber(0, color=y_colour, num_decimal_places=4, include_sign=True
                                             ).scale(text_scaling).next_to(melee_label_y, buff=text_buff)
        unit_melee_display_x.add_updater(lambda m: m.set_value(melee_input_dot.get_center()[0] / 80))
        unit_melee_display_y.add_updater(lambda m: m.set_value(melee_input_dot.get_center()[1] / 80))
        dummy_transform_x = Dot().move_to(melee_input_display_x)
        dummy_transform_y = Dot().move_to(melee_input_display_y)

        animate_xy(5, 27)
        melee_input_display_x.remove_updater(mxu)
        melee_input_display_y.remove_updater(myu)
        self.play(Write(divide80_display), Write(divide80_display_copy))
        self.play(Transform(divide80_display[:], dummy_transform_x),
                  Transform(divide80_display_copy[:], dummy_transform_y),
                  FadeOut(melee_input_display_x),
                  FadeOut(melee_input_display_y),
                  Write(unit_melee_display_x),
                  Write(unit_melee_display_y)
                  )
        animate_xy(x=128+80)
        self.wait()
        animate_xy(x=128+40)
        self.wait()
        animate_xy(y=128-80)
        self.wait()
        animate_xy()
        self.wait(2)


class DeadZoneScene(MovingCameraScene):
    def __init__(self, **kwargs):
        MovingCameraScene.__init__(self, **kwargs)

    def construct(self):
        text_scaling = 50
        text_buff = 10
        x_colour = RED
        y_colour = PURPLE
        raw_colour = GREY
        melee_colour = YELLOW
        dz_colour = LIGHT_BROWN

        frame_height = stick_and_di.INPUT_SIZE * 1.5
        self.camera.frame.set(height=frame_height)
        control_stick = ControlStick()

        raw_x = 128
        raw_x_tracker = ValueTracker()
        raw_x_display = Integer(raw_x, color=x_colour).scale(text_scaling)
        raw_x_display.add_updater(lambda m: m.set_value(raw_x_tracker.get_value()))
        raw_x_label = MathTex('x=', color=x_colour).scale(text_scaling).next_to(
            raw_x_display, LEFT, buff=text_buff)
        raw_y = 128
        raw_y_tracker = ValueTracker(raw_y)
        raw_y_label = MathTex('y=', color=y_colour).scale(text_scaling)
        raw_y_display = Integer(raw_y, color=y_colour).scale(text_scaling).next_to(raw_y_label, RIGHT, buff=text_buff)
        raw_y_display.add_updater(lambda m: m.set_value(raw_y_tracker.get_value()))

        def animate_xy(x=128, y=128, random=False):
            target_x = x if not random else np.random.randint(255)
            target_y = y if not random else np.random.randint(255)
            self.play(
                raw_x_tracker.animate.set_value(target_x),
                raw_y_tracker.animate.set_value(target_y))

        raw_input_dot = Dot(radius=3, color=DARK_GREY, fill_opacity=1)
        raw_input_dot.add_updater(
            lambda m: m.move_to(np.array([
                raw_x_tracker.get_value() - 128,
                raw_y_tracker.get_value() - 128,
                0])))
        raw_input_line = Line(start=ORIGIN, end=0.01 * UP + raw_input_dot.get_center(),
                              color=DARK_GREY, stroke_width=100, stroke_opacity=1)
        raw_input_line.add_updater(lambda m: m.put_start_and_end_on(ORIGIN, 0.01 * UP + raw_input_dot.get_center()))

        raw_label = Tex('Raw Input',
                        color=raw_colour
                        ).scale(text_scaling)
        label_gap = 90
        melee_label = Tex(r'Processed\\Input',
                          color=melee_colour).scale(text_scaling).next_to(raw_label, DOWN, buff=label_gap)

        def get_melee_input():
            m_x, m_y = stick_and_di.raw_to_melee(raw_x_tracker.get_value(), raw_y_tracker.get_value())
            return np.array([m_x, m_y, 0])

        melee_input_dot = Dot(radius=3, color=melee_colour, fill_opacity=0)
        melee_input_dot.add_updater(lambda m: m.move_to(get_melee_input()))

        melee_label_x = MathTex('x =',
                                color=x_colour
                                ).scale(text_scaling
                                        ).next_to(melee_label, DOWN, buff=text_buff).align_to(raw_y_label, LEFT)
        melee_input_display_x = Integer(color=x_colour, include_sign=True
                                        ).scale(text_scaling
                                                ).next_to(melee_label_x, RIGHT, buff=text_buff)
        melee_label_y = MathTex('y =',
                                color=y_colour).scale(text_scaling).next_to(melee_label_x, DOWN, text_buff)
        melee_input_display_y = Integer(color=y_colour, include_sign=True
                                        ).scale(text_scaling).next_to(melee_label_y, RIGHT, buff=text_buff)
        melee_input_display_x.add_updater(lambda m: m.set_value(melee_input_dot.get_center()[0]/80))
        melee_input_display_y.add_updater(lambda m: m.set_value(melee_input_dot.get_center()[1])/80)

        def get_dead_zone_input():
            m_input = melee_input_dot.get_center()
            m_x, m_y = m_input[0], m_input[1]
            dz_x, dz_y = stick_and_di.apply_dead_zone(m_x, m_y)
            return np.array([dz_x, dz_y, 0])
        dz_input_dot = Dot(radius=3, colour=dz_colour)
        dz_input_dot.add_updater(lambda m: m.move_to(get_dead_zone_input()))

        dz_label = Tex(r'with Dead Zone', color=dz_colour).scale(text_scaling)

        dz_label_x = MathTex(r'x=', color=x_colour).scale(text_scaling)
        dz_display_x = DecimalNumber(0, num_decimal_places=4, include_sign=True, color=x_colour).scale(text_scaling)
        dz_display_x.add_updater(lambda m: m.set_value(dz_input_dot.get_center()[0]/80))

        dz_label_y = MathTex(r'y=', color=y_colour).scale(text_scaling)
        dz_display_y = DecimalNumber(0, num_decimal_places=4, include_sign=True, color=y_colour).scale(text_scaling)
        dz_display_y.add_updater(lambda m: m.set_value(dz_input_dot.get_center()[1] / 80))

        self.add(control_stick.square, control_stick.circle, control_stick.nice_gate)
        self.add(raw_input_line, raw_input_dot, melee_input_dot, dz_input_dot)


class Testing(Scene):
    def construct(self):
        bg = Rectangle(color=GREY)
        blocky_circle_data = np.uint8(stick_and_di.possible_inputs() * 255)
        blocky_circle = ImageMobject(blocky_circle_data)
        print(blocky_circle.height)
        self.add(bg)
        self.add(blocky_circle)
        self.add(SurroundingRectangle(blocky_circle))
        self.wait(3)
