"""
Check endpoint for evaluating content against guardrails.
"""

import logging

from fastapi import APIRouter, HTTPException

from stinger.api.models import CheckRequest, CheckResponse
from stinger.core.conversation import Conversation
from stinger.core.pipeline import GuardrailPipeline

logger = logging.getLogger(__name__)
router = APIRouter()

# Cache for pipelines to avoid recreation
_pipeline_cache = {}


def get_pipeline(preset: str) -> GuardrailPipeline:
    """Get or create a pipeline for the given preset."""
    if preset not in _pipeline_cache:
        try:
            _pipeline_cache[preset] = GuardrailPipeline.from_preset(preset)
        except Exception as e:
            logger.error(f"Failed to create pipeline for preset {preset}: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid preset: {preset}")
    return _pipeline_cache[preset]


@router.post("/check", response_model=CheckResponse)
async def check_content(request: CheckRequest):
    """
    Check content against guardrails.

    This endpoint evaluates user prompts or LLM responses against
    the configured guardrails and returns an action decision.
    """
    try:
        # Get pipeline for the requested preset
        pipeline = get_pipeline(request.preset)

        # Create a simple conversation context if needed
        conversation = None
        if request.context and request.context.get("sessionId"):
            conversation = Conversation.human_ai(
                user_id=request.context.get("userId", "user"),
                model_id="gpt-4",  # Default, not used for checking
            )

        # Check the content based on type
        if request.kind == "prompt":
            result = await pipeline.check_input_async(request.text, conversation=conversation)
        else:  # response
            result = await pipeline.check_output_async(request.text, conversation=conversation)

        # Convert to response format
        action = "block" if result["blocked"] else "allow"
        if result.get("warnings") and not result["blocked"]:
            action = "warn"

        return CheckResponse(
            action=action,
            reasons=result.get("reasons", []),
            warnings=result.get("warnings", []),
            metadata={
                "guardrails_triggered": result.get("guardrails_triggered", []),
                "processing_time_ms": result.get("processing_time_ms", 0),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking content: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
