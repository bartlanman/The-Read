# Symbol Index — working local search

The first operational index for the [Symbolic Masterwork](../README.md). This is a **versioned, searchable JSON catalog** with a dependency-free Python search tool, not yet a hosted database or automated semantic engine.

## Contents
- [symbols.json](symbols.json) — records for Spiral (SYM-0001), Threshold (SYM-0002), and their collision The Altered Horizon (MW-0001), plus six resource-collection lens definitions.
- [search_index.py](search_index.py) — full-text keyword filtering over titles, aliases, propositions, formal structure, cultural contexts and keywords; cross-reference validation.
- Existing detailed historical and creative files remain the source of truth. The index is a *discovery layer* and links back to those files.

## Run locally
From a checkout of the repository:

```bash
python3 Protocols/Symbolic_Masterwork/Index/search_index.py --validate
python3 Protocols/Symbolic_Masterwork/Index/search_index.py spiral
python3 Protocols/Symbolic_Masterwork/Index/search_index.py passage
python3 Protocols/Symbolic_Masterwork/Index/search_index.py --kind masterwork_collision perception
```

A search automatically logs a timestamped retrieval record in `encounters.local.jsonl` **in your local checkout**. That file is not automatically pushed to GitHub. Review and curate research encounters before adding them to the versioned [Atlas encounter ledgers](../Examples/Spiral/ATLAS_AND_ENCOUNTERS.md). This avoids silently elevating search results into historical facts.

## How to add a symbol
1. Complete a Symbol Read and source Encounter Records under `Examples/<Name>/`.
2. Add one item with unique `SYM-000N` or `MW-000N` ID, proposition epistemic type, aliases, contexts, file links, and meaningful relationship edges to `symbols.json`.
3. Keep independently supported history separate from creative proposals. Include unresolved questions and visual status.
4. Run `--validate`. The validator checks IDs, relationships and file links.
5. Commit index + source records together. Do not claim a collection is imported without actually obtaining authorized data access.

**Scope:** The six named collections are reference *lenses*, not embedded licensed catalogs. Index coverage remains incomplete and first-pass; this does not itself consult the collections or verify their full text.

**Operational safeguard:** A lookup can identify a relationship to investigate, but only a later reviewed Encounter Record can assert the source context and possible new meaning.
