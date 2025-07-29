# Coposet

Coposet is a tool for manipulating posets and allowing them to be  and exporting them to various formats.

## Posets (Partially Ordered Sets)

A poset is a set with a partial order relation (≤) that is:
- **Reflexive**: a ≤ a
- **Antisymmetric**: if a ≤ b and b ≤ a, then a = b
- **Transitive**: if a ≤ b and b ≤ c, then a ≤ c

The product of two posets P and Q creates a new poset P × Q where:
  - Elements: All pairs (p, q) where p ∈ P and q ∈ Q
  - Ordering: (p1, q1) ≤ (p2, q2) if and only if p1 ≤ p2 in P AND q1 ≤ q2 in Q

## Schema

### Core

posetspace:
- id: uuid
- name: string
- description: string
- posets: list of posets
- default_poset: poset
- elements: list of elements
- projections?: list of posetspaces
- injections?: list of posetspaces
- consensus(consensus_type) -> poset

poset:
- id: uuid
- name: string
- description: string
- posetspace: posetspace
- relations: list of relations
- enrichment?: posetspace
- product(poset, poset) -> (poset, posetspace)
- coproduct(poset, poset) -> (poset, posetspace)
- export(format: format) -> string

element:
- id: uuid
- name: string
- description: string
- posetspace: posetspace

relation<T: posetspace, E: posetspace>:
- id: uuid
- less: element<where less.posetspace == T>
- greater: element<where greater.posetspace == T>
- enrichment?: element<where enrichment.posetspace == E>

### Helpers

consensus_type:
- derive<T: posetspace>(array of posets<T>, dropEnrichments: boolean) -> poset<T>

format enum:
- mcdp, latex

### Voting
voter:
- poset: poset
- next_antichain(voted_antichain: voted_antichain<T>) -> Either<antichain<T>, poset>

antichain<T: posetspace>:
- id: uuid
- element: element<T>
- comparisons: set of elements<T>

voted_antichain<T: posetspace>:
- id: uuid
- antichain: antichain<T>
- new_less: set of elements<T>
- new_greater: set of elements<T>

### Enricher

enricher:
- poset: poset
- enrichment: posetspace
- enrich(relations: set<(relation<poset>, element<enrichment>)>) -> poset


## Details

We will use the [posets](https://pypi.org/project/posets/) library for the basic poset operations under the hood. This will be connected by a thin interface that converts the posets from the posets library to the coposet types we need to add on our layer of voting and consensus.

We should look into using [networkx](https://networkx.org) for the complex poset operations involved in consensus and voting.
