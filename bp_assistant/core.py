from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
import hashlib
import json
import random
from typing import Any


FORMAT_VERSION = 1
PLAYER_A = "A"
PLAYER_B = "B"


class RuleError(ValueError):
    """规则校验失败。"""


@dataclass(frozen=True)
class Operator:
    operator_id: str
    name: str
    rarity: int
    profession: str
    branch: str
    branch_id: str = ""


@dataclass
class MatchRules:
    branch_bans_per_player: int = 1
    operator_bans_per_player: int = 4
    rounds: int = 2
    picks_per_round: int = 5
    max_picks_per_round: int = 7
    min_increment: int = 1
    price_cap: int = 24
    starting_prices: dict[int, int] = field(
        default_factory=lambda: {1: 2, 2: 2, 3: 2, 4: 2, 5: 4, 6: 8}
    )
    enable_default_bans: bool = False
    default_banned_operator_ids: list[str] = field(default_factory=list)
    default_banned_branches: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if not 1 <= self.rounds <= 10:
            raise RuleError("轮数必须在 1 到 10 之间")
        if not 1 <= self.picks_per_round <= self.max_picks_per_round <= 7:
            raise RuleError("每轮选取数必须为 1～7，且不能超过每轮上限")
        if self.branch_bans_per_player < 0 or self.operator_bans_per_player < 0:
            raise RuleError("Ban 数量不能为负数")
        if self.min_increment < 1:
            raise RuleError("最小加价必须至少为 1 点")
        if self.price_cap < max(self.starting_prices.values()):
            raise RuleError("价格上限不能低于起拍价")

    def starting_price(self, rarity: int) -> int:
        try:
            return int(self.starting_prices[rarity])
        except KeyError as exc:
            raise RuleError(f"未配置 {rarity} 星干员的起拍价") from exc


@dataclass
class MatchConfig:
    match_id: str
    title: str
    player_a_name: str
    player_b_name: str
    rules: MatchRules
    global_banned_operator_ids: list[str] = field(default_factory=list)
    global_banned_branches: list[str] = field(default_factory=list)
    host_banned_branches: dict[str, list[str]] = field(
        default_factory=lambda: {PLAYER_A: [], PLAYER_B: []}
    )
    host_banned_operator_ids: dict[str, list[str]] = field(
        default_factory=lambda: {PLAYER_A: [], PLAYER_B: []}
    )
    bans_finalized: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def validate(self) -> None:
        if not self.match_id.strip():
            raise RuleError("比赛编号不能为空")
        if not self.player_a_name.strip() or not self.player_b_name.strip():
            raise RuleError("双方选手名称不能为空")
        self.rules.validate()
        if len(set(self.global_banned_operator_ids)) != len(
            self.global_banned_operator_ids
        ):
            raise RuleError("全局 Ban 中存在重复干员")
        if len(set(self.global_banned_branches)) != len(
            self.global_banned_branches
        ):
            raise RuleError("全局 Ban 中存在重复分支")
        for player in (PLAYER_A, PLAYER_B):
            if player not in self.host_banned_branches:
                self.host_banned_branches[player] = []
            if player not in self.host_banned_operator_ids:
                self.host_banned_operator_ids[player] = []
        if self.bans_finalized:
            for player in (PLAYER_A, PLAYER_B):
                if (
                    len(set(self.host_banned_branches[player]))
                    != self.rules.branch_bans_per_player
                ):
                    raise RuleError(
                        f"{player} 方主持人分支 Ban 数量与规则不一致"
                    )
                if (
                    len(set(self.host_banned_operator_ids[player]))
                    != self.rules.operator_bans_per_player
                ):
                    raise RuleError(
                        f"{player} 方主持人干员 Ban 数量与规则不一致"
                    )


