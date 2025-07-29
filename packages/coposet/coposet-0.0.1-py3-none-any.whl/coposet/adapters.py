"""Adapter layer to connect coposet types to the posets library."""

from posets import Poset as LibraryPoset

from coposet.models.core import Element, Poset, Relation
from coposet.models.posetspace import PosetSpace
from coposet.types import ElementId, ElementName, PosetId


class PosetAdapter:
    """Adapter to convert between coposet Poset and posets library Poset."""

    def __init__(self, poset: Poset) -> None:
        """Initialize adapter with a coposet Poset.

        Args:
            poset: The coposet Poset to adapt
        """
        self.poset = poset
        # Get all elements from the poset itself (not the entire space)
        self._elements: list[Element] = poset.get_elements()

        # Special case: if the poset has no relations (antichain), we need to determine
        # which elements belong to it. For now, we'll use a heuristic:
        # If a poset has no relations, we need to figure out which elements belong to it.
        # We'll use the following approach:
        # - If there are other posets with relations, exclude their elements
        # - Use the remaining elements for the antichain
        if not self._elements and not poset.relations:
            # Get all elements that appear in other posets' relations
            used_element_ids = set()
            for other_poset in poset.posetspace.posets:
                if other_poset.id != poset.id:
                    for rel in other_poset.relations:
                        used_element_ids.add(rel.less.id)
                        used_element_ids.add(rel.greater.id)

            # Use elements that aren't used in other posets
            self._elements = [
                elem
                for elem in poset.posetspace.elements
                if elem.id not in used_element_ids
            ]

            # If all elements are used, fall back to using all elements
            if not self._elements:
                self._elements = list(poset.posetspace.elements)

    def to_library_poset(self) -> LibraryPoset:
        """Convert coposet Poset to posets library Poset using UUIDs.

        Returns:
            A posets library Poset instance with element UUIDs as identifiers
        """
        # Build relations dictionary using UUIDs as identifiers
        relations_dict: dict[str, list[str]] = {}

        # Initialize all elements with empty lists
        for element in self._elements:
            relations_dict[str(element.id)] = []

        # Add relations
        for relation in self.poset.relations:
            less_uuid = str(relation.less.id)
            greater_uuid = str(relation.greater.id)

            if less_uuid not in relations_dict:
                relations_dict[less_uuid] = []
            relations_dict[less_uuid].append(greater_uuid)

        # Create library poset
        return LibraryPoset(relations=relations_dict)

    def from_library_operations(
        self, library_poset: LibraryPoset, operation_name: str
    ) -> tuple[Poset, PosetSpace]:
        """Convert a posets library Poset back to coposet types after an operation.

        Args:
            library_poset: The result from a library operation
            operation_name: Name of the operation (e.g., 'product', 'coproduct')

        Returns:
            Tuple of (new Poset, optional new PosetSpace for product/coproduct)
        """
        # This is a placeholder - implementation depends on how the library
        # represents product/coproduct results
        raise NotImplementedError(
            f"Conversion from library poset after {operation_name} not yet implemented"
        )


class ElementAdapter:
    """Adapter for converting elements between coposet and posets library."""

    @staticmethod
    def elements_to_names(elements: set[Element]) -> list[str]:
        """Convert a set of coposet Elements to a list of names.

        Args:
            elements: Set of coposet Elements

        Returns:
            List of element names
        """
        return [elem.name for elem in elements]

    @staticmethod
    def create_element_mapping(
        elements: set[Element],
    ) -> tuple[dict[ElementName, ElementId], dict[ElementId, ElementName]]:
        """Create bidirectional mapping between element names and IDs.

        Args:
            elements: Set of coposet Elements

        Returns:
            Tuple of (name_to_id, id_to_name) dictionaries
        """
        name_to_id = {elem.name: elem.id for elem in elements}
        id_to_name = {elem.id: elem.name for elem in elements}
        return name_to_id, id_to_name


class RelationAdapter:
    """Adapter for converting relations between coposet and posets library."""

    @staticmethod
    def relations_to_dict(
        relations: set[Relation], id_to_name: dict[ElementId, ElementName]
    ) -> dict[str, list[str]]:
        """Convert coposet Relations to posets library relations dictionary.

        Args:
            relations: Set of coposet Relations
            id_to_name: Mapping from ElementId to element names

        Returns:
            Dictionary mapping element names to lists of greater element names
        """
        relations_dict: dict[str, list[str]] = {}

        for relation in relations:
            less_name = id_to_name[relation.less.id]
            greater_name = id_to_name[relation.greater.id]

            if less_name not in relations_dict:
                relations_dict[less_name] = []
            relations_dict[less_name].append(greater_name)

        return relations_dict

    @staticmethod
    def dict_to_relations(
        relations_dict: dict[str, list[str]],
        name_to_id: dict[ElementName, ElementId],
        elements_by_id: dict[ElementId, Element],
        poset_id: PosetId,
    ) -> set[Relation]:
        """Convert posets library relations dictionary to coposet Relations.

        Args:
            relations_dict: Dictionary from posets library
            name_to_id: Mapping from element names to ElementId
            poset_id: ID of the poset these relations belong to

        Returns:
            Set of coposet Relations
        """
        relations = set()

        for less_name, greater_names in relations_dict.items():
            less_name_typed = ElementName(less_name)
            less_id = name_to_id[less_name_typed]
            less_elem = elements_by_id[less_id]

            for greater_name in greater_names:
                greater_name_typed = ElementName(greater_name)
                greater_id = name_to_id[greater_name_typed]
                greater_elem = elements_by_id[greater_id]

                relation = Relation(
                    less=less_elem,
                    greater=greater_elem,
                    enrichment=None,
                )
                relations.add(relation)

        return relations
