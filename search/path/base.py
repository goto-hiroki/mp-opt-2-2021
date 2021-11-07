from typing import Optional

import matplotlib.pyplot as plt

# ロボットの位置 ((i1,j1), (i2,j2))
Pos = tuple[tuple[int, int], tuple[int, int]]


def pos_center(pos: Pos) -> tuple[float, float]:
    """ロボットの中心位置"""
    pos1, pos2 = pos
    return (pos1[0]+pos2[0])/2, (pos1[1]+pos2[1])/2


def get_count_artist(pos: Pos, count: int):
    """数字をmatplotlibで表示"""
    x, y = pos_center(pos)
    return [plt.text(y, x, str(count), ha='center', va='center')]


# 作業環境（0は障害物，1は自由領域）
MAP = (
    (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    (0, 0, 1, 1, 1, 0, 1, 1, 1, 0),
    (0, 0, 1, 1, 1, 0, 1, 1, 1, 0),
    (0, 1, 1, 1, 0, 0, 0, 1, 1, 0),
    (0, 1, 1, 0, 0, 0, 0, 1, 1, 0),
    (0, 1, 0, 0, 0, 0, 0, 1, 1, 0),
    (0, 1, 0, 0, 0, 0, 0, 1, 1, 0),
    (0, 1, 0, 0, 0, 0, 0, 0, 1, 0),
    (0, 1, 0, 0, 0, 0, 0, 1, 1, 0),
    (0, 1, 1, 1, 1, 0, 0, 1, 1, 0),
    (0, 1, 1, 1, 1, 1, 1, 1, 1, 0),
    (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
)


class State:
    def __init__(self, pos: Pos, depth: int, parent: Optional['State']) -> None:
        """ロボットの状態

        Args:
            pos (Pos): 位置．`sorted(pos)`がなされたものとする．
            depth (int): ルートノードからの深さ
            parent (Optional[): 親ノード
        """
        self.pos = pos
        self.depth = depth
        self.parent = parent

    def extend(self) -> list['State']:
        """移動可能な次の状態を展開する"""
        pos_list: list[Pos] = []
        if self.pos[0][0] == self.pos[1][0]:
            # ロボットが横の場合
            left_pos, right_pos = self.pos
            # マップは障害物で囲われているのでロボットが外に出ることはない
            if MAP[right_pos[0]][right_pos[1]+1] == 1:
                # 右に移動
                pos_list.append((right_pos, (right_pos[0], right_pos[1]+1)))
            if MAP[left_pos[0]][left_pos[1]-1] == 1:
                # 左に移動
                pos_list.append(((left_pos[0], left_pos[1]-1), left_pos))
            above_right_free = MAP[right_pos[0]-1][right_pos[1]] == 1
            above_left_free = MAP[left_pos[0]-1][left_pos[1]] == 1
            below_right_free = MAP[right_pos[0]+1][right_pos[1]] == 1
            below_left_free = MAP[left_pos[0]+1][left_pos[1]] == 1
            if above_right_free and above_left_free:
                # 上に移動
                pos_list.append(
                    ((left_pos[0]-1, left_pos[1]), (right_pos[0]-1, right_pos[1])))
            if below_right_free and below_left_free:
                # 下に移動
                pos_list.append(
                    ((left_pos[0]+1, left_pos[1]), (right_pos[0]+1, right_pos[1])))
            if above_right_free:
                # 右上に移動
                pos_list.append(((right_pos[0]-1, right_pos[1]), right_pos))
            if above_left_free:
                # 左上に移動
                pos_list.append(((left_pos[0]-1, left_pos[1]), left_pos))
            if below_right_free:
                # 右下に移動
                pos_list.append((right_pos, (right_pos[0]+1, right_pos[1])))
            if below_left_free:
                # 左下に移動
                pos_list.append((left_pos, (left_pos[0]+1, left_pos[1])))
        else:
            # ロボットが縦の場合
            above_pos, below_pos = self.pos
            if MAP[above_pos[0]-1][above_pos[1]] == 1:
                # 上に移動
                pos_list.append(((above_pos[0]-1, above_pos[1]), above_pos))
            if MAP[below_pos[0]+1][below_pos[1]] == 1:
                # 下に移動
                pos_list.append((below_pos, (below_pos[0]+1, below_pos[1])))
            above_right_free = MAP[above_pos[0]][above_pos[1]+1] == 1
            above_left_free = MAP[above_pos[0]][above_pos[1]-1] == 1
            below_right_free = MAP[below_pos[0]][below_pos[1]+1] == 1
            below_left_free = MAP[below_pos[0]][below_pos[1]-1] == 1
            if above_right_free and below_right_free:
                # 右に移動
                pos_list.append(
                    ((above_pos[0], above_pos[1]+1), (below_pos[0], below_pos[1]+1)))
            if above_left_free and below_left_free:
                # 左に移動
                pos_list.append(
                    ((above_pos[0], above_pos[1]-1), (below_pos[0], below_pos[1]-1)))
            if above_right_free:
                # 右上に移動
                pos_list.append((above_pos, (above_pos[0], above_pos[1]+1)))
            if above_left_free:
                # 左上に移動
                pos_list.append(((above_pos[0], above_pos[1]-1), above_pos))
            if below_right_free:
                # 右下に移動
                pos_list.append((below_pos, (below_pos[0], below_pos[1]+1)))
            if below_left_free:
                # 左下に移動
                pos_list.append(((below_pos[0], below_pos[1]-1), below_pos))
        return [State(pos, self.depth+1, self) for pos in pos_list]

    def heuristic(self, goal_pos: Pos) -> int:
        """ヒューリスティック関数（マンハッタン距離）"""
        current_x, current_y = pos_center(self.pos)
        goal_x, goal_y = pos_center(goal_pos)
        return int(abs(current_x-goal_x)+abs(current_y-goal_y))

    def path(self) -> list['State']:
        """初期状態から現在の状態までの経路"""
        path: list[State] = []
        state = self
        while state is not None:
            path.append(state)
            state = state.parent
        path.reverse()
        return path

    def get_position_artist(self, fmt: str):
        """マーカーをmatplotlibで表示"""
        return plt.plot(self.pos[0][1], self.pos[0][0], fmt) + plt.plot(self.pos[1][1], self.pos[1][0], fmt)

    def get_extending_position_artist(self):
        """展開中を表すマーカー（緑）をmatplotlibで表示"""
        return self.get_position_artist('sg')

    def get_current_position_artist(self):
        """現在位置を表すマーカー（黄）をmatplotlibで表示"""
        return self.get_position_artist('sy')

    def __lt__(self, other):
        """A*で用いる比較関数"""
        if not isinstance(other, State):
            return NotImplemented
        return self.depth < other.depth


def get_first_artist(initial_state: State, goal_pos: Pos):
    """作業環境および初期位置と目標位置をmatplotlibで表示"""
    return [
        plt.imshow(MAP, cmap='gray', aspect='equal'),
        plt.text(initial_state.pos[0][1],
                 initial_state.pos[0][0], 'S', c='blue', ha='center', size='large', va='center'),
        plt.text(initial_state.pos[1][1],
                 initial_state.pos[1][0], 'S', c='blue', ha='center', size='large', va='center'),
        plt.text(goal_pos[0][1],
                 goal_pos[0][0], 'G', c='red', ha='center', size='large', va='center'),
        plt.text(goal_pos[1][1],
                 goal_pos[1][0], 'G', c='red', ha='center', size='large', va='center'),
    ]
