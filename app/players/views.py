from aiohttp_apispec import querystring_schema, response_schema

from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response

from .schemas import ListPlayerSchema, PlayerQuerySchema, PlayerSchema


class PlayerListView(AuthRequiredMixin, View):
    @querystring_schema(PlayerQuerySchema)
    @response_schema(ListPlayerSchema, 200)
    async def get(self):
        query_params = PlayerQuerySchema().load(self.request.query)

        if query_params.get("id"):
            player = await self.store.players.get_player_by_id(
                player_id=int(query_params.get("id"))
            )
            return json_response(data=PlayerSchema().dump(player))

        players = {
            "players": await self.store.players.get_players_by_filters(
                filters=query_params
            )
        }
        if not players:
            self.logger.error("No players found for the specified filters")
            return json_response(data={"games": []}, status=404)
        return json_response(data=ListPlayerSchema().dump(players))
