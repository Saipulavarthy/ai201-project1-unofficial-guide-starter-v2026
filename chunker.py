"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


# Topic prefix -> the companion suffixes that belong with its base post.
# course_cs_210.txt + course_cs_210_exams.txt + course_cs_210_workload.txt
# all share the key ("course", "cs_210").
CLUSTER_SUFFIXES = {
    "course": ("_exams", "_workload"),
    "dining": ("_followup",),
    "housing": ("_noise", "_laundry"),
}


def _cluster_key(filename: str) -> tuple[str, str] | None:
    """Return (prefix, topic) for a clusterable file, or None if it stands alone."""
    stem = filename.removesuffix(".txt")
    prefix, _, rest = stem.partition("_")
    if prefix not in CLUSTER_SUFFIXES or not rest:
        return None
    for suffix in CLUSTER_SUFFIXES[prefix]:
        if rest.endswith(suffix):
            return prefix, rest.removesuffix(suffix)
    return prefix, rest


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split documents into chunks — one topic, one chunk.

    These are short posts, not long guides, so nothing is ever cut. But the
    narrow companion posts (a course's exam and workload notes, a dining
    hall's follow-up, a hall's noise and laundry notes) are too thin to stand
    on their own and kept landing in retrieval as 200-300 character scraps.
    So each companion is merged with its base post into one chunk: base file
    first, then the companions alphabetically, joined by a blank line, with
    every filename in the cluster joined by "+" as the source. Everything
    else stays one whole document, one chunk at index 0.
    """
    clusters: dict[tuple[str, str], list[Document]] = {}
    order: list[tuple[str, str] | Document] = []
    for doc in documents:
        key = _cluster_key(doc.source)
        if key is None:
            order.append(doc)
        else:
            if key not in clusters:
                clusters[key] = []
                order.append(key)
            clusters[key].append(doc)

    chunks: list[Chunk] = []
    for item in order:
        if isinstance(item, Document):
            group = [item]
        else:
            prefix, topic = item
            base = f"{prefix}_{topic}.txt"
            group = sorted(clusters[item], key=lambda d: (d.source != base, d.source))
        chunks.append(
            Chunk(
                text="\n\n".join(d.text.strip() for d in group).strip(),
                source="+".join(d.source for d in group),
                index=0,
                produced_by="chunker.py::split_documents",
            )
        )
    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
