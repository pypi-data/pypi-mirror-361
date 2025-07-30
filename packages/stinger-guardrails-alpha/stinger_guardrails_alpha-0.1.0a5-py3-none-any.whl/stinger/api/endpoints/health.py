"""
Health check endpoint for API service.
"""

from fastapi import APIRouter

from stinger.core.api_key_manager import get_openai_key
from stinger.core.pipeline import GuardrailPipeline

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify API is running and dependencies are available.
    """
    try:
        # Check if we can create a basic pipeline
        pipeline = GuardrailPipeline.from_preset("customer_service")
        pipeline_status = True
        guardrail_count = len(pipeline.input_pipeline) + len(pipeline.output_pipeline)
    except Exception:
        pipeline_status = False
        guardrail_count = 0

    # Check API key availability
    api_key_available = bool(get_openai_key())

    return {
        "status": "healthy",
        "pipeline_available": pipeline_status,
        "guardrail_count": guardrail_count,
        "api_key_configured": api_key_available,
    }
