class NotFoundError(Exception):
    """Resource not found."""

    pass


class DuplicateEntryError(Exception):
    """Duplicate entry."""

    pass


class AlreadyExistsError(Exception):
    """Resource already exists."""

    pass


class InvalidCredentialsError(Exception):
    """Invalid credentials."""

    pass


class TokenExpiredError(Exception):
    """Token has expired."""

    pass


class InvalidTokenError(Exception):
    """Invalid token."""

    pass


class InvalidRequestError(Exception):
    """Invalid request."""

    pass


class PermissionDeniedError(Exception):
    """Пользователь не имеет необходимых прав доступа для выполнения операции."""

    pass


class UnauthorizedError(Exception):
    """Пользователь не аутентифицирован."""

    pass


class ValidationError(Exception):
    """Ошибка валидации данных."""

    def __init__(self, message: str, field: str = None, errors: dict = None):
        self.message = message
        self.field = field
        self.errors = errors or {}
        super().__init__(message)


class DatabaseError(Exception):
    """Ошибка базы данных."""

    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(message)


class CarNotAvailableError(Exception):
    """Автомобиль недоступен для операции (например, уже продан)."""

    pass


class InvalidVINError(Exception):
    """Недействительный VIN номер автомобиля."""

    pass


class DuplicateVINError(Exception):
    """VIN номер уже существует в системе."""

    pass


class MaxPhotosLimitError(Exception):
    """Превышено максимальное количество фотографий."""

    def __init__(
        self,
        message: str = "Превышено максимальное количество фотографий",
        max_photos: int = None,
    ):
        self.max_photos = max_photos
        super().__init__(message)


class FileFormatError(Exception):
    """Неподдерживаемый формат файла."""

    def __init__(
        self,
        message: str = "Неподдерживаемый формат файла",
        supported_formats: list = None,
    ):
        self.supported_formats = supported_formats or []
        super().__init__(message)


class FileSizeError(Exception):
    """Превышен максимальный размер файла."""

    def __init__(
        self,
        message: str = "Превышен максимальный размер файла",
        max_size_mb: int = None,
    ):
        self.max_size_mb = max_size_mb
        super().__init__(message)


class RateLimitError(Exception):
    """Превышен лимит запросов."""

    def __init__(
        self, message: str = "Превышен лимит запросов", retry_after: int = None
    ):
        self.retry_after = retry_after
        super().__init__(message)


class PaymentError(Exception):
    """Ошибка при обработке платежа."""

    def __init__(self, message: str, payment_id: str = None, error_code: str = None):
        self.payment_id = payment_id
        self.error_code = error_code
        super().__init__(message)


class SearchParameterError(Exception):
    """Ошибка в параметрах поиска автомобилей."""

    def __init__(self, message: str, invalid_parameters: list = None):
        self.invalid_parameters = invalid_parameters or []
        super().__init__(message)


class InvalidDateRangeError(Exception):
    """Недействительный диапазон дат."""

    def __init__(
        self, message: str = "Недействительный диапазон дат", field: str = None
    ):
        self.field = field
        super().__init__(message)


class TooManyListingsError(Exception):
    """Пользователь превысил лимит объявлений."""

    def __init__(
        self,
        message: str = "Превышен лимит активных объявлений",
        max_listings: int = None,
    ):
        self.max_listings = max_listings
        super().__init__(message)


class InvalidPriceError(Exception):
    """Недействительная цена автомобиля."""

    def __init__(
        self,
        message: str = "Недействительная цена автомобиля",
        min_price: float = None,
        max_price: float = None,
    ):
        self.min_price = min_price
        self.max_price = max_price
        super().__init__(message)


class ExternalServiceError(Exception):
    """Ошибка взаимодействия с внешним сервисом."""

    def __init__(self, message: str, service_name: str = None, status_code: int = None):
        self.service_name = service_name
        self.status_code = status_code
        super().__init__(message)


class ModelYearError(Exception):
    """Год выпуска автомобиля не соответствует допустимому диапазону для данной модели."""

    def __init__(
        self,
        message: str = "Год выпуска не соответствует модели",
        year_from: int = None,
        year_to: int = None,
    ):
        self.year_from = year_from
        self.year_to = year_to
        super().__init__(message)


class BrandModelMismatchError(Exception):
    """Несоответствие бренда и модели."""

    pass
