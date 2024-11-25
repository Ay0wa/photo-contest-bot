from aiohttp_apispec import querystring_schema, response_schema

from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response

from .schemas import GameQuerySchema, GameSchema, ListGameSchema


class GameListView(AuthRequiredMixin, View):
    @querystring_schema(GameQuerySchema)
    @response_schema(ListGameSchema, 200)
    async def get(self):
        chat_id = self.request.query.get("chat_id")
        game_id = self.request.query.get("game_id")
        status = self.request.query.get("status")
        current_round = self.request.query.get("current_round")

        if game_id:
            game = await self.store.games.get_game_by_id(game_id=int(game_id))
            return json_response(data=GameSchema().dump(game))

        filters = {}

        if chat_id:
            filters["chat_id"] = int(chat_id)

        if status:
            filters["status"] = status

        if current_round:
            filters["current_round"] = int(current_round)

        games = await self.store.games.get_games_by_filters(filters)

        if not games:
            self.logger.error("No games found for the specified filters")
            return json_response(data={"games": []}, status=404)

        return json_response(data=ListGameSchema().dump({"games": games}))
