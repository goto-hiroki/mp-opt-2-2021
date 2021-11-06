"""幅優先探索"""
from collections import deque
from time import time

import matplotlib.pyplot as plt
from matplotlib import animation

from base import Pos, State, get_count_artist, get_first_artist


def bfs(initial_state: State, goal_pos: Pos, disp: bool = True) -> animation.ArtistAnimation:
    """幅優先探索

    Args:
        initial_state (State): 初期状態
        goal_pos (Pos): 目標状態の位置
        disp (bool, optional): 図示するか否か. Defaults to True.

    Returns:
        animation.ArtistAnimation: 探索の様子と解の経路のアニメーション
    """

    fig = plt.figure()
    artists = [get_first_artist(initial_state, goal_pos)]
    extension_artists = []

    start_time = time()

    q = deque([initial_state])  # キュー
    pos_set: set[Pos] = {initial_state.pos}  # 繰り返し状態を回避するための訪れた場所の集合

    extension_count = 0  # 展開した回数
    while True:
        state = q.popleft()  # キューの先頭から取り出す
        if disp:
            extension_artist = get_count_artist(state.pos, extension_count)
            extension_artists.append(extension_artists[-1]+extension_artist
                                    if len(extension_artists) > 0 else extension_artist)
            artists.append(
                artists[0] + state.get_extending_position_artist() + extension_artists[-1])

        if state.pos == goal_pos:
            # 目標状態に到達したのでループを抜ける
            break
        # 子ノードをキューに追加する
        children = [child for child in state.extend()
                    if child.pos not in pos_set]
        for child in children:
            pos_set.add(child.pos)
        q.extend(children)
        extension_count += 1

    end_time = time()
    print(f"計算時間:\t{(end_time-start_time)*1e+3:.3f} ms")
    print(f"展開回数:\t{extension_count}")
    print(f"解の経路コスト:\t{state.depth}")

    # 目標状態から初期状態まで遡って表示
    path = state.path()
    order_artists = []
    for i, state in enumerate(path):
        order_artist = get_count_artist(state.pos, i)
        order_artists.append(order_artists[-1]+order_artist
                             if len(order_artists) > 0 else order_artist)
        artists.append(
            artists[0] + state.get_current_position_artist() + order_artists[-1])

    return animation.ArtistAnimation(fig, artists)


if __name__ == '__main__':
    initial_state = State(((1, 3), (2, 3)), 0, None)
    goal_pos: Pos = ((4, 7), (5, 7))
    ani = bfs(initial_state, goal_pos)
    from os import path
    meth = path.splitext(path.basename(__file__))[0]
    ani.save(f'{meth}.gif', writer="imagemagick")
    ani.save(f'{meth}.mp4', writer="ffmpeg")
