KEYBOARD_MESSAGE = """
Я могу начать для вас новую игру, 
либо показать результаты последней!
\nНапишите: keyboard, чтобы получить клавиатуру
"""

INIT_MESSAGE = "Привет, добавьте меня в админы. Напишите: keyboard"

IDLE_MESSAGE = "Ожидание начала игры..."

KEYBOARD = {
    "one_time": True,
    "buttons": [
        [
            {
                "action": {
                    "type": "callback",
                    "payload": '{"button": "start_game"}',
                    "label": "Начать игру",
                },
                "color": "positive",
            }
        ],
        [
            {
                "action": {
                    "type": "callback",
                    "payload": '{"button": "get_last_game"}',
                    "label": "Показать последнюю игру",
                },
                "color": "secondary",
            }
        ],
    ],
}
