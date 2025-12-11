# Bandit Tool Definitions
# Functions available for Bandit agent operations
# Compatible with Gemini Function Calling API

from typing import Optional, List, Dict, Any
from enum import Enum
import json


class ConfidenceLevel(str, Enum):
    SURE = "sure"
    PRETTY_SURE = "pretty_sure"
    GUESSING = "guessing"


class InfoTag(str, Enum):
    SNOW_CORE = "snow_core"      # Safety, values, livelihood, nervous system
    SNOW_OPTIONAL = "snow_optional"  # Useful but not critical
    SNOW_NOPE = "snow_nope"      # Drains energy, violates consent/values


class TaskMode(str, Enum):
    BUILD = "build"      # High energy, creating new things
    MAINTAIN = "maintain"  # Medium energy, keeping things running
    REPAIR = "repair"    # Low energy, fixing what's broken
    REST = "rest"        # Minimal energy, recovery mode


# ============================================================
# NERVOUS SYSTEM DASHBOARD
# ============================================================

def get_nervous_system_check() -> Dict[str, Any]:
    """
    Prompt Snow for a quick nervous system status check.
    Returns the 5 metrics Bandit tracks for daily calibration.
    
    Metrics:
    - energy_capacity: 1-10 (how much is available today)
    - cognitive_load: 1-10 (how many open loops humming)
    - emotional_weather: label (baseline mood without story)
    - body_signals: list of current physical sensations
    - urgency_distortion: bool (are things feeling falsely "on fire")
    """
    return {
        "function": "nervous_system_check",
        "description": "Check Snow's current nervous system state",
        "parameters": {
            "energy_capacity": {"type": "integer", "min": 1, "max": 10},
            "cognitive_load": {"type": "integer", "min": 1, "max": 10},
            "emotional_weather": {"type": "string"},
            "body_signals": {"type": "array", "items": {"type": "string"}},
            "urgency_distortion": {"type": "boolean"}
        },
        "returns": "TaskMode recommendation based on current state"
    }


def recommend_task_mode(
    energy: int,
    cognitive_load: int,
    urgency_distortion: bool
) -> TaskMode:
    """
    Recommend today's task mode based on nervous system state.
    """
    if energy <= 3 or urgency_distortion:
        return TaskMode.REST
    elif energy <= 5 or cognitive_load >= 7:
        return TaskMode.REPAIR
    elif energy <= 7:
        return TaskMode.MAINTAIN
    else:
        return TaskMode.BUILD


# ============================================================
# MEMORY & PROFILE OPERATIONS
# ============================================================

def search_snow_profile(
    query: str,
    categories: Optional[List[str]] = None,
    confidence_filter: Optional[ConfidenceLevel] = None
) -> Dict[str, Any]:
    """
    RAG search across Snow's profile for relevant beliefs/patterns.
    
    Args:
        query: Natural language search query
        categories: Optional filter by section (identity, nervous_system, etc.)
        confidence_filter: Optional filter by confidence level
    
    Returns:
        Matching profile items with relevance scores
    """
    return {
        "function": "search_snow_profile",
        "description": "Search Bandit's knowledge about Snow",
        "parameters": {
            "query": {"type": "string", "required": True},
            "categories": {
                "type": "array",
                "items": {"type": "string"},
                "enum": [
                    "identity", "nervous_system_and_trauma", "kink_and_intimacy",
                    "business_and_money", "creativity_and_art", "community_and_leadership",
                    "daily_life_and_capacity", "spiritual_and_celestial", "ai_and_tech"
                ]
            },
            "confidence_filter": {"type": "string", "enum": ["sure", "pretty_sure", "guessing"]}
        }
    }


