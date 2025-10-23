from typing import (
    Any,
    Callable,
    Dict,
)

type MessageType = Dict[str, Any]
type _HandlerFunc = Callable[[MessageType], None]