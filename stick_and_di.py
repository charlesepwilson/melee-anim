import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import fractions

INPUT_SIZE = 256
ORIGIN = INPUT_SIZE // 2
MAX_MAGNITUDE = 80
MAX_MAG_SQUARE = 6400
DEAD_ZONE = 23  # Out of 80, 23 is not included in dead zone
MAX_DI = 18  # degrees

GATE_XS = [233, 206, 125, 55, 32, 56, 131, 210, 233]
GATE_YS = [129, 44, 22, 50, 125, 202, 227, 205, 129]
GATE_DIAMETER_MM = 21.5
STICK_STEM_DIAMETER_MM = 10.6
input_gate_diameter = 205  # max(GATE_YS) - min(GATE_YS)
input_gate_diameter_mm = 10.9  # GATE_DIAMETER_MM - STICK_STEM_DIAMETER_MM
mm_to_input = 18.8  # 205 / 10.9
physical_diameter_as_input = 404  # GATE_DIAMETER_MM * mm_to_input


def raw_to_melee(x, y):
    """Takes a stick input consisting of two integers x and y that are each between 0 and 255 inclusive.
    Returns a tuple containing this input converted to the integer representation in Melee,
    where each coordinate is an integer between -80 and 80 inclusive, and the magnitude <= 80
    """
    n = ORIGIN
    max_magnitude = MAX_MAGNITUDE
    max_magnitude_squared = MAX_MAG_SQUARE
    x_shift, y_shift = x - n, y - n
    magnitude_squared = x_shift ** 2 + y_shift ** 2

    def shorten(coord, mag):
        output = coord * max_magnitude
        output = output / mag
        output = int(output)
        return output

    if magnitude_squared > max_magnitude_squared:
        magnitude = magnitude_squared ** 0.5
        x_shift = shorten(x_shift, magnitude)
        y_shift = shorten(y_shift, magnitude)
        assert x_shift**2 + y_shift**2 <= max_magnitude_squared

    x_shift = int(x_shift)
    y_shift = int(y_shift)
    return x_shift, y_shift


def apply_dead_zone(x, y):
    """Takes in integers x and y, which are stick inputs in the integer Melee representation
    i.e. each coordinate is between -80 and 80 inclusive, magnitude of the input <= 80
    Returns The input in the same representation but with the dead zones for each axis applied.
    """
    dead_zone_size = DEAD_ZONE
    if dead_zone_size > x > -dead_zone_size:
        x_out = 0
    else:
        x_out = x
    if dead_zone_size > y > -dead_zone_size:
        y_out = 0
    else:
        y_out = y

    return int(x_out), int(y_out)


def xy_to_angle(x, y):
    """Takes in coordinates x and y and returns the positive angle in degrees between that vector and the positive
    x-axis
    """
    if x == 0:
        if y > 0:
            input_angle = 90
        elif y < 0:
            input_angle = 270
        else:
            input_angle = None
    else:
        input_angle = np.rad2deg(np.arctan(y / x))
        if x < 0:
            input_angle += 180
        elif y < 0:
            input_angle += 360
    return input_angle


def get_di_effectiveness(kb_angle, x, y):
    """Takes in a knockback angle and a DI input in the integer Melee representation
    i.e. each coordinate is between -80 and 80 inclusive, magnitude of the input <= 80
    This function does not apply dead zones, use apply_dead_zone first to get an accurate-to-Melee result.
    Returns the signed DI effectiveness as a float between -1 and +1, where positive values represent a clockwise
    rotation of the knockback, and negative values represent an anticlockwise rotation.
    Multiply this value by 18 degrees to get the actual angle change to the knockback."""
    input_angle = xy_to_angle(x, y)
    if input_angle is None:
        return 0
    angle_difference = input_angle - kb_angle
    if angle_difference > 180:
        angle_difference -= 360

    if isinstance(x, int) and isinstance(y, int):
        x /= MAX_MAGNITUDE
        y /= MAX_MAGNITUDE
    else:
        raise Exception("Input to get_di_effectiveness was not int")

    input_mag = (x ** 2 + y ** 2) ** 0.5
    p_distance_squared = (np.sin(np.deg2rad(angle_difference)) * input_mag) ** 2
    signed_effectiveness = p_distance_squared * np.sign(angle_difference)

    return signed_effectiveness