@dataclass
class PlayerSubmission:
    match_id: str
    player: str
    player_name: str
    round_index: int
    banned_branches: list[str]
    banned_operator_ids: list[str]
    picks: list[str]
    submitted_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def validate(self, config: MatchConfig, operators: dict[str, Operator]) -> None:
        rules = config.rules
        if self.match_id != config.match_id:
            raise RuleError("选手文件与当前比赛编号不一致")
        if self.player not in (PLAYER_A, PLAYER_B):
            raise RuleError("选手身份必须是 A 或 B")
        expected_name = config.player_a_name if self.player == PLAYER_A else config.player_b_name
        if self.player_name != expected_name:
            raise RuleError(f"选手名称不匹配，应为“{expected_name}”")
        if not 1 <= self.round_index <= rules.rounds:
            raise RuleError(f"轮次必须在 1 到 {rules.rounds} 之间")
        if len(set(self.banned_branches)) != rules.branch_bans_per_player:
            raise RuleError(f"必须选择 {rules.branch_bans_per_player} 个不同的子职业分支 Ban")
        if len(set(self.banned_operator_ids)) != rules.operator_bans_per_player:
            raise RuleError(f"必须选择 {rules.operator_bans_per_player} 名不同的干员 Ban")
        if len(self.picks) != rules.picks_per_round:
            raise RuleError(f"第 {self.round_index} 轮必须选择 {rules.picks_per_round} 名干员")
        if len(set(self.picks)) != len(self.picks):
            raise RuleError(f"第 {self.round_index} 轮存在重复干员")
        unknown = (set(self.banned_operator_ids) | set(self.picks)) - set(operators)
        if unknown:
            raise RuleError(f"文件中含有未知干员：{', '.join(sorted(unknown))}")
        unknown_global = set(config.global_banned_operator_ids) - set(operators)
        if unknown_global:
            raise RuleError(
                f"配置的全局 Ban 中含有未知干员：{', '.join(sorted(unknown_global))}"
            )
        if config.bans_finalized:
            if set(self.banned_branches) != set(
                config.host_banned_branches[self.player]
            ):
                raise RuleError("选手文件中的主持人分支 Ban 与比赛配置不一致")
            if set(self.banned_operator_ids) != set(
                config.host_banned_operator_ids[self.player]
            ):
                raise RuleError("选手文件中的主持人干员 Ban 与比赛配置不一致")
        effective_banned_ids = set(config.global_banned_operator_ids)
        effective_banned_branches = set(config.global_banned_branches)
        for player in (PLAYER_A, PLAYER_B):
            effective_banned_ids.update(config.host_banned_operator_ids[player])
            effective_banned_branches.update(config.host_banned_branches[player])
        invalid_picks = {
            operator_id
            for operator_id in self.picks
            if operator_id in effective_banned_ids
            or operators[operator_id].branch in effective_banned_branches
        }
        if invalid_picks:
            names = "、".join(
                operators[operator_id].name for operator_id in sorted(invalid_picks)
            )
            raise RuleError(f"不能 Pick 全局或主持人已 Ban 的干员：{names}")
        own_banned = set(self.banned_operator_ids)
        if own_banned & set(self.picks):
            raise RuleError("不能 Pick 自己 Ban 的干员")
        for operator_id in self.picks:
            if operators[operator_id].branch in set(self.banned_branches):
                raise RuleError(f"不能 Pick 已 Ban 分支中的干员：{operators[operator_id].name}")


@dataclass
class Bid:
    player: str
    amount: int | None
    action: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


