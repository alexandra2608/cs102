import dataclasses
import math
import time
import typing as tp

from homework08.vkapi import config, session  # type: ignore
from homework08.vkapi.session import Session  # type: ignore

QueryParams = tp.Optional[tp.Dict[str, tp.Union[str, int]]]


@dataclasses.dataclass(frozen=True)
class FriendsResponse:
    count: int
    items: tp.Union[tp.List[int], tp.List[tp.Dict[str, tp.Any]]]


def get_friends(
    user_id: int,
    count: int = 5000,
    offset: int = 0,
    fields: tp.Optional[tp.List[str]] = None,
) -> FriendsResponse:
    """
    Получить список идентификаторов друзей пользователя или расширенную информацию
    о друзьях пользователя (при использовании параметра fields).
    :param user_id: Идентификатор пользователя, список друзей для которого нужно получить.
    :param count: Количество друзей, которое нужно вернуть.
    :param offset: Смещение, необходимое для выборки определенного подмножества друзей.
    :param fields: Список полей, которые нужно получить для каждого пользователя.
    :return: Список идентификаторов друзей пользователя или список пользователей.
    """
    vk_config = {
        "token": "vk1.a.zk4YX-vPF_ULUhpiB_jFO0tyl3utLsaANweNkg-DP20awDqGUSKS0lgb9i0j1jMc4gY-c2aLVeMynClyug2SXL_MedY5cRSQSddNJwazilpSG-xrLzS3lXPfy_sPjZ8alOv9T_4CNHFN1NsB6YNIt1YQJPWvxysIBpUeNCQv4IPhZ_c0Pd83-zohEKTmYnwi",
        "client_id": "51673375",
        "version": "5.131",
        "domain": "https://api.vk.com/method/",
    }
    domain = Session(vk_config["domain"])
    try:
        req = domain.get(
            "friends.get",
            params={
                "access_token": vk_config["token"],
                "v": vk_config["version"],
                "user_id": str(user_id),
                "offset": str(offset),
                "count": str(count),
                "fields": fields,
            },
        )
        data = req.json()["response"]["items"]
        count = req.json()["response"]["count"]
        return FriendsResponse(count, list(data))
    except:
        pass
    return FriendsResponse(0, [{"items": ""}])


class MutualFriends(tp.Dict):
    id: int
    common_friends: tp.List[int]
    common_count: int


def get_mutual(
    source_uid: tp.Optional[int] = None,
    target_uid: tp.Optional[int] = None,
    target_uids: tp.Optional[tp.List[int]] = None,
    order: str = "",
    count: tp.Optional[int] = None,
    offset: int = 0,
    progress=None,
) -> tp.Union[tp.List[int], tp.List[MutualFriends]]:
    """
    Получить список идентификаторов общих друзей между парой пользователей.
    :param source_uid: Идентификатор пользователя, чьи друзья пересекаются с друзьями пользователя с идентификатором target_uid.
    :param target_uid: Идентификатор пользователя, с которым необходимо искать общих друзей.
    :param target_uids: Cписок идентификаторов пользователей, с которыми необходимо искать общих друзей.
    :param order: Порядок, в котором нужно вернуть список общих друзей.
    :param count: Количество общих друзей, которое нужно вернуть.
    :param offset: Смещение, необходимое для выборки определенного подмножества общих друзей.
    :param progress: Callback для отображения прогресса.
    """
    vk_config = {
        "token": "vk1.a.zk4YX-vPF_ULUhpiB_jFO0tyl3utLsaANweNkg-DP20awDqGUSKS0lgb9i0j1jMc4gY-c2aLVeMynClyug2SXL_MedY5cRSQSddNJwazilpSG-xrLzS3lXPfy_sPjZ8alOv9T_4CNHFN1NsB6YNIt1YQJPWvxysIBpUeNCQv4IPhZ_c0Pd83-zohEKTmYnwi",
        "client_id": "51673375",
        "version": "5.131",
        "domain": "https://api.vk.com/method/",
    }
    domain = Session(vk_config["domain"])
    target_uids = [] if target_uids is None else target_uids
    if target_uid is not None:
        target_uids.append(target_uid)
    if not target_uids:
        return target_uids  # type: ignore
    cycles = (len(target_uids) - 1) // 100 + 1
    mutual_friends = []
    for i in range(cycles):
        user_ids = ""
        for j in range(i * 100, i * 100 + 100 if i != cycles - 1 else len(target_uids) % 100):
            user_ids = user_ids + "," + str(target_uids[j])
        user_ids = user_ids[1 : len(user_ids)]
        try:
            req = domain.get(
                "friends.getMutual",
                params={
                    "access_token": vk_config["token"],
                    "v": vk_config["version"],
                    "source_uid": str(source_uid),
                    "target_uids": str(user_ids),
                    "offset": str(i * 100),
                    "order": order,
                    "count": 100,
                },
            )
            for item in req.json()["response"]:
                mutual_friends.append(
                    MutualFriends(
                        id=item["id"],
                        common_count=item["common_count"],
                        common_friends=item["common_friends"],
                    )
                )
        except:
            pass
        time.sleep(0.35)
    if len(mutual_friends) == 1:
        return mutual_friends[0]["common_friends"]
    return mutual_friends


if __name__ == "__main__":
    print(get_friends(225953999))
    print(get_mutual(source_uid=225953999, target_uid=262094290))
