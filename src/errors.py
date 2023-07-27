"""Contains classes that represent local program erros."""


class BaseError(Exception):
    """
    Base Class for all Errors.
    """

    def __init__(self, message: str):
        self.message: str = message

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.message}')"


class MissingVariableError(BaseError):
    """Raised when missing a required environment vaiable."""

    def __init__(self, message: str):
        super().__init__(message)
