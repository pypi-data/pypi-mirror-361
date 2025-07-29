"""Coposet: Mathematical posets for Python with functional programming patterns.

Coposet provides a type-safe, functional approach to working with partially ordered
sets (posets) in Python. It supports voting workflows, enrichment, and mathematical
operations like products and coproducts.

Quick Start Example:
    >>> from coposet import PosetSpace, Element, Poset, Relation
    >>> from coposet.types import PosetSpaceName, Description, ElementName, PosetName
    >>>
    >>> # Create a space for task priorities
    >>> task_space = PosetSpace(
    ...     name=PosetSpaceName("Tasks"),
    ...     description=Description("Project task priorities")
    ... )
    >>>
    >>> # Define tasks as elements
    >>> design = Element(
    ...     name=ElementName("Design"),
    ...     description=Description("UI/UX design phase"),
    ...     posetspace=task_space
    ... )
    >>> backend = Element(
    ...     name=ElementName("Backend"),
    ...     description=Description("API development"),
    ...     posetspace=task_space
    ... )
    >>> testing = Element(
    ...     name=ElementName("Testing"),
    ...     description=Description("Quality assurance"),
    ...     posetspace=task_space
    ... )
    >>>
    >>> # Create a poset with task dependencies
    >>> project_plan = Poset(
    ...     name=PosetName("Development Plan"),
    ...     description=Description("Task execution order"),
    ...     posetspace=task_space,
    ...     relations=[
    ...         Relation(less=design, greater=backend),   # design before backend
    ...         Relation(less=backend, greater=testing),  # backend before testing
    ...     ]
    ... )
    >>>
    >>> # Export to LaTeX for documentation
    >>> from coposet.types import ExportFormat
    >>> latex = project_plan.export(ExportFormat.LATEX)

Key Features:
    - Type-safe operations with branded types (ElementId, PosetId, etc.)
    - Voting workflows for interactive poset construction
    - Enrichment to add semantic information to relations
    - Mathematical operations (product, coproduct)
    - Export to LaTeX and MCDP formats
    - Consensus algorithms for aggregating multiple posets
"""

from .errors import (
    ConsensusError,
    CoposetError,
    EnrichmentError,
    ExportError,
    NotFoundError,
    RelationError,
    ValidationError,
    VotingError,
)
from .models import (
    Antichain,
    Element,
    Enricher,
    Poset,
    PosetSpace,
    Relation,
    VotedAntichain,
    Voter,
)
from .types import (
    AntichainId,
    ConsensusType,
    Description,
    ElementId,
    ElementName,
    EnricherId,
    ExportFormat,
    PosetId,
    PosetName,
    PosetSpaceId,
    PosetSpaceName,
    RelationId,
    VotedAntichainId,
    VoterId,
)

__version__ = "0.1.0"

__all__ = [
    # Core models
    "Element",
    "Poset",
    "Relation",
    "PosetSpace",
    # Voting system
    "Voter",
    "Antichain",
    "VotedAntichain",
    # Enrichment
    "Enricher",
    # Enums
    "ConsensusType",
    "ExportFormat",
    # Errors
    "CoposetError",
    "ValidationError",
    "NotFoundError",
    "RelationError",
    "ConsensusError",
    "ExportError",
    "VotingError",
    "EnrichmentError",
    # Branded types
    "PosetSpaceId",
    "PosetId",
    "ElementId",
    "RelationId",
    "VoterId",
    "AntichainId",
    "VotedAntichainId",
    "EnricherId",
    "PosetSpaceName",
    "PosetName",
    "ElementName",
    "Description",
]
