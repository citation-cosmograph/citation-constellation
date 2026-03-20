"""
citation-constellation/app/BARON_and_HEROCON.py
=======================================
Information about how BARON and HEROCON work
"""

BARON_and_HEROCON = """
**How BARON and HEROCON Work**

BARON and HEROCON are two ways to measure the same thing: how much of a researcher's citation profile comes from outside their immediate professional circle. They use the same underlying data but compute differently.

---

### The Core Idea

Every citation a researcher receives gets checked against their professional network. The system looks for connections between the researcher and the citing author across three layers:

1. **Self** – The researcher cited themselves  
2. **Co-authors** – Someone they've published with (or their collaborators)  
3. **Institution** – Colleagues at their university or organization  

If none of these apply, the citation is **External**.

BARON and HEROCON classify citations into these layers differently. BARON is strict. HEROCON is flexible.

---

### BARON (Binary)

BARON treats every citation as either inside the researcher's network or outside it.

- **In-group** (self, co-author, institutional colleague, venue connection) = **0 points**
- **External** = **1 point**

**Calculation:**
```
BARON = (External citations ÷ Classifiable citations) × 100
```

A BARON score of 65% means 65% of the researcher's classifiable citations came from people with no detected connection to them.

*Classifiable citations exclude any citations where the system lacks data to determine the relationship (marked as UNKNOWN).*

---

### HEROCON (Graduated)

HEROCON gives partial credit for in-group citations based on how close the connection is. Instead of 0 or 1, each category has a weight between 0 and 1.

| Connection Type | Weight | Rationale |
|----------------|--------|-----------|
| Self-citation | 0.0 | No credit |
| Same department | 0.1 | Forced proximity, no collaboration |
| Direct co-author | 0.2 | Chosen collaboration |
| Transitive co-author | 0.5 | Friend-of-friend |
| Same institution (different dept) | 0.4 | Same university, different field |
| Same parent organization | 0.7 | Shared umbrella (e.g., UC system) |
| External | 1.0 | Full credit |

**Calculation:**
```
HEROCON = (Sum of all citation weights ÷ Classifiable citations) × 100
```

HEROCON will always be equal to or higher than BARON because it gives partial credit where BARON gives zero.

---

### The Gap

**Gap = HEROCON − BARON**

The gap measures how much of the researcher's impact depends on their inner circle.

- **Small gap (0–10%)**: Most citations come from independent sources; the researcher's network provides minimal boost
- **Large gap (20%+)**: Many citations flow through professional relationships; the collaborative network is a major channel

---

### The Detection Layers

The system builds the researcher's network in phases. Each phase adds a new detection layer:

**Phase 1: Identity**
Checks if the citing author is the researcher (self-citation).

**Phase 2: Co-authorship**  
Builds a graph of everyone the researcher has published with. By default, checks connections up to two degrees out (co-authors' co-authors).

**Phase 3: Affiliation**  
Checks if the citing author worked at the same institution as the researcher when the citation was made. Uses publication dates to match contemporaneous affiliations, not current ones.

---

### Data Quality Handling

When the system cannot determine an affiliation or relationship (missing metadata), it classifies the citation as **UNKNOWN**. These citations are excluded from both BARON and HEROCON calculations rather than assumed external.

This prevents artificially high scores for researchers with incomplete metadata, but it means the scores reflect only the *classifiable* portion of the researcher's citation profile (typically 70–90% of total citations, depending on data availability).
"""
