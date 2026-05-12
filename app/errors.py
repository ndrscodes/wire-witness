from dataclasses import dataclass


@dataclass
class ErrorMixin:
    error: str | None = None

    def is_error(self) -> bool:
        return self.error is not None
