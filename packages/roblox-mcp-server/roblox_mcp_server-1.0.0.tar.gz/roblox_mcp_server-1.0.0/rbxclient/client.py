from uuid import uuid4
from roblox import Client
from roblox.utilities.requests import Requests
from roblox.utilities.url import URLGenerator
from roblox.utilities.exceptions import NotFound

from rbxclient.deeplink import RobloxDeeplink
from rbxclient.models.friends import (
    FriendUser,
    UserPresence,
    UserPresenceStatus,
    UserPresenceGame,
)
from rbxclient.models.game import GameDiscoverTopic, Game

BASE_URL: str = "roblox.com"


class RBXClient:
    def __init__(self, token: str, client=Client()):
        self.client: Client = client
        self._url_generator: URLGenerator = URLGenerator(base_url=BASE_URL)
        self._requests: Requests = Requests(url_generator=self._url_generator)
        self.authenticated_user: dict = {}
        self.set_token(token)
        self._token: str | None = None
        self._roblox_session_id: str = str(uuid4())

    @staticmethod
    def login_required(func):
        async def wrapper(self, *args, **kwargs):
            if not self._token:
                return {
                    "error": "User not authenticated. Please log in. (use login method)"
                }
            return await func(self, *args, **kwargs)

        return wrapper

    async def set_roblox_auth_key(self, key: str) -> None | dict:
        """
        Sets the Roblox authentication key for the client.
        """
        self._requests.session.cookies[".ROBLOSECURITY"] = key
        self._token = key
        try:
            await self.set_authenticated_user()
        except Exception as error:
            return {"error": str(error)}

    @property
    def user_id(self) -> int:
        """
        Returns the user ID of the authenticated user.
        """
        return self.authenticated_user.get("id")

    @property
    def deeplink(self) -> RobloxDeeplink:
        return RobloxDeeplink()

    async def set_authenticated_user(self) -> None:
        """
        Sets the authenticated user information by fetching it from the Roblox API.
        """
        try:
            user_me = await self.client.get_authenticated_user()
            self.authenticated_user = {
                "id": user_me.id,
                "name": user_me.name,
                "display_name": user_me.display_name,
                "description": user_me.description,
                "is_banned": user_me.is_banned,
                "created": user_me.created,
            }
        except NotFound as exception:
            raise exception

    @login_required
    async def fetch_discover_games(self, limit: int = 5) -> list[GameDiscoverTopic]:
        try:
            games_response = await self._requests.get(
                url=self._url_generator.get_url("apis", "explore-api/v1/get-sorts"),
                params={
                    "sessionId": self._roblox_session_id,
                    "device": "computer",
                    "country": "all",
                    "cpuCores": 8,
                    "maxResolution": "1920x1080",
                },
            )
            topic_data = games_response.json()
            recommend_games_response = topic_data["sorts"][1:]
            return [
                GameDiscoverTopic(
                    sort_id=topic.get("sortId"),
                    sort_display_name=topic.get("sortDisplayName"),
                    applied_filter_detail=topic.get("appliedFilters"),
                    games=[
                        Game(
                            universe_id=game.get("universeId"),
                            place_id=game.get("rootPlaceId"),
                            name=game.get("name"),
                            player_count=game.get("playerCount", 0),
                            total_up_votes=game.get("totalUpVotes", 0),
                            total_down_votes=game.get("totalDownVotes", 0),
                            is_sponsored=game.get("isSponsored", False),
                        )
                        for game in topic.get("games", [])[:limit]
                    ],
                )
                for topic in recommend_games_response
            ]
        except NotFound as exception:
            raise exception

    @login_required
    async def fetch_unread_private_message_count(self) -> int:
        if not self.authenticated_user:
            await self.set_authenticated_user()
        try:
            unread_response = await self._requests.get(
                url=self._url_generator.get_url(
                    "privatemessages", f"v1/messages/unread/count"
                )
            )
        except NotFound as exception:
            raise exception
        unread_data = unread_response.json()
        return unread_data.get("count", 0)

    @login_required
    async def fetch_robux_balance(self) -> int:
        if not self.authenticated_user:
            await self.set_authenticated_user()
        try:
            balance_response = await self._requests.get(
                url=self._url_generator.get_url(
                    "economy", f"v1/users/{self.user_id}/currency"
                )
            )
        except NotFound as exception:
            raise exception
        balance_data = balance_response.json()
        return balance_data.get("robux", 0)

    @login_required
    async def fetch_user_presences(self, user_ids: list[int]) -> list[UserPresence]:
        try:
            presence_response = await self._requests.post(
                url=self._url_generator.get_url("presence", "v1/presence/users"),
                json={"userIds": user_ids},
            )
        except NotFound as exception:
            raise exception
        presence_data = presence_response.json()
        return [
            UserPresence(
                status=UserPresenceStatus(int(presence.get("userPresenceType", 0))),
                name=presence.get("lastLocation"),
                game=(
                    UserPresenceGame(
                        id=presence.get("gameId"),
                        place_id=presence.get("placeId", 0),
                        root_place_id=presence.get("rootPlaceId", 0),
                    )
                    if presence.get("gameId") is not None
                    else None
                ),
            )
            for presence in presence_data.get("userPresences", [])
        ]

    @login_required
    async def fetch_friends(self, with_presence: bool = True) -> list[FriendUser]:
        if not self.authenticated_user:
            await self.set_authenticated_user()
        try:
            friends_response = await self._requests.get(
                url=self._url_generator.get_url(
                    "friends", f"v1/users/{self.user_id}/friends"
                ),
                params={"userSort": "StatusFrequents"},
            )
        except NotFound as exception:
            raise exception
        friends_data = friends_response.json()
        friends_presences = []
        if with_presence:
            user_ids = [friend.get("id") for friend in friends_data.get("data", [])]
            friends_presences = await self.fetch_user_presences(user_ids)
        return [
            FriendUser(
                id=friend.get("id"),
                name=friend.get("name"),
                display_name=friend.get("displayName"),
                presence=friend_presence,
            )
            for friend, friend_presence in zip(
                friends_data.get("data", []), friends_presences
            )
        ]

    def set_token(self, token: str):
        self.client.set_token(token)
        self._requests.session.cookies[".ROBLOSECURITY"] = token
        self._token = token

    def get_client(self):
        return self.client

    def set_client(self, client):
        self.client = client

    def __repr__(self):
        return f"RBXClient(client={self.client})"

    def __str__(self):
        return f"RBXClient with client: {self.client}"
