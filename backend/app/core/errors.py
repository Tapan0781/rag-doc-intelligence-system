from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AppError(Exception):
    message: str
    status_code: int = 400
    error_code: str = "bad_request"

    def __str__(self) -> str:
        return f"{self.error_code}: {self.message}"
