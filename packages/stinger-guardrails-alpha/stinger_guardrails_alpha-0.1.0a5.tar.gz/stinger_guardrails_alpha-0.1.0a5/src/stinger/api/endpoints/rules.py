"""
Rules endpoint for retrieving guardrail configurations.
"""

import hashlib
import json
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from stinger.api.models import RulesResponse
from stinger.core.pipeline import GuardrailPipeline

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/rules", response_model=RulesResponse)
async def get_rules(
    preset: str = Query("customer_service", description="Preset configuration to retrieve"),
    ext_version: Optional[str] = Query(None, description="Extension version for compatibility"),
):
    """
    Get the current guardrail rules configuration.

    This endpoint returns the active guardrail configuration that
    browser extensions can use to understand what rules are in effect.
    """
    try:
        # Try to create a pipeline with the preset to validate it exists
        try:
            pipeline = GuardrailPipeline.from_preset(preset)
        except Exception as e:
            logger.error(f"Invalid preset {preset}: {e}")
            raise HTTPException(status_code=404, detail=f"Preset '{preset}' not found")

        # Create a simplified rules structure for the extension
        rules = {"input_guardrails": {}, "output_guardrails": {}}

        # Extract enabled guardrails from pipeline
        for guardrail in pipeline.input_pipeline:
            if guardrail.enabled:
                name = guardrail.name
                rules["input_guardrails"][name] = {
                    "type": type(guardrail).__name__,
                    "enabled": True,
                    "config": {},
                }

        for guardrail in pipeline.output_pipeline:
            if guardrail.enabled:
                name = guardrail.name
                rules["output_guardrails"][name] = {
                    "type": type(guardrail).__name__,
                    "enabled": True,
                    "config": {},
                }

        # Generate a version hash
        config_str = json.dumps(rules, sort_keys=True)
        version_hash = hashlib.sha256(config_str.encode()).hexdigest()[:8]

        return RulesResponse(preset=preset, guardrails=rules, version=f"1.0.{version_hash}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving rules: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
