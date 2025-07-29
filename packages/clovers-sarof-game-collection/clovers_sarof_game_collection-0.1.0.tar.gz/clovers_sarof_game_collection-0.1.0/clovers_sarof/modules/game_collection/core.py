import time
import asyncio
from typing import Any
from collections.abc import Coroutine, Callable, Sequence, Iterable
from clovers.core import Plugin, PluginCommand
from clovers.config import Config as CloversConfig
from clovers_sarof.core import Event, Rule
from clovers_sarof.core import manager
from clovers_sarof.core import GOLD
from clovers_sarof.core.account import Item
from clovers_sarof.core.linecard import card_template
from clovers_sarof.core.tools import to_int
from .config import Config


config_data = CloversConfig.environ().setdefault(__package__, {})
__config__ = Config.model_validate(config_data)
"""主配置类"""
config_data.update(__config__.model_dump())

default_bet = __config__.default_bet
timeout = __config__.timeout


class Session[Data]:
    """
    游戏场次信息
    """

    time: float
    group_id: str
    at: str | None = None
    p1_uid: str
    p1_nickname: str
    p2_uid: str = ""
    p2_nickname: str | None = None
    round = 1
    next: str
    win: str | None = None
    bet: tuple[Item, int] | None = None
    basebet: int = 0
    maxbet: int = 0
    data: Data
    game: str
    end_tips: str | None = None
    start_tips: Any = None

    def __init__(self, group_id: str, user_id: str, nickname: str, game: str):
        self.time = time.time()
        self.group_id = group_id
        self.p1_uid = user_id
        self.p1_nickname = nickname
        self.next = user_id
        self.game = game

    def __repr__(self) -> str:
        return f"Session({self.game}, group_id={self.group_id})"

    def join(self, user_id: str, nickname: str):
        self.time = time.time()
        self.p2_uid = user_id
        self.p2_nickname = nickname

    def timeout(self):
        return timeout + self.time - time.time()

    def nextround(self):
        self.time = time.time()
        self.round += 1
        self.next = self.p1_uid if self.next == self.p2_uid else self.p2_uid

    def double_bet(self):
        if not self.bet:
            return
        item, n = self.bet
        n += self.basebet
        self.bet = (item, min(n, self.maxbet) if self.maxbet > 0 else n)

    def delay(self, t: float = 0):
        self.time = time.time() + t

    def cover_check(self, user_id: str):
        p2_uid = self.p2_uid
        if not p2_uid:
            return
        p1_uid = self.p1_uid
        if p1_uid == user_id:
            return "你已发起了一场对决"
        if p2_uid == user_id:
            return "你正在进行一场对决"
        if p1_uid and p2_uid:
            return f"{self.p1_nickname} 与 {self.p2_nickname} 的对决还未结束，请等待比赛结束后再开始下一轮..."

    def action_check(self, user_id: str):
        if not self.p2_uid:
            if self.p1_uid == user_id:
                return "目前无人接受挑战哦"
            return "请先接受挑战"
        if self.p1_uid == user_id or self.p2_uid == user_id:
            if user_id == self.next:
                return
            return f"现在是{self.p1_nickname if self.next == self.p1_uid else self.p2_nickname}的回合"
        return f"{self.p1_nickname} v.s. {self.p2_nickname}\n正在进行中..."

    @property
    def create_info(self):
        if self.bet:
            item, n = self.bet
            self.basebet = n
            tip = f"本场下注：{n}{item.name}\n"
        else:
            tip = ""
        if self.at:
            p2_nickname = self.p2_nickname or f"玩家{self.at[:4]}..."
            return f"{tip}{self.p1_nickname} 向 {p2_nickname} 发起挑战！\n请 {p2_nickname} 回复 接受挑战 or 拒绝挑战\n【{timeout}秒内有效】"
        else:
            return f"{tip}{self.p1_nickname} 发起挑战！\n回复 接受挑战 即可开始对局。\n【{timeout}秒内有效】"

    def settle(self):
        """
        游戏结束结算
            return:结算界面
        """
        group_id = self.group_id
        win = self.win if self.win else self.p1_uid if self.next == self.p2_uid else self.p2_uid
        if win == self.p1_uid:
            win_name = self.p1_nickname
            lose = self.p2_uid
            lose_name = self.p2_nickname
        else:
            win_name = self.p2_nickname
            lose = self.p1_uid
            lose_name = self.p1_nickname

        with manager.db.session as session:
            # 胜者
            winner = manager.db.user(win, session)
            # 获胜数据
            winner.extra["win"] = winner.extra.get("win", 0) + 1
            win_streak = winner.extra.get("win_streak", 0) + 1
            winner.extra["win_streak"] = win_streak
            winner.extra["win_streak_max"] = max(winner.extra.get("win_streak_max", 0), win_streak)
            # 中断连败
            winner.extra.setdefault("lose", 0)
            winner.extra["lose_streak"] = 0
            winner.extra.setdefault("lose_streak_max", 0)
            # 败者
            loser = manager.db.user(lose, session)
            # 失败数据
            loser.extra["lose"] = loser.extra.get("lose", 0) + 1
            lose_streak = loser.extra.get("lose_streak", 0) + 1
            loser.extra["lose_streak"] = lose_streak
            loser.extra["lose_streak_max"] = max(loser.extra.get("lose_streak_max", 0), lose_streak)
            # 中断连胜
            loser.extra.setdefault("win", 0)
            loser.extra["win_streak"] = 0
            loser.extra.setdefault("win_streak_max", 0)
            card = (
                f"[pixel 20]◆胜者 {win_name}[pixel 460]◇败者 {lose_name}\n"
                f"[pixel 20]◆战绩 {winner.extra["win"]}:{winner.extra["lose"]}[pixel 460]◇战绩 {loser.extra["win"]}:{loser.extra["lose"]}\n"
                f"[pixel 20]◆连胜 {winner.extra["win_streak"]}[pixel 460]◇连败 {loser.extra["lose_streak"]}"
            )
            info = [card_template(card, "对战")]
            bet = self.bet
            if bet is not None:
                tip = manager.transfer(*bet, lose, win, group_id, session, force=True)
                info.append(card_template(tip[1], "结算", autowrap=True))
        result = [f"这场对决是 {win_name} 胜利了", manager.info_card(info, win)]
        if self.end_tips:
            result.append(self.end_tips)
        return result

    def end(self, result=None):
        self.time = -1
        settle = self.settle()

        async def output():
            if result:
                yield result
                await asyncio.sleep(1)
            for x in settle:
                yield x
                await asyncio.sleep(1)

        return output()


