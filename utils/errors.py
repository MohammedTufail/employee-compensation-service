class AppError(Exception):
    """Raised deliberately by validation/repositories to signal a specific HTTP status."""

    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message
