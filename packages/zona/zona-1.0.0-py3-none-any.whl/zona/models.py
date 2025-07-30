from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from zona.metadata import Metadata


class ItemType(Enum):
    MARKDOWN = "markdown"
    HTML = "html"
    IMAGE = "image"


@dataclass
class Item:
    source: Path
    destination: Path
    url: str  # relative to site root
    metadata: Metadata | None = None  # frontmatter
    content: str | None = None
    type: ItemType | None = None
    copy: bool = True
    post: bool = False


# @dataclass
# class BuildCtx:
#     layout: Layout
#     item_map: dict[Path, Item] = field(default_factory=dict)
