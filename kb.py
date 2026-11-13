"""Knowledge Base: indexes data/ into ChromaDB and searches it."""
from pathlib import Path

import chromadb
from pypdf import PdfReader

DATA_DIR = Path(__file__).parent / "data"
DB_DIR = Path(__file__).parent / "chroma_db"
# Cosine distance above which a match is treated as "not in the documents".
THRESHOLD = 0.68  # shortcut: tuned by hand on the sample docs, retune when the Knowledge Base changes


def _collection():
    client = chromadb.PersistentClient(path=str(DB_DIR))
    return client.get_or_create_collection("knowledge_base", metadata={"hnsw:space": "cosine"})


def _read(path: Path) -> str:
    if path.suffix == ".pdf":
        return "\n\n".join(p.extract_text() or "" for p in PdfReader(path).pages)
    return path.read_text()


def _chunks(text: str, size: int = 250):
    buf = ""
    for para in (p.strip() for p in text.split("\n\n") if p.strip()):
        if buf and len(buf) + len(para) > size:
            yield buf
            buf = ""
        buf = f"{buf}\n\n{para}".strip()
    if buf:
        yield buf


def ingest() -> int:
    """Rebuild the index from data/*.txt and data/*.pdf. Returns chunk count."""
    col = _collection()
    existing = col.get()["ids"]
    if existing:
        col.delete(ids=existing)
    docs, ids, metas = [], [], []
    for path in sorted([*DATA_DIR.glob("*.txt"), *DATA_DIR.glob("*.pdf")]):
        for i, chunk in enumerate(_chunks(_read(path))):
            docs.append(chunk)
            ids.append(f"{path.name}-{i}")
            metas.append({"source": path.name})
    if docs:
        col.add(documents=docs, ids=ids, metadatas=metas)
    return len(docs)


def search(query: str, k: int = 3) -> str:
    """Relevant passages with sources, or the literal NOT_FOUND."""
    col = _collection()
    if col.count() == 0:
        ingest()
    res = col.query(query_texts=[query], n_results=k)
    hits = [
        (doc, meta["source"])
        for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0])
        if dist <= THRESHOLD
    ]
    if not hits:
        return "NOT_FOUND"
    return "\n\n".join(f"[{src}]\n{doc}" for doc, src in hits)
