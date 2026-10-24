from functools import lru_cache

from fastembed import TextEmbedding

from app.models.resume_chunk import ResumeChunk


EMBEDDING_MODEL = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
EMBEDDING_DIMENSIONS = 384
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


@lru_cache(maxsize=1)
def get_embedding_model() -> TextEmbedding:
    """Load the multilingual embedding model once."""
    return TextEmbedding(model_name=EMBEDDING_MODEL)


def split_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Split text into overlapping chunks."""
    cleaned_text = " ".join(text.split())

    if not cleaned_text:
        return []

    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Invalid chunk_size or overlap.")

    chunks = []
    start = 0

    while start < len(cleaned_text):
        end = min(start + chunk_size, len(cleaned_text))
        chunk = cleaned_text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(cleaned_text):
            break

        start = end - overlap

    return chunks


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for text fragments."""
    if not texts:
        return []

    model = get_embedding_model()
    return [vector.tolist() for vector in model.embed(texts)]


def generate_query_embedding(query: str) -> list[float]:
    """Generate an embedding for a search query."""
    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    return generate_embeddings([query.strip()])[0]


def index_resume(db, resume) -> int:
    """Replace the stored chunks for a resume and return their count."""
    chunks = split_text(resume.extracted_text)

    db.query(ResumeChunk).filter(
        ResumeChunk.resume_id == resume.id,
        ResumeChunk.user_id == resume.user_id,
    ).delete(synchronize_session=False)

    if not chunks:
        db.commit()
        return 0

    embeddings = generate_embeddings(chunks)

    for index, (content, embedding) in enumerate(zip(chunks, embeddings)):
        db.add(
            ResumeChunk(
                resume_id=resume.id,
                user_id=resume.user_id,
                chunk_index=index,
                content=content,
                embedding=embedding,
            )
        )

    db.commit()
    return len(chunks)

def search_resume_chunks(
    db,
    resume_id: int,
    user_id: int,
    query: str,
    limit: int = 5,
) -> list[dict]:
    """Retrieve the most relevant resume chunks using cosine distance."""
    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    if limit < 1 or limit > 20:
        raise ValueError("Limit must be between 1 and 20.")

    query_embedding = generate_query_embedding(query)

    distance = ResumeChunk.embedding.cosine_distance(
        query_embedding
    ).label("distance")

    results = (
        db.query(ResumeChunk.content, distance)
        .filter(
            ResumeChunk.resume_id == resume_id,
            ResumeChunk.user_id == user_id,
        )
        .order_by(distance)
        .limit(limit)
        .all()
    )

    return [
        {
            "content": content,
            "distance": float(score),
        }
        for content, score in results
    ]
