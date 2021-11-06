from enum import Enum
from typing import Literal, Optional

# 8パズル上の数字（0は空きマスを表す）
Digit = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8]
# 8パズルを左上→右上→左下→右下の順に一列に並べたもの
Seq = tuple[Digit, Digit, Digit, Digit, Digit, Digit, Digit, Digit, Digit]


class Action(Enum):
    """行為(数字の移動)を表す列挙型"""
    NONE = 0
    UP = 1
    DOWN = 2
    RIGHT = 3
    LEFT = 4


class State:
    def __init__(self, seq: Seq, depth: int, prev_act: Action, parent: Optional['State']) -> None:
        """状態

        Args:
            seq (Seq): 8パズルを左上→右上→左下→右下の順に一列に並べたもの．空きマスは0で表す．
            depth (int): ルートノードからの深さ
            prev_act (Action): 前回の行為．どう動かしてこの状態になったか．
            parent (State): 親ノード
        """
        self.seq = seq
        self.depth = depth
        self.prev_act = prev_act
        self.parent = parent

    @property
    def name(self) -> str:
        """名前"""
        return str(self.depth)+'\n'+''.join([str(s)+'\n' if i % 3 == 2 else str(s)
                                             for i, s in enumerate(self.seq)])+self.prev_act.name

    def extend(self) -> list['State']:
        """次の状態を展開する"""
        i0 = self.seq.index(0)
        y, x = divmod(i0, 3)  # 空きマスの位置（x: 左→右，y: 上→下）
        pos_action_list: list[tuple[Digit, Action]] = []  # 入れ替えるマスと行為の組のリスト
        if y != 2 and self.prev_act != Action.DOWN:
            # 空きマスを下のマスと入れ替える
            pos_action_list.append((i0+3, Action.UP))
        if y != 0 and self.prev_act != Action.UP:
            # 空きマスを上のマスと入れ替える
            pos_action_list.append((i0-3, Action.DOWN))
        if x != 0 and self.prev_act != Action.LEFT:
            # 空きマスを左のマスと入れ替える
            pos_action_list.append((i0-1, Action.RIGHT))
        if x != 2 and self.prev_act != Action.RIGHT:
            # 空きマスを右のマスと入れ替える
            pos_action_list.append((i0+1, Action.LEFT))
        return [State(tuple(self.seq[pos] if i == i0 else
                            (0 if i == pos else self.seq[i]) for i in range(9)), self.depth+1, action, self)
                for pos, action in pos_action_list]

    def label(self, count: Optional[int] = None, cost: Optional[str] = None) -> str:
        """graphvizでグラフを可視化するときのラベル"""
        label = '{{'+'}|{'.join([
            '|'.join([str(self.seq[i+3*j]) for i in range(3)])
            for j in range(3)
        ])+'}}'
        if count is None and cost is None:
            return label
        labels = [label]
        if count is not None:
            labels.insert(0, f'<B>{count}</B>')
        if cost is not None:
            labels.append(cost)
        return '<'+'|'.join(labels)+'>'

    def heuristic1(self, goal_seq: Seq) -> int:
        """ヒューリスティック関数（ゴール位置にないタイルの数）"""
        h = 8
        for s, g in zip(self.seq, goal_seq):
            if s != 0 and s == g:
                h -= 1
        return h

    def heuristic2(self, goal_seq: Seq) -> int:
        """ヒューリスティック関数（ゴール状態からのタイルの距離の和）"""
        h = 0
        for i in range(1, 9):
            sy, sx = divmod(self.seq.index(i), 3)
            gy, gx = divmod(goal_seq.index(i), 3)
            h += abs(sx-gx)+abs(sy-gy)
        return h

    def __str__(self) -> str:
        return self.name

    def __lt__(self, other):
        """比較関数"""
        if not isinstance(other, State):
            return NotImplemented
        return (self.depth, self.prev_act.value) < (other.depth, other.prev_act.value)
