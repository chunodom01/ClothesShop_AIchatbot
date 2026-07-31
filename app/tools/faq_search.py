"""FAQ retrieval tool backed by Pinecone."""
from langchain_core.tools import tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pinecone import Pinecone
from app.config import settings

# Build clients ONCE at import, reuse on every call.
_embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=settings.google_api_key,
    output_dimensionality=768,  # ✅ must match your Pinecone index dimension
)

# ✅ Initialize Pinecone client and index
pc = Pinecone(api_key=settings.pinecone_api_key)
_index = pc.Index(settings.pinecone_index_name)

SCORE_THRESHOLD = 0.5

@tool
def search_faq(query: str) -> str:
    """Look up the pet salon's FAQ to answer customer questions about hours,
    prices, services, location, payment, booking, and policies.
    Call this whenever the customer asks anything about the business."""
    # Embed the query
    vector = _embeddings.embed_query(query)

    # Query Pinecone index
    result = _index.query(vector=vector, top_k=3, include_metadata=True)

    # Filter matches by score
    matches = [m for m in result["matches"] if m["score"] >= SCORE_THRESHOLD]
    if not matches:
        return "No relevant FAQ found. Tell the customer you'll check and follow up."

    # Format answers
    return "\n\n".join(
        f"Q: {m['metadata']['question']}\nA: {m['metadata']['answer']}"
        for m in matches
    )
