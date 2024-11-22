from app.bot.states.game_finished import BotGameFinishedState
from app.bot.states.game_processing import BotGameProcessingState
from app.bot.states.idle import BotIdleState
from app.bot.states.init import BotInitState
from app.bot.states.round_processing import BotRoundProcessingState
from app.bot.states.start_new_game import BotStartNewGameState

states = {
    "init": BotInitState,
    "idle": BotIdleState,
    "start_new_game": BotStartNewGameState,
    "round_processing": BotRoundProcessingState,
    "game_processing": BotGameProcessingState,
    "game_finished": BotGameFinishedState,
}
