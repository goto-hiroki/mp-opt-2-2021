"""幅優先探索"""
from collections import deque
from time import time

from graphviz import Digraph

from base import Action, Seq, State


def bfs(initial_state: State, goal_seq: Seq, show_all: bool = False) -> Digraph:
    """幅優先探索

    Args:
        initial_state (State): 初期状態
        goal_seq (Seq): 目標状態の盤面
        show_all (bool, optional): 展開された全てのノードを表示するか否か. Defaults to False.

    Returns:
        Digraph: グラフ(graphviz)
    """
    start_time = time()

    q = deque([initial_state])  # キュー

    extension_count = 0  # 展開した回数
    state_dict: dict[str, tuple(State, int)] = {}
    while True:
        state = q.popleft()  # キューの先頭から取り出す
        state_dict[state.name] = (state, extension_count)
        if state.seq == goal_seq:
            # 目標状態に到達したのでループを抜ける
            break
        # 子ノードをキューに追加する
        children = state.extend()
        q.extend(children)
        extension_count += 1

    end_time = time()
    print(f"計算時間:\t{(end_time-start_time)*1e+3:.3f} ms")
    print(f"展開回数:\t{extension_count}")
    print(f"解の経路コスト:\t{state.depth}")

    # グラフで可視化する
    graph = Digraph(name="幅優先探索")
    if show_all:
        # 全てのノードを表示
        for state, extension_count in state_dict.values():
            graph.node(state.name, label=state.label(extension_count), shape='record',
                       color=('blue' if state.seq == goal_seq else 'black'))
            if state.parent is not None:
                graph.edge(state.parent.name, state.name)
    else:
        # 目標状態から初期状態まで遡って表示
        state_name = state.name
        while True:
            state, extension_count = state_dict.get(state_name)
            graph.node(state.name, label=state.label(
                extension_count), shape='record')
            if state.parent is None:
                # 初期状態に到達したのでループを抜ける
                break
            graph.edge(state.parent.name, state.name)
            state_name = state.parent.name
    return graph


if __name__ == '__main__':
    initial_state = State((2, 8, 3, 1, 6, 4, 7, 0, 5), 0, Action.NONE, None)
    goal_seq: Seq = (1, 2, 3, 8, 0, 4, 7, 6, 5)
    graph = bfs(initial_state, goal_seq, True)
    graph.view()
