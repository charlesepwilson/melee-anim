import numpy as np
import matplotlib.pyplot as plt
import stick_and_di

FOX = {'weight': 75,
       'fall_speed': 2.8,
       'gravity': 0.23
       }

EXAMPLE_HITBOX = {'kb_angle': 45,
                  'attack_dmg': 17,
                  'bkb': 70,
                  'kbg': 50
                  }
CURRENT_PERCENT = 100 - EXAMPLE_HITBOX['attack_dmg']


def get_knockback(current_dmg, weight, attack_dmg, bkb, kbg, staled_dmg=None):
    if staled_dmg is None:
        staled_dmg = attack_dmg
    victim_dmg = current_dmg + staled_dmg
    g = kbg / 100
    w = weight / 100

    kb = bkb + g * (
                    (1.4 * (attack_dmg + 2) * (staled_dmg + np.floor(victim_dmg)) * (2.0 - (2 * w / (1 + w))) / 20) + 18
                    )

    if kb > 2500:
        kb = 2500
    return kb


def get_path(kb_angle, kb_strength, fall_speed, gravity, di=(0, 0)):
    angle_change = stick_and_di.get_di_angle_change(kb_angle, *di)
    kb_angle_di = kb_angle + angle_change

    kb_angle_rad = np.deg2rad(kb_angle_di)
    unit = np.exp(kb_angle_rad * 1j)
    decay = 0.051 * unit

    gravity_frames = int(fall_speed / gravity)
    last_gravity_frame = fall_speed % gravity
    hit_stun = int(kb_strength * 0.4)
    position = 0 + 0j
    fall_velocity = 0 + 0j
    kb_vel_start = kb_strength * 0.03 * unit
    kb_vel = kb_vel_start.copy()
    pos_list = [0 + 0j]
    for i in range(hit_stun):
        # Apply decay
        kb_vel -= decay

        if np.sign(kb_vel.real) != np.sign(kb_vel_start.real):
            kb_vel = kb_vel.imag * 1j
        if np.sign(kb_vel.imag) != np.sign(kb_vel_start.imag):
            kb_vel = kb_vel.real
        # Apply gravity
        if i < gravity_frames:
            fall_velocity -= gravity * 1j
        elif i == gravity_frames:
            fall_velocity -= last_gravity_frame * 1j
        position += fall_velocity + kb_vel

        pos_list.append(position)
    return pos_list


def get_path_from_hitbox_char(current_dmg, kb_angle, attack_dmg, bkb, kbg, weight=100, fall_speed=1.8, gravity=0.1):
    kb_strength = get_knockback(current_dmg, weight, attack_dmg, bkb, kbg)
    return get_path(kb_angle, kb_strength, fall_speed, gravity)


def main():
    path = get_path_from_hitbox_char(CURRENT_PERCENT, **EXAMPLE_HITBOX, **FOX)
    print(path[0])
    xs = [i.real for i in path]
    ys = [i.imag for i in path]
    plt.plot(xs, ys)
    plt.xlim(-224, 224)
    plt.ylim(-100.8, 200)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()


if __name__ == '__main__':
    main()
