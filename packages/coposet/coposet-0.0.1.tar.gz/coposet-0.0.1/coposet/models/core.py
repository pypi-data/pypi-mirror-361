"""
Core data structures: Element, Poset, and Relation.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from ..types import (
    Description,
    ElementId,
    ElementName,
    ExportFormat,
    PosetId,
    PosetName,
    PosetSpaceId,
    PosetSpaceName,
    RelationId,
)

if TYPE_CHECKING:
    from .posetspace import PosetSpace


@dataclass
class Element:
    """An element in a posetspace.

    Elements are the basic building blocks of posets. Each element belongs to a
    posetspace and has a unique identifier, name, and description.

    Attributes:
        name: Human-readable name for the element.
        description: Detailed description of what the element represents.
        posetspace: The posetspace this element belongs to.
        id: Unique identifier for the element (auto-generated if not provided).

    Examples:
        >>> from coposet.models.posetspace import PosetSpace
        >>> from coposet.types import PosetSpaceName, Description, ElementName
        >>>
        >>> # Create a posetspace for ethical choices
        >>> ethics_space = PosetSpace(
        ...     name=PosetSpaceName("Ethics"),
        ...     description=Description("Ethical decision space")
        ... )
        >>>
        >>> # Create elements representing different values
        >>> honesty = Element(
        ...     name=ElementName("Honesty"),
        ...     description=Description("Being truthful and transparent"),
        ...     posetspace=ethics_space
        ... )
        >>> kindness = Element(
        ...     name=ElementName("Kindness"),
        ...     description=Description("Being compassionate and caring"),
        ...     posetspace=ethics_space
        ... )
    """

    name: ElementName
    description: Description
    posetspace: "PosetSpace"
    id: ElementId = field(default_factory=lambda: ElementId(uuid4()))


@dataclass
class Relation:
    """A relation between two elements in a poset.

    Relations define the ordering between elements in a poset. Each relation
    represents that one element is less than another. Relations can optionally
    be enriched with additional semantic information.

    Attributes:
        less: The smaller element in the ordering relation.
        greater: The larger element in the ordering relation.
        enrichment: Optional enrichment element providing additional semantics.
        id: Unique identifier for the relation (auto-generated if not provided).

    Examples:
        >>> # Basic relation: honesty < kindness (kindness is preferred)
        >>> rel1 = Relation(less=honesty, greater=kindness)
        >>>
        >>> # Enriched relation with confidence level
        >>> confidence_space = PosetSpace(
        ...     name=PosetSpaceName("Confidence"),
        ...     description=Description("Confidence levels")
        ... )
        >>> high_conf = Element(
        ...     name=ElementName("High"),
        ...     description=Description("High confidence"),
        ...     posetspace=confidence_space
        ... )
        >>>
        >>> # Relation with enrichment: safety < efficiency (with high confidence)
        >>> rel2 = Relation(
        ...     less=safety,
        ...     greater=efficiency,
        ...     enrichment=high_conf
        ... )
    """

    less: Element
    greater: Element
    enrichment: Element | None = None
    id: RelationId = field(default_factory=lambda: RelationId(uuid4()))


@dataclass
class Poset:
    """A partially ordered set with elements and relations.

    A poset (partially ordered set) is a set of elements with a binary relation
    that is reflexive, antisymmetric, and transitive. This class represents a
    poset through its cover relations (direct ordering relationships).

    Attributes:
        name: Human-readable name for the poset.
        description: Detailed description of what the poset represents.
        posetspace: The posetspace this poset belongs to.
        id: Unique identifier for the poset (auto-generated if not provided).
        relations: List of cover relations defining the poset ordering.
        enrichment: Optional posetspace providing enrichment structure.

    Examples:
        >>> from coposet.types import PosetName
        >>>
        >>> # Create a preference poset for urban planning
        >>> urban_space = PosetSpace(
        ...     name=PosetSpaceName("Urban Planning"),
        ...     description=Description("City development priorities")
        ... )
        >>>
        >>> # Define elements
        >>> parks = Element(
        ...     name=ElementName("Parks"),
        ...     description=Description("Green spaces and recreation"),
        ...     posetspace=urban_space
        ... )
        >>> housing = Element(
        ...     name=ElementName("Housing"),
        ...     description=Description("Affordable housing development"),
        ...     posetspace=urban_space
        ... )
        >>> transit = Element(
        ...     name=ElementName("Transit"),
        ...     description=Description("Public transportation"),
        ...     posetspace=urban_space
        ... )
        >>>
        >>> # Create poset with community preferences
        >>> community_prefs = Poset(
        ...     name=PosetName("Community Priorities"),
        ...     description=Description("What the community values most"),
        ...     posetspace=urban_space,
        ...     relations=[
        ...         Relation(less=parks, greater=housing),  # housing > parks
        ...         Relation(less=parks, greater=transit),  # transit > parks
        ...         # Note: housing and transit remain incomparable
        ...     ]
        ... )
    """

    name: PosetName
    description: Description
    posetspace: "PosetSpace"
    id: PosetId = field(default_factory=lambda: PosetId(uuid4()))
    relations: list[Relation] = field(default_factory=list)
    enrichment: "PosetSpace | None" = None

    def get_elements(self) -> list[Element]:
        """Extract all unique elements from relations.

        Collects all elements that appear in any relation of this poset,
        ensuring each element appears only once in the result.

        Returns:
            List of unique elements ordered by first appearance in relations.

        Examples:
            >>> # Get all elements from a poset
            >>> elements = community_prefs.get_elements()
            >>> print([e.name for e in elements])
            ['Parks', 'Housing', 'Transit']
            >>>
            >>> # Works even with complex relation structures
            >>> complex_poset = Poset(
            ...     name=PosetName("Complex"),
            ...     description=Description("Multi-level ordering"),
            ...     posetspace=space,
            ...     relations=[
            ...         Relation(less=a, greater=b),
            ...         Relation(less=b, greater=c),
            ...         Relation(less=a, greater=d),
            ...         Relation(less=d, greater=c),
            ...     ]
            ... )
            >>> # Returns [a, b, c, d] in order of first appearance
        """
        seen_ids = set()
        elements = []
        for relation in self.relations:
            if relation.less.id not in seen_ids:
                seen_ids.add(relation.less.id)
                elements.append(relation.less)
            if relation.greater.id not in seen_ids:
                seen_ids.add(relation.greater.id)
                elements.append(relation.greater)
        return elements

    def product(self, other: "Poset") -> tuple["Poset", "PosetSpace"]:
        """Compute the product of two posets.

        The product operation creates a new poset whose elements are ordered pairs
        (a, b) where a comes from self and b comes from other. The ordering is
        defined component-wise: (a1, b1) <= (a2, b2) if and only if a1 <= a2 in
        self and b1 <= b2 in other.

        Args:
            other: The second poset to form the product with.

        Returns:
            A tuple containing:
            - The product poset with paired elements and component-wise ordering
            - The product posetspace containing both posets and projection mappings

        Examples:
            >>> # Restaurant rating example: combine food quality and service ratings
            >>> food_space = PosetSpace(
            ...     name=PosetSpaceName("Food Quality"),
            ...     description=Description("Restaurant food ratings")
            ... )
            >>> service_space = PosetSpace(
            ...     name=PosetSpaceName("Service Quality"),
            ...     description=Description("Restaurant service ratings")
            ... )
            >>>
            >>> # Food quality levels
            >>> poor_food = Element(ElementName("Poor"), Description("Low quality"), food_space)
            >>> good_food = Element(ElementName("Good"), Description("Good quality"), food_space)
            >>> excellent_food = Element(ElementName("Excellent"), Description("Top quality"), food_space)
            >>>
            >>> # Service quality levels
            >>> slow_service = Element(ElementName("Slow"), Description("Poor service"), service_space)
            >>> ok_service = Element(ElementName("OK"), Description("Adequate service"), service_space)
            >>> great_service = Element(ElementName("Great"), Description("Excellent service"), service_space)
            >>>
            >>> # Create rating posets
            >>> food_ratings = Poset(
            ...     name=PosetName("Food Ratings"),
            ...     description=Description("Food quality ordering"),
            ...     posetspace=food_space,
            ...     relations=[
            ...         Relation(less=poor_food, greater=good_food),
            ...         Relation(less=good_food, greater=excellent_food),
            ...     ]
            >>> )
            >>>
            >>> service_ratings = Poset(
            ...     name=PosetName("Service Ratings"),
            ...     description=Description("Service quality ordering"),
            ...     posetspace=service_space,
            ...     relations=[
            ...         Relation(less=slow_service, greater=ok_service),
            ...         Relation(less=ok_service, greater=great_service),
            ...     ]
            >>> )
            >>>
            >>> # Compute product for overall restaurant ratings
            >>> overall_ratings, rating_space = food_ratings.product(service_ratings)
            >>>
            >>> # Product contains combinations like:
            >>> # (Poor,Slow), (Poor,OK), (Poor,Great),
            >>> # (Good,Slow), (Good,OK), (Good,Great),
            >>> # (Excellent,Slow), (Excellent,OK), (Excellent,Great)
            >>> #
            >>> # With ordering: (Poor,Slow) < (Good,OK) < (Excellent,Great)
            >>> # But (Good,Slow) and (Poor,OK) are incomparable

        Note:
            The product posetspace includes projection mappings back to the
            original posetspaces, allowing recovery of the component elements.
        """
        from ..adapters import PosetAdapter
        from .posetspace import PosetSpace

        # Get source posetspaces
        self_space = self.posetspace
        other_space = other.posetspace

        # Convert to library posets using UUIDs
        self_adapter = PosetAdapter(self)
        other_adapter = PosetAdapter(other)

        self_lib = self_adapter.to_library_poset()
        other_lib = other_adapter.to_library_poset()

        # Compute cartesian product using the library
        product_lib = self_lib.cartesianProduct(other_lib)

        # Create maps from UUID to element for both posets
        # Use the adapter's elements which handles antichains correctly
        self_elem_by_uuid = {str(elem.id): elem for elem in self_adapter._elements}
        other_elem_by_uuid = {str(elem.id): elem for elem in other_adapter._elements}

        # First, create product elements without posetspace reference
        temp_elements: dict[
            tuple[str, str], tuple[ElementId, ElementName, Description]
        ] = {}

        # The library product has elements as tuples like (uuid1, uuid2)
        for product_uuid_pair in product_lib.elements:
            # The library gives us tuples
            uuid1, uuid2 = product_uuid_pair

            # Get the original elements
            self_elem = self_elem_by_uuid[uuid1]
            other_elem = other_elem_by_uuid[uuid2]

            # Store element data for later creation
            temp_elements[product_uuid_pair] = (
                ElementId(uuid4()),
                ElementName(f"({self_elem.name},{other_elem.name})"),
                Description(
                    f"Product of {self_elem.description} and {other_elem.description}"
                ),
            )

        # Now create the product PosetSpace (it will create its own default poset)
        product_space = PosetSpace(
            id=PosetSpaceId(uuid4()),
            name=PosetSpaceName(f"{self.name} × {other.name} Space"),
            description=Description(f"Product space of {self.name} and {other.name}"),
            posets=[],
            elements=[],
            projections=[self_space, other_space],
            injections=None,
        )

        # Now create the actual elements with the correct posetspace reference
        product_elements: list[Element] = []
        element_map: dict[tuple[str, str] | str, Element] = {}

        for uuid_pair, (elem_id, elem_name, elem_desc) in temp_elements.items():
            elem = Element(
                name=elem_name,
                description=elem_desc,
                posetspace=product_space,
                id=elem_id,
            )
            product_elements.append(elem)
            element_map[uuid_pair] = elem

        # Extract relations from the library product
        product_relations: list[Relation] = []

        # Get cover relations from the library
        covers_dict = product_lib.covers()

        # covers_dict maps elements to lists of elements that cover them
        # If a is in covers_dict[b], then a covers b, meaning b < a
        for less_elem_pair, covering_elems in covers_dict.items():
            if less_elem_pair in element_map:
                less_elem = element_map[less_elem_pair]

                for greater_elem_pair in covering_elems:
                    if greater_elem_pair in element_map:
                        greater_elem = element_map[greater_elem_pair]

                        relation = Relation(
                            less=less_elem,
                            greater=greater_elem,
                            enrichment=None,
                        )
                        product_relations.append(relation)

        # Create the product poset
        product_poset = Poset(
            name=PosetName(f"{self.name} × {other.name}"),
            description=Description(f"Product of {self.name} and {other.name}"),
            posetspace=product_space,
            relations=product_relations,
            enrichment=None,
        )

        # Update the product space with the correct elements and add the product poset
        # Since PosetSpace is mutable, we need to create a new one
        final_product_space = PosetSpace(
            id=product_space.id,
            name=product_space.name,
            description=product_space.description,
            posets=[
                product_space.default_poset,
                product_poset,
            ],  # Include both default and product
            elements=product_elements,
            projections=product_space.projections,
            injections=product_space.injections,
        )

        # The product poset is the one with actual relations, not the default
        return product_poset, final_product_space

    def coproduct(self, other: "Poset") -> tuple["Poset", "PosetSpace"]:
        """Compute the coproduct (disjoint union) of two posets.

        The coproduct operation creates a new poset that contains all elements
        from both input posets, with relations preserved within each component
        but no new relations between components. Elements are prefixed with
        'L_' (left) or 'R_' (right) to indicate their source.

        Args:
            other: The second poset to form the coproduct with.

        Returns:
            A tuple containing:
            - The coproduct poset with disjoint union of elements
            - The coproduct posetspace containing both posets and injection mappings

        Examples:
            >>> # Merge preferences from two different departments
            >>> eng_space = PosetSpace(
            ...     name=PosetSpaceName("Engineering Dept"),
            ...     description=Description("Engineering priorities")
            ... )
            >>> sales_space = PosetSpace(
            ...     name=PosetSpaceName("Sales Dept"),
            ...     description=Description("Sales priorities")
            ... )
            >>>
            >>> # Engineering priorities
            >>> reliability = Element(ElementName("Reliability"), Description("System uptime"), eng_space)
            >>> performance = Element(ElementName("Performance"), Description("Speed"), eng_space)
            >>> scalability = Element(ElementName("Scalability"), Description("Growth capacity"), eng_space)
            >>>
            >>> # Sales priorities
            >>> price = Element(ElementName("Price"), Description("Competitive pricing"), sales_space)
            >>> features = Element(ElementName("Features"), Description("Feature richness"), sales_space)
            >>> usability = Element(ElementName("Usability"), Description("Ease of use"), sales_space)
            >>>
            >>> # Engineering preferences
            >>> eng_prefs = Poset(
            ...     name=PosetName("Engineering Priorities"),
            ...     description=Description("What engineering values"),
            ...     posetspace=eng_space,
            ...     relations=[
            ...         Relation(less=performance, greater=reliability),  # reliability > performance
            ...         Relation(less=scalability, greater=reliability),  # reliability > scalability
            ...     ]
            >>> )
            >>>
            >>> # Sales preferences
            >>> sales_prefs = Poset(
            ...     name=PosetName("Sales Priorities"),
            ...     description=Description("What sales values"),
            ...     posetspace=sales_space,
            ...     relations=[
            ...         Relation(less=price, greater=features),   # features > price
            ...         Relation(less=usability, greater=features),  # features > usability
            ...     ]
            >>> )
            >>>
            >>> # Create coproduct to see all priorities without forcing comparisons
            >>> all_prefs, combined_space = eng_prefs.coproduct(sales_prefs)
            >>>
            >>> # Result contains:
            >>> # L_Reliability, L_Performance, L_Scalability (from engineering)
            >>> # R_Features, R_Price, R_Usability (from sales)
            >>> #
            >>> # With relations:
            >>> # L_Performance < L_Reliability, L_Scalability < L_Reliability
            >>> # R_Price < R_Features, R_Usability < R_Features
            >>> #
            >>> # But no relations between L_* and R_* elements
            >>> # This preserves department autonomy while combining views

        Note:
            The coproduct posetspace includes injection mappings from the
            original posetspaces, preserving the source information.
        """
        from ..adapters import PosetAdapter
        from .posetspace import PosetSpace

        # Get source posetspaces
        self_space = self.posetspace
        other_space = other.posetspace

        # Convert to library posets using UUIDs
        self_adapter = PosetAdapter(self)
        other_adapter = PosetAdapter(other)

        self_lib = self_adapter.to_library_poset()
        other_lib = other_adapter.to_library_poset()

        # Compute disjoint union using the library
        coproduct_lib = self_lib.union(other_lib)

        # Create maps from UUID to element for both posets
        # Use the adapter's elements which handles antichains correctly
        self_elem_by_uuid = {str(elem.id): elem for elem in self_adapter._elements}
        other_elem_by_uuid = {str(elem.id): elem for elem in other_adapter._elements}

        # First, create coproduct elements without posetspace reference
        temp_elements: dict[
            tuple[str, int] | str, tuple[ElementId, ElementName, Description]
        ] = {}

        # The library union creates elements as either original elements (if disjoint)
        # or tuples like (element, 0) and (element, 1) to ensure disjointness
        for union_elem in coproduct_lib.elements:
            if isinstance(union_elem, tuple):
                # This is a disambiguated element (uuid, index)
                uuid, index = union_elem
                if index == 0:
                    # From self
                    orig_elem = self_elem_by_uuid[str(uuid)]
                    elem_name = ElementName(f"L_{orig_elem.name}")
                    elem_desc = Description(
                        f"Left injection of {orig_elem.description}"
                    )
                else:
                    # From other
                    orig_elem = other_elem_by_uuid[str(uuid)]
                    elem_name = ElementName(f"R_{orig_elem.name}")
                    elem_desc = Description(
                        f"Right injection of {orig_elem.description}"
                    )
            else:
                # Element appears only in one poset, no disambiguation needed
                uuid = str(union_elem)
                if uuid in self_elem_by_uuid:
                    orig_elem = self_elem_by_uuid[uuid]
                    elem_name = ElementName(f"L_{orig_elem.name}")
                    elem_desc = Description(
                        f"Left injection of {orig_elem.description}"
                    )
                else:
                    orig_elem = other_elem_by_uuid[uuid]
                    elem_name = ElementName(f"R_{orig_elem.name}")
                    elem_desc = Description(
                        f"Right injection of {orig_elem.description}"
                    )

            temp_elements[union_elem] = (
                ElementId(uuid4()),
                elem_name,
                elem_desc,
            )

        # Now create the coproduct PosetSpace (it will create its own default poset)
        coproduct_space = PosetSpace(
            id=PosetSpaceId(uuid4()),
            name=PosetSpaceName(f"{self.name} + {other.name} Space"),
            description=Description(f"Coproduct space of {self.name} and {other.name}"),
            posets=[],
            elements=[],
            projections=None,
            injections=[self_space, other_space],
        )

        # Now create the actual elements with the correct posetspace reference
        coproduct_elements: list[Element] = []
        element_map: dict[tuple[str, int] | str, Element] = {}

        for union_elem, (elem_id, elem_name, elem_desc) in temp_elements.items():
            elem = Element(
                name=elem_name,
                description=elem_desc,
                posetspace=coproduct_space,
                id=elem_id,
            )
            coproduct_elements.append(elem)
            element_map[union_elem] = elem

        # Extract relations from the library coproduct
        coproduct_relations: list[Relation] = []

        # Get cover relations from the library
        covers_dict = coproduct_lib.covers()

        # covers_dict maps elements to lists of elements that cover them
        # If a is in covers_dict[b], then a covers b, meaning b < a
        for less_elem, covering_elems in covers_dict.items():
            if less_elem in element_map:
                less_elem_obj = element_map[less_elem]

                for greater_elem in covering_elems:
                    if greater_elem in element_map:
                        greater_elem_obj = element_map[greater_elem]

                        relation = Relation(
                            less=less_elem_obj,
                            greater=greater_elem_obj,
                            enrichment=None,
                        )
                        coproduct_relations.append(relation)

        # Create the coproduct poset
        coproduct_poset = Poset(
            name=PosetName(f"{self.name} + {other.name}"),
            description=Description(f"Coproduct of {self.name} and {other.name}"),
            posetspace=coproduct_space,
            relations=coproduct_relations,
            enrichment=None,
        )

        # Update the coproduct space with the correct elements and add the coproduct poset
        # Since PosetSpace is mutable, we need to create a new one
        final_coproduct_space = PosetSpace(
            id=coproduct_space.id,
            name=coproduct_space.name,
            description=coproduct_space.description,
            posets=[
                coproduct_space.default_poset,
                coproduct_poset,
            ],  # Include both default and coproduct
            elements=coproduct_elements,
            projections=coproduct_space.projections,
            injections=coproduct_space.injections,
        )

        # The coproduct poset is the one with actual relations, not the default
        return coproduct_poset, final_coproduct_space

    def export(self, format: ExportFormat) -> str:
        """Export the poset to a specified format.

        Converts the poset representation into various output formats suitable
        for visualization, documentation, or integration with other tools.

        Args:
            format: The desired export format (LATEX or MCDP).

        Returns:
            String representation of the poset in the requested format.

        Raises:
            NotImplementedError: If the requested format is not yet supported.

        Examples:
            >>> from coposet.types import ExportFormat
            >>>
            >>> # Export to LaTeX for paper figures
            >>> latex_code = community_prefs.export(ExportFormat.LATEX)
            >>> print(latex_code[:50] + "...")
            \begin{tikzpicture}[node distance=2cm]...
            >>>
            >>> # Use in a LaTeX document
            >>> latex_doc = f'''
            ... \\documentclass{{article}}
            ... \\usepackage{{tikz}}
            ... \\begin{{document}}
            ... {latex_code}
            ... \\end{{document}}
            ... '''
            >>>
            >>> # MCDP export for engineering co-design (future)
            >>> # mcdp_code = poset.export(ExportFormat.MCDP)

        Note:
            - LATEX format uses element names for readability
            - MCDP format is not yet implemented
        """
        if format == ExportFormat.LATEX:
            # Import here to avoid circular import issues
            from posets import Poset as LibraryPoset

            # For export, we want to use names not UUIDs for readability
            # So we'll create a temporary library poset with names
            relations_dict: dict[str, list[str]] = {}
            elements = self.get_elements()

            for elem in elements:
                relations_dict[elem.name] = []

            for relation in self.relations:
                less_name = relation.less.name
                greater_name = relation.greater.name
                if less_name not in relations_dict:
                    relations_dict[less_name] = []
                relations_dict[less_name].append(greater_name)

            lib_poset = LibraryPoset(relations=relations_dict)
            latex_output: str = lib_poset.latex()
            return latex_output
        elif format == ExportFormat.MCDP:
            # MCDP format would need custom implementation
            raise NotImplementedError("MCDP export not yet implemented")

        # This should never be reached with current enum values
        raise NotImplementedError(f"Unknown export format: {format}")
