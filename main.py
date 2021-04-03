import numpy as np
import matplotlib.pyplot as plt
from manim import *
import melee_physics
import stick_and_di


def main():
    print(max(stick_and_di.GATE_YS) - min(stick_and_di.GATE_YS))
    print(max(stick_and_di.GATE_XS) - min(stick_and_di.GATE_XS))


if __name__ == '__main__':
    main()
