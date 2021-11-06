"""欲張り探索"""
import heapq
from time import time

from graphviz import Digraph

from base import Action, Seq, State


def greedy(initial_state: State, goal_seq: Seq, show_all: bool = False) -> Digraph:
    """欲張り探索
    ヒューリスティック関数はゴール位置にないタイルの数

    Args:
        initial_state (State): 初期状態
        goal_seq (Seq): 目標状態の盤面
        show_all (bool, optional): 展開された全てのノードを表示するか否か. Defaults to False.

    Returns:
        Digraph: グラフ(graphviz)
    """
    start_time = time()

    # 状態とヒューリスティック関数の値のタプルをキューに追加
    q = [(initial_state.heuristic1(goal_seq), initial_state)]
    heapq.heapify(q)

    extension_count = 0  # 展開した回数
    state_dict: dict[str, tuple(State, int)] = {}  # 可視化のために状態を記録する辞書
    while True:
        _h, state = heapq.heappop(q)  # ヒューリスティック関数が最小の状態を取り出す
        state_dict[state.name] = (state, extension_count)
        if state.seq == goal_seq:
            # 目標状態に到達したのでループを抜ける
            break
        # 子ノードをキューに追加する
        children = state.extend()
        for child in children:
            heapq.heappush(q, (child.heuristic1(goal_seq), child))
        extension_count += 1

    end_time = time()
    print(f"計算時間:\t{(end_time-start_time)*1e+3:.3f} ms")
    print(f"展開回数:\t{extension_count}")
    print(f"解の経路コスト:\t{state.depth}")

    # グラフで可視化する
    graph = Digraph(name="欲張り探索")
    if show_all:
        # 全てのノードを表示
        for state, count in state_dict.values():
            graph.node(state.name, label=state.label(count, f'h={state.heuristic1(goal_seq)}'), shape='record',
                       color=('blue' if state.seq == goal_seq else 'black'))
            if state.parent is not None:
                graph.edge(state.parent.name, state.name)
    else:
        # 目標状態から初期状態まで遡って表示
        state_name = state.name
        while True:
            state, count = state_dict.get(state_name)
            graph.node(state.name, label=state.label(
                count, f'h={state.heuristic1(goal_seq)}'), shape='record')
            if state.parent is None:
                # 初期状態に到達したのでループを抜ける
                break
            graph.edge(state.parent.name, state.name)
            state_name = state.parent.name
    return graph


if __name__ == '__main__':
    initial_state = State((2, 8, 3, 1, 6, 4, 7, 0, 5), 0, Action.NONE, None)
    goal_seq: Seq = (1, 2, 3, 8, 0, 4, 7, 6, 5)
    graph = greedy(initial_state, goal_seq, True)
    graph.view()