def get_di_angle_change(kb_angle, x, y):
    """Takes in a knockback angle and a DI input in the integer Melee representation
    i.e. each coordinate is between -80 and 80 inclusive, magnitude of the input <= 80
    This function does not apply dead zones, use apply_dead_zone first to get an accurate-to-Melee result.
    Returns the angle change to the knockback caused by this DI input.
    """
    max_di = MAX_DI
    p_distance_squared = get_di_effectiveness(kb_angle, x, y)
    di_angle_change = p_distance_squared * max_di
    return di_angle_change


def get_di_kb_angle(kb_angle, x, y):
    """Takes in a knockback angle and a DI input in the integer Melee representation
    i.e. each coordinate is between -80 and 80 inclusive, magnitude of the input <= 80
    This function does not apply dead zones, use apply_dead_zone first to get an accurate-to-Melee result.
    Returns the new knockback angle after the DI is applied.
    """
    return kb_angle + get_di_angle_change(kb_angle, x, y)


def di_heatmap(kb_angle, sign=False):
    """Takes in a knockback angle, and an optional boolean to determine whether to include the sign on the output.
    Returns a 256 by 256 numpy array where the [x, y] element of the array is the effectiveness of the DI, as a
    proportion of the maximum 18 degrees, for the raw input (x, y) when kb_angle is applied.
    """
    n = INPUT_SIZE
    raw_input = [[(0, 0) for _ in range(n)] for __ in range(n)]
    melee_input = raw_input.copy()
    dz_input = raw_input.copy()
    heatmap = np.zeros((n, n))
    for x in range(n):
        for y in range(n):
            raw_input[x][y] = (x, y)
            melee_input[x][y] = raw_to_melee(x, y)
            dz_input[x][y] = apply_dead_zone(*melee_input[x][y])
            heatmap[y, x] = get_di_effectiveness(kb_angle, *dz_input[x][y])
    if not sign:
        heatmap = np.abs(heatmap)
    return np.round(heatmap, 4)


def possible_inputs():
    """Returns a 256 by 256 numpy array where the [x, y] indexed element is equal to 0 if the raw input (x, y)
     gets shortened down in the Melee representation of the input, or 1 otherwise.
     Creating an image from this array shows the shape of all possible inputs in the Melee representation.
     """
    grid = np.zeros((INPUT_SIZE, INPUT_SIZE))
    for x in range(INPUT_SIZE):
        for y in range(INPUT_SIZE):
            if (x-128)**2 + (y-128)**2 <= MAX_MAG_SQUARE:
                grid[x, y] = 1
    return grid


def process_raw_input(x, y):
    """Takes in raw inputs x and y and applies both the Melee level processing and the dead zones.
    Returns a tuple containing the integer coordinates in the integer Melee representation after dead zones are applied
    """
    nx, ny = raw_to_melee(x, y)
    nx, ny = apply_dead_zone(nx, ny)
    return nx, ny


def get_kb_line_points(kb_angle):
    """Takes in a knockback angle and returns a tuple of lists.
    The first list is x coordinates and the second is y coordinates. When plotted against each other this represents a
    line of length 128*sqrt(2) starting at the raw input origin (128, 128), at the angle kb_angle to the positive x axis
    This is used to represent the knockback angle on a DI heatmap.
    """
    def unit2raw(n):
        return n * 2 ** 0.5 * ORIGIN + ORIGIN

    kb_x = unit2raw(np.cos(np.deg2rad(kb_angle)))
    kb_y = unit2raw(np.sin(np.deg2rad(kb_angle)))
    xs = [ORIGIN, kb_x]
    ys = [ORIGIN, kb_y]
    return xs, ys


