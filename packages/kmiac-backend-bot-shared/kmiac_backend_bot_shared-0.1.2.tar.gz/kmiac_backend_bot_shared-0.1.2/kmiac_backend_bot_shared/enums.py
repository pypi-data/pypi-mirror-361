from enum import StrEnum


class TaskSource(StrEnum):
    """Источник задачи"""
    TELEGRAM = "telegram"
    VK = "vk"
    MAX_BOT = "max_bot"