@dataclass
class AuctionItem:
    operator_id: str
    round_index: int
    nominated_by: list[str]
    starting_price: int
    status: str = "pending"
    bids: list[Bid] = field(default_factory=list)
    current_price: int | None = None
    leader: str | None = None
    winner: str | None = None
    final_price: int | None = None
    passed_players: list[str] = field(default_factory=list)

    def place_bid(self, player: str, amount: int, rules: MatchRules) -> None:
        if self.status not in ("pending", "active"):
            raise RuleError("当前干员的拍卖已经结束")
        if player not in (PLAYER_A, PLAYER_B):
            raise RuleError("竞价方必须是 A 或 B")
        minimum = self.starting_price if self.current_price is None else self.current_price + rules.min_increment
        if amount < minimum:
            raise RuleError(f"本次出价不能低于 {minimum} 点")
        if amount > rules.price_cap:
            raise RuleError(f"出价不能超过 {rules.price_cap} 点")
        self.status = "active"
        self.current_price = amount
        self.leader = player
        self.bids.append(Bid(player=player, amount=amount, action="bid"))
        opponent = PLAYER_B if player == PLAYER_A else PLAYER_A
        if opponent in self.passed_players:
            self.award()

    def pass_bid(self, player: str) -> bool:
        """记录放弃。返回 True 表示拍卖已自动结束。"""
        if self.status not in ("pending", "active"):
            raise RuleError("当前干员的拍卖已经结束")
        if player == self.leader:
            raise RuleError("当前领先方无需放弃跟价")
        if player in self.passed_players:
            raise RuleError("该选手已经放弃过本轮出价")
        self.bids.append(Bid(player=player, amount=None, action="pass"))
        self.passed_players.append(player)
        if self.leader:
            self.award()
            return True
        if len(set(self.passed_players)) == 2:
            self.mark_unsold()
            return True
        return False

    def award(self) -> None:
        if not self.leader or self.current_price is None:
            raise RuleError("尚无有效出价，不能成交")
        self.status = "sold"
        self.winner = self.leader
        self.final_price = self.current_price

    def mark_unsold(self) -> None:
        if self.leader:
            raise RuleError("已有领先出价，不能标记为流拍")
        self.status = "unsold"


@dataclass
class MatchState:
    config: MatchConfig
    host_banned_branches: dict[str, list[str]] = field(
        default_factory=lambda: {PLAYER_A: [], PLAYER_B: []}
    )
    host_banned_operator_ids: dict[str, list[str]] = field(
        default_factory=lambda: {PLAYER_A: [], PLAYER_B: []}
    )
    ban_turn: str = PLAYER_A
    ban_complete: bool = False
    submissions: dict[str, PlayerSubmission] = field(default_factory=dict)
    auction_items: list[AuctionItem] = field(default_factory=list)
    auction_seed: int | None = None
    auction_seeds: dict[str, int] = field(default_factory=dict)
    current_index: int = 0
    used_operator_ids: dict[str, list[str]] = field(
        default_factory=lambda: {PLAYER_A: [], PLAYER_B: []}
    )
    perfect_clear: dict[str, bool] = field(
        default_factory=lambda: {PLAYER_A: False, PLAYER_B: False}
    )
    notes: str = ""

    @property
    def auction_complete(self) -> bool:
        prepared_rounds = {item.round_index for item in self.auction_items}
        return prepared_rounds == set(range(1, self.config.rules.rounds + 1)) and all(
            item.status in ("sold", "unsold") for item in self.auction_items
        )

    def current_item(self) -> AuctionItem | None:
        if not self.auction_items or self.current_index >= len(self.auction_items):
            return None
        return self.auction_items[self.current_index]

    def advance(self) -> AuctionItem | None:
        while self.current_index < len(self.auction_items):
            item = self.auction_items[self.current_index]
            if item.status not in ("sold", "unsold"):
                return item
            self.current_index += 1
        return None

    def calculate_score(self, player: str) -> dict[str, float]:
        won = [item for item in self.auction_items if item.winner == player]
        used = set(self.used_operator_ids.get(player, []))
        owned = {item.operator_id for item in won}
        if not used <= owned:
            raise RuleError("实际上场列表中包含该选手未获得的干员")
        used_cost = sum(item.final_price or 0 for item in won if item.operator_id in used)
        bench_cost = sum(item.final_price or 0 for item in won if item.operator_id not in used)
        return {
            "used_cost": float(used_cost),
            "bench_full_cost": float(bench_cost),
            "bench_weighted_cost": bench_cost / 2,
            "total": used_cost + bench_cost / 2,
        }

    def result(self) -> dict[str, Any]:
        a_score = self.calculate_score(PLAYER_A)
        b_score = self.calculate_score(PLAYER_B)
        a_clear = self.perfect_clear[PLAYER_A]
        b_clear = self.perfect_clear[PLAYER_B]
        if a_clear and not b_clear:
            winner, reason = PLAYER_A, "仅 A 方完美通关"
        elif b_clear and not a_clear:
            winner, reason = PLAYER_B, "仅 B 方完美通关"
        elif not a_clear and not b_clear:
            winner, reason = None, "双方均未完美通关"
        elif a_score["total"] < b_score["total"]:
            winner, reason = PLAYER_A, "双方完美通关，A 方人力消耗更少"
        elif b_score["total"] < a_score["total"]:
            winner, reason = PLAYER_B, "双方完美通关，B 方人力消耗更少"
        else:
            winner, reason = None, "双方完美通关且人力消耗相同"
        return {"A": a_score, "B": b_score, "winner": winner, "reason": reason}


