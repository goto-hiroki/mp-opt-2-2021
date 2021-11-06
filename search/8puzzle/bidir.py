"""双方向探索"""
from time import time

from graphviz import Digraph

from base import Action, Seq, State


def bidir(initial_state: State, goal_seq: Seq, show_all: bool = False) -> Digraph:
    """双方向探索

    Args:
        initial_state (State): 初期状態
        goal_seq (Seq): 目標状態の盤面
        show_all (bool, optional): 展開された全てのノードを表示するか否か. Defaults to False.

    Returns:
        Digraph: グラフ(graphviz)
    """
    if initial_state.seq == goal_seq:
        # 初期状態と目標状態が同じ場合
        graph = Digraph()
        graph.node(initial_state.name,
                   label=initial_state.label(), shape='record')
        return graph

    start_time = time()

    goal_state = State(goal_seq, 0, Action.NONE, None)  # 目標状態

    # 初期状態側・目標状態側から探索した辺境（端）
    start_frontier_list: list[State] = [initial_state]
    goal_frontier_list: list[State] = [goal_state]

    extension_count = 0  # 展開した回数
    # 可視化用に記録しておく辞書
    start_state_dict: dict[str, tuple(State, int)] = {
        initial_state.name: (initial_state, None)
    }
    goal_state_dict: dict[str, tuple(State, int)] = {
        goal_state.name: (goal_state, None)
    }
    meet = False  # 出会ったかどうかのフラグ
    while not meet:
        # 初期状態側から探索
        new_start_frontier_list: list[State] = []
        for start_frontier in start_frontier_list:
            # 展開回数を更新
            start_state_dict[start_frontier.name] = (
                start_frontier, extension_count)
            extension_count += 1
            # 展開
            start_frontier_children = start_frontier.extend()
            for start_frontier_child in start_frontier_children:
                # 展開して出現したノードを記録
                start_state_dict[start_frontier_child.name] = (
                    start_frontier_child, None)
            # 出会ったのか多対多で判定
            for start_frontier_child in start_frontier_children:
                for goal_frontier in goal_frontier_list:
                    if start_frontier_child.seq == goal_frontier.seq:
                        meet = True
                        meet_start_frontier = start_frontier_child
                        meet_goal_frontier = goal_frontier
                        break
                if meet:
                    break
            if meet:
                # 出会った場合は展開を終了
                break
            else:
                new_start_frontier_list.extend(start_frontier_children)
        if not meet:
            # まだ出会っていない場合は辺境の状態を更新
            start_frontier_list = new_start_frontier_list
        else:
            break

        # 目標状態側から探索
        new_goal_frontier_list: list[State] = []
        for goal_frontier in goal_frontier_list:
            # 展開回数を更新
            goal_state_dict[goal_frontier.name] = (
                goal_frontier, extension_count)
            extension_count += 1
            # 展開
            goal_frontier_children = goal_frontier.extend()
            for goal_frontier_child in goal_frontier_children:
                # 展開して出現したノードを記録
                goal_state_dict[goal_frontier_child.name] = (
                    goal_frontier_child, None)
            # 出会ったのか多対多で判定
            for goal_frontier_child in goal_frontier_children:
                for start_frontier in start_frontier_list:
                    if goal_frontier_child.seq == start_frontier.seq:
                        meet = True
                        meet_start_frontier = start_frontier
                        meet_goal_frontier = goal_frontier_child
                        break
                if meet:
                    break
            if meet:
                # 出会った場合は展開を終了
                break
            else:
                new_goal_frontier_list.extend(goal_frontier_children)
        if not meet:
            # まだ出会っていない場合は辺境の状態を更新
            goal_frontier_list = new_goal_frontier_list

    end_time = time()
    print(f"計算時間:\t{(end_time-start_time)*1e+3:.3f} ms")
    print(f"展開回数:\t{extension_count}")
    print(f"解の経路コスト:\t{meet_start_frontier.depth+meet_goal_frontier.depth}")

    # グラフで可視化する
    graph = Digraph(name="双方向探索")
    if show_all:
        # 全てのノードを表示
        for state, count in start_state_dict.values():
            if state.name != meet_start_frontier.name:
                graph.node(state.name, label=state.label(
                    count), shape='record', color='red')
                if state.parent is not None:
                    graph.edge(state.parent.name, state.name)
        for state, count in goal_state_dict.values():
            graph.node(state.name, label=state.label(
                count), shape='record', color='blue')
            if state.parent is not None:
                graph.edge(state.name, state.parent.name)
    else:
        # 出会った状態から初期状態まで遡って表示
        state_name = start_state_dict.get(
            meet_start_frontier.name)[0].parent.name
        while True:
            state, count = start_state_dict.get(state_name)
            graph.node(state.name, label=state.label(
                count), shape='record', color='red')
            if state.parent is None:
                # 初期状態に到達したのでループを抜ける
                break
            graph.edge(state.parent.name, state.name)
            state_name = state.parent.name
        # 出会った状態から目標状態まで遡って表示
        state_name = meet_goal_frontier.name
        while True:
            state, count = goal_state_dict.get(state_name)
            graph.node(state.name, label=state.label(
                count), shape='record', color='blue')
            if state.parent is None:
                # 目標状態に到達したのでループを抜ける
                break
            graph.edge(state.name, state.parent.name)
            state_name = state.parent.name
    graph.node(meet_goal_frontier.name, label=meet_goal_frontier.label(
    ), shape='record', color='purple')
    graph.edge(meet_start_frontier.parent.name, meet_goal_frontier.name)

    return graph


if __name__ == '__main__':
    initial_state = State((2, 8, 3, 1, 6, 4, 7, 0, 5), 0, Action.NONE, None)
    goal_seq: Seq = (1, 2, 3, 8, 0, 4, 7, 6, 5)
    graph = bidir(initial_state, goal_seq, True)
    graph.view()
