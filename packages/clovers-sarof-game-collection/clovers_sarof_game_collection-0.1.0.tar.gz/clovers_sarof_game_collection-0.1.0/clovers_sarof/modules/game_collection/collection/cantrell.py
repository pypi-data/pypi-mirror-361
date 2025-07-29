from ..action import place
from io import BytesIO
from typing import TypedDict
from collections.abc import Iterable
from clovers_sarof.core.linecard import text_to_image
from ..action import place, Event
from ..core import Session as BaseSession, to_int
from ..tools import PokerCard, random_poker, poker_suit, poker_point, poker_show

game = "梭哈"
place.info[game] = "看牌|开牌"


class SessionData(TypedDict):
    hand1: list[PokerCard]
    hand2: list[PokerCard]
    pt1: int
    pt2: int
    name1: str
    name2: str
    expose: int


type Session = BaseSession[SessionData]


@place.create(game, ["同花顺", "港式五张", "梭哈"])
async def _(session: Session, arg: str):
    level = to_int(arg)
    if level:
        level = 1 if level < 1 else level
        level = 5 if level > 5 else level
    else:
        level = 1
    deck = random_poker(range_point=(2, 15))

    if level == 1:
        hand1 = deck[0:5]
        pt1, name1 = cantrell_pt(hand1)
        hand2 = deck[5:10]
        pt2, name2 = cantrell_pt(hand2)
    else:
        deck = [deck[i : i + 5] for i in range(0, 50, 5)]
        hand1, pt1, name1 = max_hand(deck[0:level])
        hand2, pt2, name2 = max_hand(deck[level : 2 * level])

    session.data = {"hand1": hand1, "hand2": hand2, "pt1": pt1, "pt2": pt2, "name1": name1, "name2": name2, "expose": 3}
    return f"唰唰~，随机牌堆已生成，等级：{level}\n{session.create_info}"


@place.action(game, ["看牌"])
async def _(event: Event, session: Session):
    if not event.is_private():
        return "请私信回复 看牌 查看手牌"
    expose = session.data["expose"]
    session.delay()
    hand = session.data["hand1"] if event.user_id == session.p1_uid else session.data["hand2"]
    return f"{poker_show(hand[0:expose],'\n')}"


@place.action(game, ["开牌"])
async def _(event: Event, session: Session):
    user_id = event.user_id
    session.nextround()
    if user_id == session.p1_uid:
        return f"请{session.p2_nickname}\n{place.info[game]}"
    session.double_bet()
    if session.bet:
        prop, n = session.bet
        tip = f"\n----\n当前下注{n}{prop.name}"
    else:
        tip = ""
    expose = session.data["expose"]
    session.data["expose"] += 1
    hand1 = session.data["hand1"][:expose]
    hand2 = session.data["hand2"][:expose]
    result1 = f"玩家：{session.p1_nickname}\n手牌：{poker_show(hand1)}"
    result2 = f"玩家：{session.p2_nickname}\n手牌：{poker_show(hand2)}"
    output = BytesIO()
    if expose == 5:
        session.win = session.p1_uid if session.data["pt1"] > session.data["pt2"] else session.p2_uid
        result1 += f"\n牌型：{session.data['name1']}"
        result2 += f"\n牌型：{session.data['name2']}"
        text_to_image(
            f"{result1}\n----\n{result2}",
            bg_color="white",
            width=880,
        ).save(output, format="png")
        return session.end(output)
    else:
        text_to_image(
            f"{result1}\n----\n{result2}{tip}",
            bg_color="white",
            width=880,
        ).save(output, format="png")
        return [output, f"请{session.p1_nickname}\n{place.info[game]}"]


def is_straight(points: Iterable[int]):
    """
    判断是否为顺子
    """
    points = sorted(points)
    for i in range(1, len(points)):
        if points[i] - points[i - 1] != 1:
            return False
    return True


def cantrell_pt(hand: list[PokerCard]) -> tuple[int, str]:
    """
    牌型点数
    """
    pt = 0
    name = []
    suits, points = zip(*hand)
    # 判断同花
    if len(set(suits)) == 1:
        pt += suits[0]
        if is_straight(points):
            point = max(points)
            pt += point * (100**9)
            name.append(f"同花顺{poker_suit[suits[0]]} {poker_point[point]}")
        else:
            point = sum(points)
            pt += point * (100**6)
            name.append(f"同花{poker_suit[suits[0]]} {point}")
    else:
        pt += sum(suits)
        # 判断顺子
        if is_straight(points):
            point = max(points)
            pt += point * (100**5)
            name.append(f"顺子 {poker_point[point]}")
        else:
            setpoints = set(points)
            # 判断四条或葫芦
            if len(setpoints) == 2:
                for point in setpoints:
                    if points.count(point) == 4:
                        pt += point * (100**8)
                        name.append(f"四条 {poker_point[point]}")
                    if points.count(point) == 3:
                        pt += point * (100**7)
                        name.append(f"葫芦 {poker_point[point]}")
            else:
                # 判断三条，两对，一对
                exp = 1
                tmp = 0
                for point in setpoints:
                    if points.count(point) == 3:
                        pt += point * (100**4)
                        name.append(f"三条 {poker_point[point]}")
                        break
                    if points.count(point) == 2:
                        exp += 1
                        tmp += point
                        name.append(f"对 {poker_point[point]}")
                else:
                    pt += tmp * (100**exp)

            tmp = 0
            for point in setpoints:
                if points.count(point) == 1:
                    pt += point * (100)
                    tmp += point
            if tmp:
                name.append(f"散 {tmp}")

    return pt, " ".join(name)


def max_hand(hands: list[list[PokerCard]]):
    max_hand = hands[0]
    max_pt, max_name = cantrell_pt(max_hand)
    for hand in hands[1:]:
        pt, name = cantrell_pt(hand)
        if pt > max_pt:
            max_pt = pt
            max_name = name
            max_hand = hand
    return max_hand, max_pt, max_name