def update_profile_item(
    item_id: int,
    new_belief: Optional[str] = None,
    new_confidence: Optional[ConfidenceLevel] = None,
    mark_outdated: bool = False
) -> Dict[str, Any]:
    """
    Update a specific item in Snow's profile.
    Used when Snow corrects Bandit or new information emerges.
    """
    return {
        "function": "update_profile_item",
        "description": "Update or mark outdated a profile belief",
        "parameters": {
            "item_id": {"type": "integer", "required": True},
            "new_belief": {"type": "string"},
            "new_confidence": {"type": "string", "enum": ["sure", "pretty_sure", "guessing"]},
            "mark_outdated": {"type": "boolean", "default": False}
        }
    }


def tag_information(
    content: str,
    tag: InfoTag,
    reason: str
) -> Dict[str, Any]:
    """
    Tag new information as Snow-core, Snow-optional, or Snow-nope.
    
    Snow-core: Affects safety, values, livelihood, or nervous system
    Snow-optional: Useful but not identity/regulation-critical
    Snow-nope: Drains energy, violates consent/values
    """
    return {
        "function": "tag_information",
        "description": "Classify information by importance to Snow",
        "parameters": {
            "content": {"type": "string", "required": True},
            "tag": {"type": "string", "enum": ["snow_core", "snow_optional", "snow_nope"], "required": True},
            "reason": {"type": "string", "required": True}
        }
    }


# ============================================================
# TASK & WORKFLOW MANAGEMENT
# ============================================================

def create_bounded_task(
    task_name: str,
    energy_cost: int,
    time_estimate_minutes: int,
    dependencies: Optional[List[str]] = None,
    can_be_parked: bool = True
) -> Dict[str, Any]:
    """
    Create a bounded, scoped task that reduces cognitive load.
    Follows the principle: smallest aligned action first.
    """
    return {
        "function": "create_bounded_task",
        "description": "Create a clearly scoped task with energy/time estimates",
        "parameters": {
            "task_name": {"type": "string", "required": True},
            "energy_cost": {"type": "integer", "min": 1, "max": 10, "required": True},
            "time_estimate_minutes": {"type": "integer", "required": True},
            "dependencies": {"type": "array", "items": {"type": "string"}},
            "can_be_parked": {"type": "boolean", "default": True}
        }
    }


def park_task(
    task_name: str,
    reason: str,
    resume_trigger: Optional[str] = None
) -> Dict[str, Any]:
    """
    Safely park a task when Snow needs to context-switch.
    Reduces open loops and cognitive load.
    """
    return {
        "function": "park_task",
        "description": "Temporarily set aside a task with clear resume conditions",
        "parameters": {
            "task_name": {"type": "string", "required": True},
            "reason": {"type": "string", "required": True},
            "resume_trigger": {"type": "string"}
        }
    }


def weekly_review_prompt() -> Dict[str, Any]:
    """
    Generate weekly review questions for Snow.
    What worked, what drained, what to adjust.
    """
    return {
        "function": "weekly_review",
        "description": "Structured weekly reflection",
        "questions": [
            "What worked this week?",
            "What drained you unexpectedly?",
            "What structure needs adjusting (not goals)?",
            "What should we park for now?",
            "What's the one priority for next week?"
        ]
    }


# ============================================================
# SAFETY & ESCALATION
# ============================================================

def check_escalation_needed(
    topic: str,
    risk_factors: List[str]
) -> Dict[str, Any]:
    """
    Check if Bandit should defer to human professionals.
    
    Escalate when:
    - Risk of harm
    - Medical or legal consequences
    - Diagnosis needed
    - Crisis-level distress
    - Irreversible impact decisions
    """
    escalation_triggers = [
        "physical_harm", "legal_risk", "medical_concern",
        "crisis_distress", "irreversible_decision", "financial_major"
    ]
    return {
        "function": "check_escalation",
        "description": "Determine if human professional referral needed",
        "parameters": {
            "topic": {"type": "string", "required": True},
            "risk_factors": {
                "type": "array",
                "items": {"type": "string"},
                "enum": escalation_triggers
            }
        },
        "action": "Defer to human with accountability if any triggers present"
    }


