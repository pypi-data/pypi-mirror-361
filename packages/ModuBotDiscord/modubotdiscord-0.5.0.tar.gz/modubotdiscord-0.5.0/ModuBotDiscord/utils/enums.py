from enum import Enum


class ErrorType(Enum):
    DEFAULT = "⚠️ An error occurred"
    ACTION_NOT_ALLOWED = "🚫 Action not allowed"
    VALIDATION = "❗ Invalid input"
    TIMEOUT = "⌛ Timeout occurred"
    NOT_FOUND = "🔍 Not found"
