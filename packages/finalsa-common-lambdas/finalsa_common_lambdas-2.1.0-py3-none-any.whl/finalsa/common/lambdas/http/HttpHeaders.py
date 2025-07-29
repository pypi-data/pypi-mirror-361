from typing import Dict, Optional

from finalsa.traceability.functions import (
    HTTP_HEADER_CORRELATION_ID,
    HTTP_HEADER_TRACE_ID,
)


class HttpHeaders:

    def __init__(self, headers: Dict[str, str]) -> None:
        self.headers = headers

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return self.headers.get(key, default)

    def get_content_type(self) -> Optional[str]:
        return self.get("Content-Type", "")

    def get_correlation_id(self) -> Optional[str]:
        return self.get(HTTP_HEADER_CORRELATION_ID)

    def get_trace_id(self) -> Optional[str]:
        return self.get(HTTP_HEADER_TRACE_ID)
