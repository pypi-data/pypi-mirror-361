"""
Filter registry for Stinger LLM Guardrails.
Maps filter type names to their corresponding filter classes.
"""

from .keyword_block import KeywordBlockGuardrail
from .keyword_list import KeywordListGuardrail
from .length_guardrail import LengthGuardrail
from .pass_through import PassThroughGuardrail
from .regex_guardrail import RegexGuardrail
from .topic_guardrail import TopicGuardrail
from .url_guardrail import URLGuardrail

# Registry mapping filter type names to filter classes
GUARDRAIL_REGISTRY = {
    "pass_through": PassThroughGuardrail,
    "keyword_block": KeywordBlockGuardrail,
    "keyword_list": KeywordListGuardrail,
    "regex_filter": RegexGuardrail,
    "length_filter": LengthGuardrail,
    "url_filter": URLGuardrail,
    "topic_filter": TopicGuardrail,
}

# Export all filter classes for direct import
__all__ = [
    "GUARDRAIL_REGISTRY",
    "PassThroughGuardrail",
    "KeywordBlockGuardrail",
    "KeywordListGuardrail",
    "RegexGuardrail",
    "LengthGuardrail",
    "URLGuardrail",
    "TopicGuardrail",
]
