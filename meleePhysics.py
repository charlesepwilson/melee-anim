import numpy as np

FOX = {
    'weight': 80,
    'fall_speed': 100,
    'gravity': 0.5
}

EXAMPLE_HITBOX = {'kb_angle': 45,
                  'attack_dmg': 15,
                  'bkb': 50,
                  'kbg': 50
                  }


def get_knockback(current_dmg, attack_dmg, bkb, kbg, weight):
    # todo implement knockback formula
    return 100


def get_path(kb_angle, kb_strength, fall_speed, gravity):
    unit = np.exp(kb_angle * 1j)
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


def get_path_from_hitbox_char(current_dmg, kb_angle, attack_dmg, bkb, kbg, weight, fall_speed, gravity):
    kb_strength = get_knockback(current_dmg, attack_dmg, bkb, kbg, weight)
    return get_path(kb_angle, kb_strength, fall_speed, gravity)


if __name__ == '__main__':
    print(get_path_from_hitbox_char(30, **EXAMPLE_HITBOX, **FOX))