class Manager:
    def __init__(self, plugin: Plugin):
        self.place: dict[str, Session] = {}
        self.plugin = plugin
        self.info: dict[str, str] = {}

    def session(self, group_id: str):
        if not (session := self.place.get(group_id)):
            return
        if session.timeout() < 0:
            del self.place[group_id]
            return
        return session

    @staticmethod
    def args_parse(args: Sequence[str]) -> tuple[str, int, str]:
        match len(args):
            case 0:
                return "", 0, ""
            case 1:
                arg = args[0]
                return arg, 0, ""
            case 2:
                name, n = args
                return name, to_int(n) or 0, ""
            case _:
                arg, n, name = args[:3]
                if num := to_int(n):
                    n = num
                elif num := to_int(name):
                    name = n
                    n = num
                else:
                    n = 0
                return arg, n, name

    def create(
        self,
        game: str,
        command: PluginCommand,
        properties: Iterable[str] | None = None,
        priority: int = 10,
    ):
        _properties = {"user_id", "group_id", "at"}
        if properties:
            _properties.update(properties)

        def decorator(func: Callable[[Session, str], Coroutine]):
            @self.plugin.handle(command, _properties, rule=Rule.group, priority=priority)
            async def wrapper(event: Event):
                user_id = event.user_id
                group_id: str = event.group_id  # type: ignore
                if (session := self.session(group_id)) and (tip := session.cover_check(user_id)):
                    return tip
                arg, n, prop_name = self.args_parse(event.args)
                if n < 0:
                    n = default_bet
                with manager.db.session as sql_session:
                    account = manager.db.account(user_id, group_id, sql_session)
                    if n > 0:
                        item = manager.items_library.get(prop_name, GOLD)
                        if (bank_n := item.bank(account, sql_session).n) < n:
                            return f"你没有足够的{item.name}支撑这场对决({bank_n})。"
                    nickname = account.nickname
                    session = self.place[group_id] = Session(group_id, user_id, nickname, game=game)
                    if n > 0:
                        session.bet = (item, n)
                    if event.at:
                        session.at = event.at[0]
                        session.p2_nickname = manager.db.account(session.at, group_id, sql_session).nickname
                return await func(session, arg)

            return wrapper

        return decorator

    def action(
        self,
        game: str,
        command: PluginCommand,
        properties: Iterable[str] | None = None,
        priority: int = 20,
    ):
        _properties = {"user_id", "group_id"}
        if properties:
            _properties.update(properties)
        if not game in self.info:
            if isinstance(command, Iterable):
                self.info[game] = " | ".join(command)
            elif isinstance(command, str):
                self.info[game] = command
            elif command is None:
                self.info[game] = "任何指令"
            else:
                self.info[game] = command.pattern

        def decorator(func: Callable[[Event, Session], Coroutine]):
            @self.plugin.handle(command, _properties, priority=priority)
            async def wrapper(event: Event):
                user_id = event.user_id
                group_id = event.group_id
                if group_id is None:
                    with manager.db.session as sql_session:
                        group_id = manager.db.user(user_id, sql_session).connect
                session = self.place.get(group_id)
                if not session or session.game != game or session.time == -1:
                    return
                if tip := session.action_check(user_id):
                    return tip
                return await func(event, session)

            return wrapper

        return decorator
