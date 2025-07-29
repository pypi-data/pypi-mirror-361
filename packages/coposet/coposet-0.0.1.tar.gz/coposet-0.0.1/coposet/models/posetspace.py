"""
PosetSpace and related types.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from ..types import (
    ConsensusType,
    Description,
    PosetName,
    PosetSpaceId,
    PosetSpaceName,
)

if TYPE_CHECKING:
    from .core import Element, Poset

# Import Poset at runtime to avoid circular import issues
import coposet.models.core


@dataclass
class PosetSpace:
    """A posetspace containing posets and elements.

    A posetspace is a mathematical structure that contains a collection of posets
    over a shared set of elements. It supports operations like consensus computation
    and can represent product/coproduct constructions through projections/injections.

    Attributes:
        name: Human-readable name for the posetspace.
        description: Detailed description of what the posetspace represents.
        id: Unique identifier for the posetspace (auto-generated if not provided).
        posets: List of posets in this space, all sharing the same element set.
        elements: List of elements available in this posetspace.
        projections: For product spaces, the component posetspaces.
        injections: For coproduct spaces, the component posetspaces.
        default_poset: Automatically created poset with no relations.

    Examples:
        >>> from coposet.models.core import Element
        >>> from coposet.types import PosetSpaceName, Description, ElementName
        >>>
        >>> # Create a space for restaurant preferences
        >>> food_space = PosetSpace(
        ...     name=PosetSpaceName("Restaurant Preferences"),
        ...     description=Description("Different aspects of dining experience")
        ... )
        >>>
        >>> # Add elements after creation
        >>> taste = Element(
        ...     name=ElementName("Taste"),
        ...     description=Description("Food quality and flavor"),
        ...     posetspace=food_space
        ... )
        >>> price = Element(
        ...     name=ElementName("Price"),
        ...     description=Description("Affordability"),
        ...     posetspace=food_space
        ... )
        >>> ambiance = Element(
        ...     name=ElementName("Ambiance"),
        ...     description=Description("Atmosphere and comfort"),
        ...     posetspace=food_space
        ... )
        >>> food_space.elements = [taste, price, ambiance]
        >>>
        >>> # The default poset has no relations (all elements incomparable)
        >>> print(len(food_space.default_poset.relations))
        0
        >>>
        >>> # Create multiple posets representing different user preferences
        >>> from coposet.models.core import Poset, Relation
        >>> from coposet.types import PosetName
        >>>
        >>> budget_conscious = Poset(
        ...     name=PosetName("Budget Diner"),
        ...     description=Description("Prioritizes affordability"),
        ...     posetspace=food_space,
        ...     relations=[
        ...         Relation(less=taste, greater=price),
        ...         Relation(less=ambiance, greater=price),
        ...     ]
        ... )
        >>> food_space.posets.append(budget_conscious)

    Note:
        Every posetspace automatically includes a default poset that contains
        all elements but no ordering relations (antichain).
    """

    name: PosetSpaceName
    description: Description
    id: PosetSpaceId = field(default_factory=lambda: PosetSpaceId(uuid4()))
    posets: list["Poset"] = field(default_factory=list)
    elements: list["Element"] = field(default_factory=list)
    projections: list["PosetSpace"] | None = None
    injections: list["PosetSpace"] | None = None
    default_poset: "Poset" = field(init=False)

    def __post_init__(self) -> None:
        """Initialize the default poset after all fields are set.

        This method is automatically called after dataclass initialization.
        It creates the default poset and adds it to the posets list.
        """
        self.default_poset = self.__default_poset()
        self.posets.append(self.default_poset)

    def __default_poset(self) -> "Poset":
        """Create the default poset (the one with no relations).

        The default poset contains all elements of the posetspace but no
        ordering relations, making it a complete antichain.

        Returns:
            A poset with no relations, named after the posetspace.

        Note:
            This is a private method called during initialization.
        """
        default_poset = coposet.models.core.Poset(
            name=PosetName(f"{self.name} (default)"),
            description=Description(
                f"Default poset for {self.name} with no relations."
            ),
            posetspace=self,
            relations=[],
            enrichment=None,
        )
        return default_poset

    def consensus(self, consensus_type: ConsensusType) -> "Poset":
        """Compute consensus poset from all posets in the space.

        Consensus computation aggregates multiple posets in the space to derive
        a single poset that represents the collective ordering. Different consensus
        types may use different aggregation strategies.

        Args:
            consensus_type: The type of consensus algorithm to use.

        Returns:
            A new poset representing the consensus of all posets in the space.

        Raises:
            NotImplementedError: Consensus algorithms are not yet implemented.

        Examples:
            >>> from coposet.types import ConsensusType
            >>>
            >>> # Create a space with multiple voter preferences
            >>> election_space = PosetSpace(
            ...     name=PosetSpaceName("Election"),
            ...     description=Description("Candidate preferences")
            ... )
            >>>
            >>> # Add candidates
            >>> alice = Element(ElementName("Alice"), Description("Candidate A"), election_space)
            >>> bob = Element(ElementName("Bob"), Description("Candidate B"), election_space)
            >>> carol = Element(ElementName("Carol"), Description("Candidate C"), election_space)
            >>> election_space.elements = [alice, bob, carol]
            >>>
            >>> # Add voter preference posets
            >>> voter1 = Poset(
            ...     name=PosetName("Voter 1"),
            ...     description=Description("First voter's ranking"),
            ...     posetspace=election_space,
            ...     relations=[
            ...         Relation(less=bob, greater=alice),   # Alice > Bob
            ...         Relation(less=carol, greater=alice),  # Alice > Carol
            ...     ]
            ... )
            >>> voter2 = Poset(
            ...     name=PosetName("Voter 2"),
            ...     description=Description("Second voter's ranking"),
            ...     posetspace=election_space,
            ...     relations=[
            ...         Relation(less=alice, greater=bob),   # Bob > Alice
            ...         Relation(less=carol, greater=bob),    # Bob > Carol
            ...     ]
            ... )
            >>> election_space.posets.extend([voter1, voter2])
            >>>
            >>> # Compute consensus (when implemented)
            >>> # consensus = election_space.consensus(ConsensusType.DERIVE)
            >>> # This would aggregate voter preferences into a collective ranking

        Note:
            Future implementations may support various consensus strategies such as
            majority voting, intersection, or optimization-based approaches.
        """
        # Skeleton implementation
        if consensus_type == ConsensusType.DERIVE:
            raise NotImplementedError("Consensus derivation not yet implemented")

        # This should never be reached with current enum values
        raise NotImplementedError(f"Unknown consensus type: {consensus_type}")
