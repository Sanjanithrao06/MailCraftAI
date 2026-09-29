import logging

from fastapi import APIRouter, HTTPException

from app.api.schemas import EvaluationRequest, EvaluationResponse
from app.evaluation.runner import run_evaluation

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate(request: EvaluationRequest) -> EvaluationResponse:
    """Run the full evaluation suite across specified strategies."""
    logger.info("Starting evaluation for strategies: %s", request.strategies)

    try:
        results, summary = await run_evaluation(request.strategies)
    except Exception as e:
        logger.exception("Evaluation failed")
        raise HTTPException(status_code=500, detail=str(e)) from e

    return EvaluationResponse(results=results, summary=summary)
