from pydantic import BaseModel
from typing import Any

class CommonResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = {}

    def dict(self, **kwargs):
        return dict(
            code=self.code,
            message=self.message,
            data=self.data,
        )