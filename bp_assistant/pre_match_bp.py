from __future__ import annotations

from dataclasses import dataclass, field

from .core import MatchConfig, Operator, PLAYER_A, PLAYER_B, RuleError


MODE_BAN = "ban"
MODE_BLUE = PLAYER_A
MODE_RED = PLAYER_B


@dataclass
class PreMatchBpState:
    """选手赛前 BP 看板状态；Ban 与双方 Pick 均不限制数量。"""

    match_id: str = ""
    match_title: str = ""
    blue_name: str = "蓝方"
    red_name: str = "红方"
    global_banned_operator_ids: set[str] = field(default_factory=set)
    global_banned_branches: set[str] = field(default_factory=set)
    player_banned_operator_ids: list[str] = field(default_factory=list)
    player_banned_branches: set[str] = field(default_factory=set)
    blue_pick_ids: list[str] = field(default_factory=list)
    red_pick_ids: list[str] = field(default_factory=list)

    def apply_config(
        self,
        config: MatchConfig,
        operators: dict[str, Operator] | None = None,
    ) -> None:
        self.match_id = config.match_id
        self.match_title = config.title
        self.blue_name = config.player_a_name or "蓝方"
        self.red_name = config.player_b_name or "红方"
        self.global_banned_operator_ids = set(config.global_banned_operator_ids)
        self.global_banned_branches = set(config.global_banned_branches)
        merged_operator_bans: list[str] = []
        merged_branch_bans: set[str] = set()
        for player in (PLAYER_A, PLAYER_B):
            for operator_id in config.host_banned_operator_ids.get(player, []):
                operator = operators.get(operator_id) if operators else None
                if (
                    operator_id not in self.global_banned_operator_ids
                    and (
                        operator is None
                        or operator.branch not in self.global_banned_branches
                    )
                    and operator_id not in merged_operator_bans
                ):
                    merged_operator_bans.append(operator_id)
            merged_branch_bans.update(config.host_banned_branches.get(player, []))
        self.player_banned_operator_ids = merged_operator_bans
        self.player_banned_branches = merged_branch_bans - self.global_banned_branches
        self.blue_pick_ids = []
        self.red_pick_ids = []

    def is_global_banned(self, operator: Operator) -> bool:
        return (
            operator.operator_id in self.global_banned_operator_ids
            or operator.branch in self.global_banned_branches
        )

    def is_player_banned(self, operator: Operator) -> bool:
        return (
            operator.operator_id in self.player_banned_operator_ids
            or operator.branch in self.player_banned_branches
        )

    def add(self, mode: str, operator: Operator) -> None:
        operator_id = operator.operator_id
        if self.is_global_banned(operator):
            raise RuleError("该干员已被全局 Ban，不能加入赛前 BP")
        if mode == MODE_BAN:
            if operator_id in self.blue_pick_ids or operator_id in self.red_pick_ids:
                raise RuleError("该干员已经被一方 Pick，不能再 Ban")
            if operator_id not in self.player_banned_operator_ids:
                self.player_banned_operator_ids.append(operator_id)
            return
        if mode not in (MODE_BLUE, MODE_RED):
            raise RuleError("未知的 BP 操作模式")
        if self.is_player_banned(operator):
            raise RuleError("该干员当前已被选手 Ban，不能 Pick")
        own = self.blue_pick_ids if mode == MODE_BLUE else self.red_pick_ids
        opponent = self.red_pick_ids if mode == MODE_BLUE else self.blue_pick_ids
        if operator_id in opponent:
            raise RuleError("该干员已经被另一方 Pick")
        if operator_id not in own:
            own.append(operator_id)

    def remove(self, mode: str, operator_id: str) -> None:
        if mode == MODE_BAN:
            target = self.player_banned_operator_ids
        elif mode == MODE_BLUE:
            target = self.blue_pick_ids
        elif mode == MODE_RED:
            target = self.red_pick_ids
        else:
            raise RuleError("未知的 BP 操作模式")
        if operator_id in target:
            target.remove(operator_id)

    def clear_draft(self, keep_imported_bans: bool = True) -> None:
        self.blue_pick_ids = []
        self.red_pick_ids = []
        if not keep_imported_bans:
            self.player_banned_operator_ids = []
            self.player_banned_branches = set()
