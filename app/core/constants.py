"""
Application constants
"""

# Scientific domains
SCIENTIFIC_DOMAINS = {
    "foundation_models": "Foundation Models & LLM Reasoning",
    "biology": "Biology & Life Sciences",
    "chemistry": "Chemistry & Materials",
    "physics": "Physics & Engineering",
    "medicine": "Medicine & Clinical Research",
    "environmental": "Environmental Science",
    "other": "Other"
}

# Analysis types
ANALYSIS_TYPES = {
    "comprehensive": "Full multi-document analysis",
    "comparative": "Focus on document comparison",
    "gap_detection": "Research gap identification",
    "protocol_design": "Experimental protocol generation",
    "hypothesis_validation": "Hypothesis stress testing"
}

# Study types
STUDY_TYPES = [
    "randomized_controlled_trial",
    "observational_cohort",
    "case_control",
    "cross_sectional",
    "meta_analysis",
    "systematic_review",
    "computational",
    "other"
]

# Risk levels
RISK_LEVELS = ["low", "medium", "high", "critical"]

# Status constants
STATUS_PENDING = "pending"
STATUS_PROCESSING = "processing"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
STATUS_CANCELLED = "cancelled"
