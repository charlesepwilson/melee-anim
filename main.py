import numpy as np
import matplotlib.pyplot as plt

INPUT_SIZE = 256
ORIGIN = INPUT_SIZE / 2
MAX_MAGNITUDE = 80
MAX_MAG_SQUARE = 6400
DEAD_ZONE = 23  # Out of 80, 23 is not included in dead zone
MAX_DI = 18  # degrees


def raw_to_melee(x, y, scaling=None):
    n = ORIGIN
    max_magnitude = MAX_MAGNITUDE
    max_magnitude_squared = MAX_MAG_SQUARE
    x_shift, y_shift = x - n, y - n
    magnitude_squared = x_shift ** 2 + y_shift ** 2

    def shorten(coord, mag):
        output = coord * max_magnitude
        return output // mag

    if magnitude_squared > max_magnitude_squared:
        magnitude = magnitude_squared ** 0.5
        x_shift = shorten(x_shift, magnitude)
        y_shift = shorten(y_shift, magnitude)

    if scaling is not None:
        x_shift = scaling * x_shift / max_magnitude
        y_shift = scaling * x_shift / max_magnitude
    else:
        x_shift = int(x_shift)
        y_shift = int(y_shift)
    return x_shift, y_shift


def dead_zone(x, y):
    n = DEAD_ZONE
    if isinstance(x, int) and isinstance(y, int):
        dead_zone_size = n
    elif isinstance(x, float) and isinstance(y, float):
        dead_zone_size = n / MAX_MAGNITUDE
    else:
        raise Exception("Input to dead_zone was not int or float")

    if dead_zone_size > x > -dead_zone_size:
        x_out = 0
    else:
        x_out = x
    if dead_zone_size > y > -dead_zone_size:
        y_out = 0
    else:
        y_out = y

    return x_out, y_out


def get_di_effectiveness(kb_angle, x, y):
    if isinstance(x, int) and isinstance(y, int):
        x /= MAX_MAGNITUDE
        y /= MAX_MAGNITUDE
    elif isinstance(x, float) and isinstance(y, float):
        pass
    else:
        raise Exception("Input to get_di_effectiveness was not int or float")

    if x == 0:
        if y > 0:
            input_angle = 90
        else:
            input_angle = 270
    else:
        input_angle = np.rad2deg(np.arctan(y / x))
    input_mag = (x ** 2 + y ** 2) ** 0.5
    if x < 0:
        input_angle += 180
    elif y < 0:
        input_angle += 360
    angle_difference = input_angle - kb_angle
    if angle_difference > 180:
        angle_difference -= 360
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


def di_heatmap(kb_angle, sign=True):
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
    return heatmap


def process_raw_input(x, y):
    nx, ny = raw_to_melee(x, y)
    nx, ny = dead_zone(nx, ny)
    return nx, ny


def main():
    kb_angle = 45
    sign = False

    def unit2raw(n):
        return n * 2 ** 0.5 * ORIGIN + ORIGIN

    kb_x = unit2raw(np.cos(np.deg2rad(kb_angle)))
    kb_y = unit2raw(np.sin(np.deg2rad(kb_angle)))
    xs = [ORIGIN, kb_x]
    ys = [ORIGIN, kb_y]

    gate_xs = [233, 206, 125, 55, 32, 56, 131, 210, 233]
    gate_ys = [129, 44, 22, 50, 125, 202, 227, 205, 129]

    if sign:
        c = 'seismic'
        v_min = -1
    else:
        c = 'jet'
        v_min = 0
    plt.imshow(di_heatmap(kb_angle, sign=sign), cmap=c, interpolation='none', vmin=v_min, vmax=1, origin='lower')
    plt.plot(gate_xs, gate_ys)
    plt.plot(xs, ys)
    plt.xlim(0, INPUT_SIZE)
    plt.ylim(0, INPUT_SIZE)
    plt.show()


if __name__ == '__main__':
    main()