def build_auction_round(
    config: MatchConfig,
    submission_a: PlayerSubmission,
    submission_b: PlayerSubmission,
    operators: dict[str, Operator],
    seed: int | None = None,
    previous_operator_ids: set[str] | None = None,
) -> list[AuctionItem]:
    submission_a.validate(config, operators)
    submission_b.validate(config, operators)
    if submission_a.player == submission_b.player:
        raise RuleError("必须分别导入 A、B 两方的选手文件")

    by_player = {submission_a.player: submission_a, submission_b.player: submission_b}
    a = by_player[PLAYER_A]
    b = by_player[PLAYER_B]
    if a.round_index != b.round_index:
        raise RuleError("双方选手文件不属于同一轮")
    round_index = a.round_index
    banned_ops = set(a.banned_operator_ids) | set(b.banned_operator_ids)
    banned_branches = set(a.banned_branches) | set(b.banned_branches)
    if config.rules.enable_default_bans:
        banned_ops |= set(config.rules.default_banned_operator_ids)
        banned_branches |= set(config.rules.default_banned_branches)

    all_picks = list(a.picks) + list(b.picks)
    conflicts = [
        operators[op].name
        for op in all_picks
        if op in banned_ops or operators[op].branch in banned_branches
    ]
    if conflicts:
        raise RuleError("Pick 与双方最终 Ban 冲突：" + "、".join(sorted(set(conflicts))))
    repeated = set(all_picks) & set(previous_operator_ids or set())
    if repeated:
        names = "、".join(sorted(operators[operator_id].name for operator_id in repeated))
        raise RuleError(f"本轮 Pick 包含此前已经拍卖过的干员：{names}")

    rng = random.Random(seed)
    nominations: dict[str, list[str]] = {}
    order: list[str] = []
    for player, submission in ((PLAYER_A, a), (PLAYER_B, b)):
        for operator_id in submission.picks:
            if operator_id not in nominations:
                nominations[operator_id] = []
                order.append(operator_id)
            nominations[operator_id].append(player)
    rng.shuffle(order)
    return [
        AuctionItem(
            operator_id=operator_id,
            round_index=round_index,
            nominated_by=nominations[operator_id],
            starting_price=config.rules.starting_price(operators[operator_id].rarity),
        )
        for operator_id in order
    ]


def build_auction(
    config: MatchConfig,
    submission_a: PlayerSubmission,
    submission_b: PlayerSubmission,
    operators: dict[str, Operator],
    seed: int | None = None,
) -> list[AuctionItem]:
    """兼容单轮调用；新代码应使用 build_auction_round。"""
    return build_auction_round(
        config,
        submission_a,
        submission_b,
        operators,
        seed=seed,
    )


