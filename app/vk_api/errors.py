class VkApiError(Exception):
    def __init__(self, error_data):
        self.error_code = error_data.get("error", {}).get(
            "error_code", "Неизвестный код"
        )
        self.error_msg = error_data.get("error", {}).get(
            "error_msg", "Нет описания ошибки"
        )
        self.raw_data = error_data
        super().__init__(
            f"Ошибка VK API: {self.error_msg} (код: {self.error_code})"
        )
