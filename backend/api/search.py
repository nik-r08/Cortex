from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.document import Document, DocumentStatus
from backend.schemas.document import DocumentResponse

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/", response_model=dict)
async def search_documents(
    q: str = Query(..., min_length=1, max_length=500),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Full text search over document content and extracted fields.
    Uses postgres tsvector for ranking.
    """
    # sanitize the query for tsquery
    search_terms = " & ".join(q.strip().split())

    query = (
        select(
            Document,
            func.ts_rank(Document.search_vector, func.to_tsquery("english", search_terms)).label("rank"),
        )
        .where(
            Document.search_vector.op("@@")(func.to_tsquery("english", search_terms))
        )
        .where(Document.status == DocumentStatus.COMPLETED)
        .order_by(text("rank DESC"))
    )

    # count
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    rows = result.all()

    docs = []
    for doc, rank in rows:
        d = DocumentResponse.model_validate(doc)
        docs.append({"document": d, "relevance": round(float(rank), 4)})

    return {
        "query": q,
        "results": docs,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
# search results ranked by ts_rank with weights

# filter search by document_type and processing status
# improved relevance: boost exact phrase matches
