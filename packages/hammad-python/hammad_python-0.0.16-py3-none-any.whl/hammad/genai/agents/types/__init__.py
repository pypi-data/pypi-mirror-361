"""hammad.genai.types

Contains functional types usable with various components within
the `hammad.genai` module."""

from typing import TYPE_CHECKING
from ...._internal import create_getattr_importer


if TYPE_CHECKING:
    from .history import (
        History,
    )
    from .tool import (
        Tool,
        ToolResponseMessage,
        function_tool,
    )


__all__ = (
    # hammad.genai.types.history
    "History",
    # hammad.genai.types.tool
    "Tool",
    "function_tool",
    "ToolResponseMessage",
)


__getattr__ = create_getattr_importer(__all__)


def __dir__() -> list[str]:
    return __all__