"""LRTA*探索"""
import random
import sys
from time import time

import matplotlib.pyplot as plt
from matplotlib import animation

from base import Pos, State, get_count_artist, get_first_artist


def lrta_star(initial_state: State, goal_pos: Pos, h_dict: dict[Pos, int], disp: bool = True) -> tuple[animation.ArtistAnimation, dict[Pos, int]]:
    """LRTA*探索

    Args:
        initial_state (State): 初期状態
        goal_pos (Pos): 目標状態の位置
        h_dict (dict[Pos, int]): 推定コスト・評価値の辞書
        disp (bool, optional): 図示するか否か. Defaults to True.

    Returns:
        animation.ArtistAnimation: 探索の様子と解の経路のアニメーション
    """
    fig = plt.figure()
    artists = [get_first_artist(initial_state, goal_pos)]

    start_time = time()

    extension_count = 0  # 展開した回数
    current_state = initial_state
    while True:
        if disp:
            h_artists = []
            for pos, h in h_dict.items():
                h_artists.extend(get_count_artist(pos, h))
            artists.append(
                artists[0] + current_state.get_current_position_artist()+h_artists)

        if current_state.pos == goal_pos:
            # 目標状態に到達したのでループを抜ける
            break

        # 隣接状態の評価・選択
        min_f = sys.maxsize
        next_states: list[State] = []
        for adjacent_state in current_state.extend():
            if adjacent_state.pos in h_dict:
                h = h_dict.get(adjacent_state.pos)
            else:
                h = adjacent_state.heuristic(goal_pos)
            f = 1 + h
            if f <= min_f:
                min_f = f
                next_states.append(adjacent_state)

        # 一貫性の保持
        h_dict[current_state.pos] = min_f

        # 行為の実現
        current_state: State = random.choice(next_states)
        extension_count += 1

    end_time = time()
    print(f"計算時間:\t{(end_time-start_time)*1e+3:.3f} ms")
    print(f"展開回数:\t{extension_count}")
    print(f"解の経路コスト:\t{current_state.depth}")

    return animation.ArtistAnimation(fig, artists), h_dict


if __name__ == '__main__':
    initial_state = State(((1, 3), (2, 3)), 0, None)
    goal_pos: Pos = ((4, 7), (5, 7))
    from os import path
    meth = path.splitext(path.basename(__file__))[0]
    h_dict = {}
    for k in range(3):
        ani, h_dict = lrta_star(initial_state, goal_pos, h_dict)
        # ani.save(f'{meth}_{k}.gif', writer="imagemagick")
        ani.save(f'{meth}_{k}.mp4', writer="ffmpeg")