def plot_possible_inputs():
    """Plots the possible stick inputs before dead zones within Melee on the 256 by 256 raw input grid.
    Accepted values are in white, while non-accepted values are in black. Black values would be shortened down to
    a white value in-game.
    """
    data = possible_inputs()
    print(np.count_nonzero(data))
    plt.imshow(data, cmap='gray', interpolation=None)
    plt.show()


def plot_heat_map(kb_angle, sign=False, animated=False):
    """Takes in a knockback angle and creates a heatmap of the DI effectiveness for each input on the 256 by 256 raw
    input grid.
    If sign is True then clockwise DI will be in red and anticlockwise in blue.
    If sign is False, only the absolute vale of the DI effectiveness is considered,
    with strong DI in red and weak DI in blue.
    Returns a tuple of figure elements as follows:
    (The figure itself,
    the heatmap itself,
    the line representing the knockback,
    the line representing the octagonal stick gate)
     """
    xs, ys = get_kb_line_points(kb_angle)
    gate_xs = GATE_XS
    gate_ys = GATE_YS

    if sign:
        c = 'seismic'
        v_min = -1
    else:
        c = 'jet'
        v_min = 0
    hm = di_heatmap(kb_angle, sign=sign)
    fig, ax = plt.subplots()
    fig.set_size_inches(16, 9)
    visual = ax.imshow(hm, cmap=c, interpolation='none', vmin=v_min, vmax=1, origin='lower', animated=animated)
    fig.colorbar(visual, ax=ax)
    gate, = ax.plot(gate_xs, gate_ys)
    kb_line, = ax.plot(xs, ys)
    ax.set_xlim(0, INPUT_SIZE)
    ax.set_ylim(0, INPUT_SIZE)
    return fig, visual, kb_line, gate


def heatmap_animation(start_ang=0, end_ang=360, filename="heatmap.mp4"):
    """Creates and saves an animation showing the DI heatmap created by plot_heat_map
    for each knockback angle from start_ang to end_ang, both in degrees.
    The knockback rotates clockwise, showing each integer degree angle for 1 frame.
    The animation is saved with the file name filename.
    """
    fig, visual, kb_line, gate = plot_heat_map(start_ang, animated=True)

    def update_fig(frame):
        ang = frame + start_ang
        visual.set_array(di_heatmap(ang))
        xs, ys = get_kb_line_points(ang)
        kb_line.set_xdata(xs)
        kb_line.set_ydata(ys)
        return visual, kb_line, gate

    ani = animation.FuncAnimation(fig, update_fig, end_ang, blit=True, interval=16.6667)
    ani.save(filename, fps=60, bitrate=12000, dpi=120)


def count_angles(only_gate=False):
    """Returns a tuple of 2 elements.
    The first is a set with elements of type fractions.Fraction, containing the fraction y/x for each input possible
    in the dead zoned integer representation of a Melee input in the lower left quadrant.
    Inputs of angle 180 degrees are allowed while 270 degrees are not, so that exactly 1 quarter of inputs are used.
    The second element of the tuple is the size of this set multiplied by 4, giving the number of unique angles allowed
    in Melee when dead zones are considered.
    If only_gate is True, only inputs that have been shortened by raw_to_melee are considered.
    """
    tans = set()
    for x in range(ORIGIN):
        for y in range(ORIGIN):
            x1, y1 = raw_to_melee(x, y)
            x2, y2 = apply_dead_zone(x1, y1)
            if (not only_gate) or (only_gate and (x-128)**2 + (y-128)**2 >= MAX_MAG_SQUARE):
                if x2 == 0:
                    pass
                else:
                    tans.add(fractions.Fraction(y2, x2))
    num_angles = len(tans) * 4
    return tans, num_angles


def angle_count_stuff():
    tans, angles = count_angles(True)
    print(angles)
    for tan in tans:
        angle = np.rad2deg(np.arctan(float(tan)))
        for i in range(4):
            plt.plot(*get_kb_line_points(angle + 90 * i))
    plt.show()


def main():
    plot_heat_map(45)
    plt.show()
    # heatmap_animation()
    # plot_possible_inputs()
    # angle_count_stuff()


if __name__ == '__main__':
    main()
