from pathlib import Path
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Optional,
    TypedDict,
    Union,
)

type MessageType = Dict[str, Any]
type _HandlerFunc = Union[
    Callable[[MessageType], None],
    Callable[[MessageType], Awaitable[None]]
]

class RabbitMQConfig(TypedDict):
    host: str
    port: int
    username: str
    password: str
    queue: str
    use_tls: bool
    ca_cert: Optional[Path]
    client_cert: Optional[Path]
    client_key: Optional[Path]
    prefetch_count: int