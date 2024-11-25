from aiohttp_apispec import querystring_schema, response_schema

from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response

from .schemas import ListPlayerSchema, PlayerQuerySchema, PlayerSchema


class PlayerListView(AuthRequiredMixin, View):
    @querystring_schema(PlayerQuerySchema)
    @response_schema(ListPlayerSchema, 200)
    async def get(self):
        player_id = self.request.query.get("id")
        user_id = self.request.query.get("user_id")
        username = self.request.query.get("username")

        game_id = self.request.query.get("game_id")
        status = self.request.query.get("status")

        votes = self.request.query.get("votes")
        is_voted = self.request.query.get("is_voted")

        filters = {}

        if user_id:
            filters["user_id"] = int(user_id)

        if username:
            filters["username"] = username

        if game_id:
            filters["game_id"] = int(game_id)

        if status:
            filters["status"] = status

        if votes:
            filters["votes"] = int(votes)

        if is_voted:
            filters["is_voted"] = bool(is_voted)

        if player_id:
            player = await self.store.players.get_player_by_id(
                player_id=int(player_id)
            )
            return json_response(data=PlayerSchema().dump(player))

        if filters:
            players = {
                "players": await self.store.players.get_players_by_filters(
                    filters=filters
                )
            }
            return json_response(data=ListPlayerSchema().dump(players))

        players = {"players": await self.store.players.list_players()}
        return json_response(data=ListPlayerSchema().dump(players))