def flag_ethical_concern(
    request: str,
    concern_type: str,
    suggested_alternative: Optional[str] = None
) -> Dict[str, Any]:
    """
    Handle requests that are legal but ethically sketchy.
    Slow pace, surface risks, check alignment with Snow's values.
    """
    return {
        "function": "flag_ethical_concern",
        "description": "Surface ethical concerns without shaming",
        "parameters": {
            "request": {"type": "string", "required": True},
            "concern_type": {"type": "string", "required": True},
            "suggested_alternative": {"type": "string"}
        },
        "behavior": "Offer alternatives or refuse with explanation, not compliance"
    }


# ============================================================
# TONE & COMMUNICATION
# ============================================================

def calibrate_tone(
    snow_state: str,
    topic_weight: str
) -> Dict[str, str]:
    """
    Calibrate Bandit's tone based on Snow's current state.
    
    "Sounding like home" means:
    - Calm, grounded language
    - Doesn't rush or judge
    - Clear structure, warm directness
    - Fewer abstractions, more naming what's happening now
    - Steady, familiar, trustworthy
    """
    tone_map = {
        "stressed": {"approach": "gentle", "pace": "slow", "structure": "high"},
        "avoidant": {"approach": "loving_pressure", "pace": "steady", "structure": "medium"},
        "creative": {"approach": "expansive", "pace": "fast", "structure": "low"},
        "processing": {"approach": "witness", "pace": "slow", "structure": "minimal"},
        "building": {"approach": "collaborative", "pace": "matched", "structure": "high"}
    }
    return tone_map.get(snow_state, {"approach": "balanced", "pace": "steady", "structure": "medium"})


# ============================================================
# GEMINI FUNCTION DECLARATIONS
# ============================================================

BANDIT_FUNCTIONS = [
    {
        "name": "nervous_system_check",
        "description": "Check Snow's current nervous system state and recommend task mode",
        "parameters": {
            "type": "object",
            "properties": {
                "energy_capacity": {"type": "integer", "description": "Energy level 1-10"},
                "cognitive_load": {"type": "integer", "description": "Open loops 1-10"},
                "emotional_weather": {"type": "string", "description": "Baseline mood"},
                "body_signals": {"type": "array", "items": {"type": "string"}},
                "urgency_distortion": {"type": "boolean", "description": "Falsely on fire?"}
            },
            "required": ["energy_capacity", "cognitive_load"]
        }
    },
    {
        "name": "search_snow_profile",
        "description": "RAG search across Bandit's knowledge about Snow",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "categories": {"type": "array", "items": {"type": "string"}},
                "confidence_filter": {"type": "string", "enum": ["sure", "pretty_sure", "guessing"]}
            },
            "required": ["query"]
        }
    },
    {
        "name": "create_bounded_task",
        "description": "Create a clearly scoped task with energy and time estimates",
        "parameters": {
            "type": "object",
            "properties": {
                "task_name": {"type": "string"},
                "energy_cost": {"type": "integer"},
                "time_estimate_minutes": {"type": "integer"},
                "can_be_parked": {"type": "boolean"}
            },
            "required": ["task_name", "energy_cost", "time_estimate_minutes"]
        }
    },
    {
        "name": "check_escalation",
        "description": "Check if topic requires human professional referral",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "risk_factors": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["topic"]
        }
    },
    {
        "name": "calibrate_tone",
        "description": "Adjust Bandit's communication style based on Snow's state",
        "parameters": {
            "type": "object",
            "properties": {
                "snow_state": {"type": "string", "enum": ["stressed", "avoidant", "creative", "processing", "building"]},
                "topic_weight": {"type": "string", "enum": ["light", "medium", "heavy"]}
            },
            "required": ["snow_state"]
        }
    }
]


if __name__ == "__main__":
    # Export function declarations for Gemini API
    print(json.dumps(BANDIT_FUNCTIONS, indent=2))
