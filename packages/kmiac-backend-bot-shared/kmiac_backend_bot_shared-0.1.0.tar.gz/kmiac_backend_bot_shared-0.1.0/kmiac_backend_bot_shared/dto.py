import time
from io import BytesIO
from pathlib import Path
from typing import List
from typing import Optional, Dict, Any

from pydantic import BaseModel, computed_field, ConfigDict

from enums import TaskSource


class ServiceMetaInfo(BaseModel):
    name: str  # Человеку понятное имя
    category: str
    has_personal_information: bool

    description: Optional[str] = (
        None  # можно будет на клиенте высвечивать описание для пользователей
    )
    allowed_users: Optional[List[int]] = None


class UserDTO(BaseModel):
    id: int
    name: str


class TaskMessageDTO(BaseModel):
    sender_id: int
    name: str
    source: TaskSource
    start_time: float = time.time()
    params: Optional[Dict[str, Any]]
    end_time: Optional[float] = None

    @computed_field
    @property
    def x_time(self) -> Optional[float]:
        if self.end_time:
            return round((self.end_time - self.start_time), 2)
        return None


class ResponseDTO(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    buffer: BytesIO
    smb_path: Path # относительный путь в диске Q
