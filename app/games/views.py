from aiohttp_apispec import querystring_schema, response_schema

from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response

from .schemas import GameQuerySchema, GameSchema, ListGameSchema


class GameListView(AuthRequiredMixin, View):
    @querystring_schema(GameQuerySchema)
    @response_schema(ListGameSchema, 200)
    async def get(self):
        query_params = GameQuerySchema().load(self.request.query)

        if query_params.get("game_id"):
            game = await self.store.games.get_game_by_id(
                game_id=int(query_params["game_id"]),
            )
            if not game:
                self.logger.error("No game found by game_id")
                return json_response(data={"game": []}, status=404)
            return json_response(data=GameSchema().dump(game))

        games = await self.store.games.get_games_by_filters(query_params)

        if not games:
            self.logger.error("No games found for the specified filters")
            return json_response(data={"games": []}, status=404)

        return json_response(data=ListGameSchema().dump({"games": games}))
