"""A*探索"""
import heapq
from functools import partial
from time import time
from typing import Callable

from graphviz import Digraph

from base import Action, Seq, State


def a_star(initial_state: State, goal_seq: Seq, heuristic: Callable[[State], int], show_all: bool = False) -> Digraph:
    """A*探索

    Args:
        initial_state (State): 初期状態
        goal_seq (Seq): 目標状態の盤面
        heuristic (Callable[[State], int]): ヒューリスティック関数
        show_all (bool, optional): 展開された全てのノードを表示するか否か. Defaults to False.

    Returns:
        Digraph: グラフ(graphviz)
    """
    def f(state: State) -> int:
        return state.depth+heuristic(state)

    start_time = time()

    # 状態とfの値のタプルをキューに追加
    q = [(f(initial_state), initial_state)]
    heapq.heapify(q)

    extension_count = 0  # 展開した回数
    state_dict: dict[str, tuple(State, int)] = {}  # 可視化のために状態を記録する辞書
    while True:
        _h, state = heapq.heappop(q)  # fが最小の状態を取り出す
        state_dict[state.name] = (state, extension_count)
        if state.seq == goal_seq:
            # 目標状態に到達したのでループを抜ける
            break
        # 子ノードをキューに追加する
        children = state.extend()
        for child in children:
            heapq.heappush(q, (f(child), child))
        extension_count += 1

    end_time = time()
    print(f"計算時間:\t{(end_time-start_time)*1e+3:.3f} ms")
    print(f"展開回数:\t{extension_count}")
    print(f"解の経路コスト:\t{state.depth}")

    # グラフで可視化する
    graph = Digraph(name="A*探索")
    if show_all:
        # 全てのノードを表示
        for state, count in state_dict.values():
            graph.node(state.name, label=state.label(count, f'f={f(state)}<BR/>g={state.depth}<BR/>h={heuristic(state)}'), shape='record',
                       color=('blue' if state.seq == goal_seq else 'black'))
            if state.parent is not None:
                graph.edge(state.parent.name, state.name)
    else:
        # 目標状態から初期状態まで遡って表示
        state_name = state.name
        while True:
            state, count = state_dict.get(state_name)
            graph.node(state.name, label=state.label(
                count, f'f={f(state)}<BR/>g={state.depth}<BR/>h={heuristic(state)}'), shape='record')
            if state.parent is None:
                # 初期状態に到達したのでループを抜ける
                break
            graph.edge(state.parent.name, state.name)
            state_name = state.parent.name
    return graph


def heuristic1(state: State, goal_seq: Seq) -> int:
    """ヒューリスティック関数（ゴール位置にないタイルの数）"""
    return state.heuristic1(goal_seq)


def heuristic2(state: State, goal_seq: Seq) -> int:
    """ヒューリスティック関数（ゴール状態からのタイルの距離の和）"""
    return state.heuristic2(goal_seq)


if __name__ == '__main__':
    initial_state = State((2, 8, 3, 1, 6, 4, 7, 0, 5), 0, Action.NONE, None)
    goal_seq: Seq = (1, 2, 3, 8, 0, 4, 7, 6, 5)
    graph = a_star(initial_state, goal_seq, partial(
        heuristic2, goal_seq=goal_seq), True)
    graph.view()
