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


def raw_to_melee(x, y):
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


def dead_zone(x, y):
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
    max_di = MAX_DI
    p_distance_squared = get_di_effectiveness(kb_angle, x, y)
    di_angle_change = p_distance_squared * max_di
    return di_angle_change


def get_di_kb_angle(kb_angle, x, y):
    return kb_angle + get_di_angle_change(kb_angle, x, y)


def di_heatmap(kb_angle, sign=False):
    n = INPUT_SIZE
    raw_input = [[(0, 0) for _ in range(n)] for __ in range(n)]
    melee_input = raw_input.copy()
    dz_input = raw_input.copy()
    heatmap = np.zeros((n, n))
    for x in range(n):
        for y in range(n):
            raw_input[x][y] = (x, y)
            melee_input[x][y] = raw_to_melee(x, y)
            dz_input[x][y] = dead_zone(*melee_input[x][y])
            heatmap[y, x] = get_di_effectiveness(kb_angle, *dz_input[x][y])
    if not sign:
        heatmap = np.abs(heatmap)
    return np.round(heatmap, 4)


def possible_inputs():
    grid = np.zeros((INPUT_SIZE, INPUT_SIZE))
    for x in range(INPUT_SIZE):
        for y in range(INPUT_SIZE):
            if (x-128)**2 + (y-128)**2 <= MAX_MAG_SQUARE:
                grid[x, y] = 1
    return grid


def process_raw_input(x, y):
    nx, ny = raw_to_melee(x, y)
    nx, ny = dead_zone(nx, ny)
    return nx, ny


def get_kb_line_points(kb_angle):
    def unit2raw(n):
        return n * 2 ** 0.5 * ORIGIN + ORIGIN

    kb_x = unit2raw(np.cos(np.deg2rad(kb_angle)))
    kb_y = unit2raw(np.sin(np.deg2rad(kb_angle)))
    xs = [ORIGIN, kb_x]
    ys = [ORIGIN, kb_y]
    return xs, ys


def plot_possible_inputs():
    data = possible_inputs()
    print(np.count_nonzero(data))
    plt.imshow(data, cmap='gray', interpolation=None)
    plt.show()


def plot_heat_map(kb_angle, sign=False, print_m=False, animated=False):

    xs, ys = get_kb_line_points(kb_angle)
    gate_xs = [233, 206, 125, 55, 32, 56, 131, 210, 233]
    gate_ys = [129, 44, 22, 50, 125, 202, 227, 205, 129]

    if sign:
        c = 'seismic'
        v_min = -1
    else:
        c = 'jet'
        v_min = 0
    hm = di_heatmap(kb_angle, sign=sign)
    if print_m:
        print('minimum = ', np.min(hm[hm.nonzero()]))
        print('maximum = ', np.max(hm))
    fig, ax = plt.subplots()
    fig.set_size_inches(16, 16)
    visual = ax.imshow(hm, cmap=c, interpolation='none', vmin=v_min, vmax=1, origin='lower', animated=animated)
    fig.colorbar(visual, ax=ax)
    gate, = ax.plot(gate_xs, gate_ys)
    kb_line, = ax.plot(xs, ys)
    ax.set_xlim(0, INPUT_SIZE)
    ax.set_ylim(0, INPUT_SIZE)
    return fig, visual, kb_line, gate


def heatmap_animation(start_ang=0, end_ang=360):
    fig, visual, kb_line, gate = plot_heat_map(start_ang, animated=True)

    def update_fig(frame):
        ang = frame + start_ang
        visual.set_array(di_heatmap(ang))
        xs, ys = get_kb_line_points(ang)
        kb_line.set_xdata(xs)
        kb_line.set_ydata(ys)
        return visual, kb_line, gate

    ani = animation.FuncAnimation(fig, update_fig, end_ang, blit=True, interval=16.6667)
    ani.save("heatmap.mp4", fps=60, bitrate=12000)


def count_angles(only_gate=False):
    tans = set()
    for x in range(ORIGIN):
        for y in range(ORIGIN):
            x1, y1 = raw_to_melee(x, y)
            x2, y2 = dead_zone(x1, y1)
            if (only_gate and x2**2 + y2**2 >= MAX_MAG_SQUARE) or (not only_gate):
                if x2 == 0:
                    pass
                else:
                    tans.add(fractions.Fraction(y2, x2))
    num_angles = len(tans) * 4
    return tans, num_angles


def angle_count_stuff():
    tans, angles = count_angles(False)
    print(angles)
    for tan in tans:
        angle = np.rad2deg(np.arctan(float(tan)))
        for i in range(4):
            plt.plot(*get_kb_line_points(angle + 90 * i))
    plt.show()


def main():
    # plot_heat_map(45)
    # plt.show()
    heatmap_animation()
    # plot_possible_inputs()
    # angle_count_stuff()


if __name__ == '__main__':
    main()
