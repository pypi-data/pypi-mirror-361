"""
Branded types for coposet following TYPE_SAFETY_MANIFESTO.md principles.
"""

from enum import Enum
from typing import NewType
from uuid import UUID

# UUID-based branded types for strong typing
PosetSpaceId = NewType("PosetSpaceId", UUID)
PosetId = NewType("PosetId", UUID)
ElementId = NewType("ElementId", UUID)
RelationId = NewType("RelationId", UUID)
VoterId = NewType("VoterId", UUID)
AntichainId = NewType("AntichainId", UUID)
VotedAntichainId = NewType("VotedAntichainId", UUID)
EnricherId = NewType("EnricherId", UUID)

# String-based branded types
PosetSpaceName = NewType("PosetSpaceName", str)
PosetName = NewType("PosetName", str)
ElementName = NewType("ElementName", str)
Description = NewType("Description", str)


# Enums
class ExportFormat(str, Enum):
    """Export format options."""

    MCDP = "mcdp"
    LATEX = "latex"


class ConsensusType(str, Enum):
    """Consensus algorithm types."""

    DERIVE = "derive"