def dataclass_to_dict(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return {key: dataclass_to_dict(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {key: dataclass_to_dict(item) for key, item in value.items()}
    if isinstance(value, list):
        return [dataclass_to_dict(item) for item in value]
    return value


def make_envelope(kind: str, payload: dict[str, Any]) -> dict[str, Any]:
    body = {"format_version": FORMAT_VERSION, "kind": kind, "payload": payload}
    encoded = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {**body, "checksum": hashlib.sha256(encoded).hexdigest()}


def verify_envelope(envelope: dict[str, Any], expected_kind: str) -> dict[str, Any]:
    if envelope.get("format_version") != FORMAT_VERSION:
        raise RuleError("文件版本不受支持")
    if envelope.get("kind") != expected_kind:
        raise RuleError(f"文件类型错误，应为 {expected_kind}")
    checksum = envelope.get("checksum")
    body = {key: envelope[key] for key in ("format_version", "kind", "payload")}
    encoded = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if checksum != hashlib.sha256(encoded).hexdigest():
        raise RuleError("文件校验失败，内容可能已损坏或被修改")
    return envelope["payload"]


def rules_from_dict(data: dict[str, Any]) -> MatchRules:
    prices = {int(key): int(value) for key, value in data["starting_prices"].items()}
    return MatchRules(**{**data, "starting_prices": prices})


def config_from_dict(data: dict[str, Any]) -> MatchConfig:
    return MatchConfig(
        match_id=data["match_id"],
        title=data["title"],
        player_a_name=data["player_a_name"],
        player_b_name=data["player_b_name"],
        rules=rules_from_dict(data["rules"]),
        global_banned_operator_ids=data.get("global_banned_operator_ids", []),
        global_banned_branches=data.get("global_banned_branches", []),
        host_banned_branches=data.get(
            "host_banned_branches", {PLAYER_A: [], PLAYER_B: []}
        ),
        host_banned_operator_ids=data.get(
            "host_banned_operator_ids", {PLAYER_A: [], PLAYER_B: []}
        ),
        bans_finalized=bool(data.get("bans_finalized", False)),
        created_at=data.get("created_at", datetime.now().isoformat(timespec="seconds")),
    )


def submission_from_dict(data: dict[str, Any]) -> PlayerSubmission:
    return PlayerSubmission(**data)


def auction_item_from_dict(data: dict[str, Any]) -> AuctionItem:
    return AuctionItem(
        operator_id=data["operator_id"],
        round_index=data["round_index"],
        nominated_by=data["nominated_by"],
        starting_price=data["starting_price"],
        status=data.get("status", "pending"),
        bids=[Bid(**bid) for bid in data.get("bids", [])],
        current_price=data.get("current_price"),
        leader=data.get("leader"),
        winner=data.get("winner"),
        final_price=data.get("final_price"),
        passed_players=data.get("passed_players", []),
    )


def state_from_dict(data: dict[str, Any]) -> MatchState:
    state = MatchState(config=config_from_dict(data["config"]))
    state.submissions = {
        key: submission_from_dict(value) for key, value in data.get("submissions", {}).items()
    }
    state.auction_items = [
        auction_item_from_dict(item) for item in data.get("auction_items", [])
    ]
    state.host_banned_branches = data.get(
        "host_banned_branches", {PLAYER_A: [], PLAYER_B: []}
    )
    state.host_banned_operator_ids = data.get(
        "host_banned_operator_ids", {PLAYER_A: [], PLAYER_B: []}
    )
    state.ban_turn = data.get("ban_turn", PLAYER_A)
    state.ban_complete = bool(data.get("ban_complete", False))
    if state.config.bans_finalized and not any(
        state.host_banned_operator_ids.values()
    ):
        state.host_banned_branches = {
            player: list(state.config.host_banned_branches[player])
            for player in (PLAYER_A, PLAYER_B)
        }
        state.host_banned_operator_ids = {
            player: list(state.config.host_banned_operator_ids[player])
            for player in (PLAYER_A, PLAYER_B)
        }
        state.ban_complete = True
    if not any(state.host_banned_operator_ids.values()) and state.submissions:
        for player in (PLAYER_A, PLAYER_B):
            submission = next(
                (
                    value
                    for value in state.submissions.values()
                    if value.player == player
                ),
                None,
            )
            if submission:
                state.host_banned_branches[player] = list(submission.banned_branches)
                state.host_banned_operator_ids[player] = list(
                    submission.banned_operator_ids
                )
        state.ban_complete = all(
            len(state.host_banned_operator_ids[player])
            == state.config.rules.operator_bans_per_player
            and len(state.host_banned_branches[player])
            == state.config.rules.branch_bans_per_player
            for player in (PLAYER_A, PLAYER_B)
        )
    state.auction_seed = data.get("auction_seed")
    state.auction_seeds = {
        str(key): int(value) for key, value in data.get("auction_seeds", {}).items()
    }
    state.current_index = data.get("current_index", 0)
    state.used_operator_ids = data.get(
        "used_operator_ids", {PLAYER_A: [], PLAYER_B: []}
    )
    state.perfect_clear = data.get(
        "perfect_clear", {PLAYER_A: False, PLAYER_B: False}
    )
    state.notes = data.get("notes", "")
    return state
