from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Commit:
    """
    Represents one commit node in the Mini Git commit graph.

    Attributes:
        hash: Unique identifier for the commit.
        message: Commit message written by the user.
        author: Name of the user who created the commit.
        timestamp: Date and time when the commit was created.
        parents: Hashes of the commit's parent commits.
    """

    hash: str
    message: str
    author: str
    timestamp: datetime
    parents: list[str]