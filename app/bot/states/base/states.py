from app.bot.states.game_finished import BotGameFinishedState
from app.bot.states.game_processing import BotGameProcessingState
from app.bot.states.idle import BotIdleState
from app.bot.states.init import BotInitState
from app.bot.states.round_processing import BotRoundProcessingState
from app.bot.states.start_new_game import BotStartNewGameState
from app.chats.models import ChatState

states = {
    ChatState.init: BotInitState,
    ChatState.idle: BotIdleState,
    ChatState.start_new_game: BotStartNewGameState,
    ChatState.round_processing: BotRoundProcessingState,
    ChatState.game_processing: BotGameProcessingState,
    ChatState.game_finished: BotGameFinishedState,
}
