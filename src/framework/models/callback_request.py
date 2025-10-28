from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import datetime
import uuid


@dataclass
class Meeting:
    """Информация о встрече (доставке)."""
    date: str
    time_slot: str
    courier_full_name: Optional[str] = None
    courier_phone_number: Optional[str] = None
    courier_id: Optional[str] = None


@dataclass
class File:
    """Описание вложений (например, фото документов или посылки)."""
    name: str
    url: str


@dataclass
class CallbackRequestPayload:
    """Тело колбэка о статусе заявки."""
    service_name: str
    order_id: str
    claim_number: str
    address: str
    comment: Optional[str] = None
    reason: Optional[str] = None
    barcode: Optional[str] = None
    meeting: Optional[Meeting] = None
    files: List[File] = field(default_factory=list)


@dataclass
class CallbackRequest:
    """DTO для имитации колбэка от внешней службы."""
    correlation_id: str
    event_name: str
    event_date_time: str
    code: str
    description: Optional[str]
    body: CallbackRequestPayload

    @staticmethod
    def build_example():
        """Создаёт пример запроса (аналог Java builder)."""
        meeting = Meeting(
            date=datetime.now().strftime("%Y-%m-%d"),
            time_slot="10:00-12:00",
            courier_full_name="Ivan Petrov",
            courier_phone_number="+79991234567",
            courier_id="courier-007"
        )
        payload = CallbackRequestPayload(
            service_name="SERVICE_X",
            order_id="ORDER-123",
            claim_number="CLAIM-456",
            address="Москва, ул. Ленина, д. 1",
            comment="Доставка по времени",
            reason=None,
            barcode="CODE-ABC-999",
            meeting=meeting,
            files=[File(name="photo1.jpg", url="https://example.com/photo1.jpg")]
        )
        return CallbackRequest(
            correlation_id=str(uuid.uuid4()),
            event_name="MEETING_COMPLETED",
            event_date_time=datetime.now().isoformat(),
            code="E04",
            description="Встреча успешно завершена",
            body=payload
        )

    def to_dict(self):
        """Конвертирует объект в словарь для сериализации в JSON."""
        return asdict(self)
