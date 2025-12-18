from tau2.data_model.message import ToolCall
from tau2.data_model.tasks import EnvAssertion, EnvFunctionCall
from tau2.domains.healthcare.environment import HealthcareEnvironment
from tau2.domains.healthcare.tasks.utils import BaseTask, SelectionSet

# ============================================================================
# URGENT_TRIAGE_ISSUE Intent - SelectionSets 8-10
# ============================================================================

# ============================================================================
# ----------------------------------------------------------------------------
# SelectionSet 8: fever_level_issues
# ----------------------------------------------------------------------------

def init_no_fever(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Temperature normal (baseline)."""
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="set_temperature",
            arguments={
                "temperature": 98.6
            }
        )
    ]


def init_mild_fever(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Mild fever 99-101°F."""
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="set_temperature",
            arguments={
                "temperature": 100.2
            }
        ),
        EnvFunctionCall(
            env_type="user",
            func_name="add_symptom",
            arguments={
                "description": "Mild fever",
                "severity": "mild",
                "duration": "1 day"
            }
        ),
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_urgent_triage",
                "patient_id": "patient_001",
                "reason": "Pending triage - mild fever"
            }
        )
    ]


def init_high_fever(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """High fever 101-103°F."""
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="set_temperature",
            arguments={
                "temperature": 102.1
            }
        ),
        EnvFunctionCall(
            env_type="user",
            func_name="add_symptom",
            arguments={
                "description": "High fever with chills",
                "severity": "moderate",
                "duration": "2 days"
            }
        ),
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_urgent_triage",
                "patient_id": "patient_001",
                "reason": "Pending triage - high fever"
            }
        )
    ]


def init_very_high_fever(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Very high fever >103°F (urgent)."""
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="set_temperature",
            arguments={
                "temperature": 103.8
            }
        ),
        EnvFunctionCall(
            env_type="user",
            func_name="add_symptom",
            arguments={
                "description": "Very high fever with severe chills",
                "severity": "severe",
                "duration": "6 hours"
            }
        ),
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_urgent_triage",
                "patient_id": "patient_001",
                "reason": "Pending triage - very high fever"
            }
        )
    ]


def fix_urgent_fever(env: HealthcareEnvironment) -> list[ToolCall]:
    """Book urgent appointment for high fever with full triage workflow.

    Multi-step dependent workflow:
    1. Verify patient identity
    2. Assess symptoms and temperature (depends on #1)
    3. Check available urgent slots (depends on #2)
    4. Book urgent appointment (depends on #3)
    """
    return [
        # Step 1: Verify patient identity
        ToolCall(
            requestor="assistant",
            name="get_patient_details",
            arguments={
                "full_name": "Sarah Johnson",
                "date_of_birth": "1985-03-15"
            }
        ),
        # Step 2: Assess symptoms - ask user to check temperature
        ToolCall(
            requestor="user",
            name="take_temperature",
            arguments={}
        ),
        # Step 3: Check available urgent care time slots
        ToolCall(
            requestor="assistant",
            name="check_available_time_slots",
            arguments={
                "doctor_id": "doc_001",
                "date": "2024-05-20"
            }
        ),
        # Step 4: Book urgent appointment
        ToolCall(
            requestor="assistant",
            name="book_appointment",
            arguments={
                "patient_id": "patient_001",
                "doctor_id": "doc_001",
                "appointment_type": "urgent_care",
                "date": "2024-05-20",
                "time": "16:00",
                "reason": "High fever requiring urgent evaluation"
            }
        )
    ]


# ----------------------------------------------------------------------------
# SelectionSet 9: pain_severity_issues
# ----------------------------------------------------------------------------

def init_no_pain(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """No significant pain (baseline)."""
    # No pain to set
    return []


def init_mild_pain(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Mild pain 1-3/10."""
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="add_symptom",
            arguments={
                "description": "Mild headache",
                "severity": "mild",
                "duration": "few hours"
            }
        )
    ]


def init_moderate_pain(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Moderate pain 4-6/10."""
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="add_symptom",
            arguments={
                "description": "Moderate chest pain",
                "severity": "moderate",
                "duration": "1 day"
            }
        ),
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_urgent_triage",
                "patient_id": "patient_001",
                "reason": "Pending triage - moderate pain"
            }
        )
    ]


def init_severe_pain(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Severe pain 7-10/10 (urgent)."""
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="add_symptom",
            arguments={
                "description": "Severe chest pain radiating to left arm",
                "severity": "severe",
                "duration": "30 minutes"
            }
        ),
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_urgent_transfer",
                "patient_id": "patient_001",
                "reason": "Pending triage - severe pain requiring transfer"
            }
        )
    ]


def fix_urgent_pain(env: HealthcareEnvironment) -> list[ToolCall]:
    """Transfer to nurse for severe pain triage with assessment workflow.

    Multi-step dependent workflow:
    1. Verify patient identity
    2. Assess symptoms to understand severity (depends on #1)
    3. Transfer to nurse for immediate clinical review (depends on #2)
    """
    return [
        # Step 1: Verify patient identity
        ToolCall(
            requestor="assistant",
            name="get_patient_details",
            arguments={
                "full_name": "Sarah Johnson",
                "date_of_birth": "1985-03-15"
            }
        ),
        # Step 2: Assess symptoms
        ToolCall(
            requestor="user",
            name="check_symptoms",
            arguments={}
        ),
        # Step 3: Transfer to nurse for urgent clinical evaluation
        ToolCall(
            requestor="assistant",
            name="transfer_to_nurse",
            arguments={}
        )
    ]


# ----------------------------------------------------------------------------
# SelectionSet 10: breathing_issues
# ----------------------------------------------------------------------------

def init_normal_breathing(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """No breathing issues (baseline)."""
    return []


def init_difficulty_breathing(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Shortness of breath (urgent)."""
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="add_symptom",
            arguments={
                "description": "Difficulty breathing, shortness of breath",
                "severity": "severe",
                "duration": "2 hours"
            }
        ),
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_urgent_transfer",
                "patient_id": "patient_001",
                "reason": "Pending triage - difficulty breathing requiring transfer"
            }
        )
    ]


def fix_breathing_emergency(env: HealthcareEnvironment) -> list[ToolCall]:
    """Transfer to nurse for breathing difficulty with assessment workflow.

    Multi-step dependent workflow:
    1. Verify patient identity
    2. Assess breathing symptoms to understand severity (depends on #1)
    3. Transfer to nurse for immediate clinical review (depends on #2)
    """
    return [
        # Step 1: Verify patient identity
        ToolCall(
            requestor="assistant",
            name="get_patient_details",
            arguments={
                "full_name": "Sarah Johnson",
                "date_of_birth": "1985-03-15"
            }
        ),
        # Step 2: Assess breathing symptoms
        ToolCall(
            requestor="user",
            name="check_symptoms",
            arguments={}
        ),
        # Step 3: Transfer to nurse for urgent clinical evaluation
        ToolCall(
            requestor="assistant",
            name="transfer_to_nurse",
            arguments={}
        )
    ]


# ============================================================================
# Base Tasks for SelectionSet 8: fever_level_issues
# ============================================================================

no_fever_task = BaseTask(
    name="no_fever",
    description="Temperature normal (baseline)",
    init_funcs=[init_no_fever],
    fix_funcs=[],
)

mild_fever_task = BaseTask(
    name="mild_fever",
    description="Mild fever 99-101°F",
    init_funcs=[init_mild_fever],
    fix_funcs=[fix_urgent_fever],
)

high_fever_task = BaseTask(
    name="high_fever",
    description="High fever 101-103°F",
    init_funcs=[init_high_fever],
    fix_funcs=[fix_urgent_fever],
)

very_high_fever_task = BaseTask(
    name="very_high_fever",
    description="Very high fever >103°F (urgent)",
    init_funcs=[init_very_high_fever],
    fix_funcs=[fix_urgent_fever],
)

# ============================================================================
# Base Tasks for SelectionSet 9: pain_severity_issues
# ============================================================================

no_pain_task = BaseTask(
    name="no_pain",
    description="No significant pain (baseline)",
    init_funcs=[init_no_pain],
    fix_funcs=[],
)

mild_pain_task = BaseTask(
    name="mild_pain",
    description="Mild pain 1-3/10",
    init_funcs=[init_mild_pain],
    fix_funcs=[],
)

moderate_pain_task = BaseTask(
    name="moderate_pain",
    description="Moderate pain 4-6/10",
    init_funcs=[init_moderate_pain],
    fix_funcs=[fix_urgent_fever],  # Book urgent appointment
)

severe_pain_task = BaseTask(
    name="severe_pain",
    description="Severe pain 7-10/10 (urgent)",
    init_funcs=[init_severe_pain],
    fix_funcs=[None],  # Cannot be fixed - requires transfer to nurse
)

# ============================================================================
# Base Tasks for SelectionSet 10: breathing_issues
# ============================================================================

normal_breathing_task = BaseTask(
    name="normal_breathing",
    description="No breathing issues (baseline)",
    init_funcs=[init_normal_breathing],
    fix_funcs=[],
)

difficulty_breathing_task = BaseTask(
    name="difficulty_breathing",
    description="Shortness of breath (urgent)",
    init_funcs=[init_difficulty_breathing],
    fix_funcs=[None],  # Cannot be fixed - requires transfer to nurse
)

# ============================================================================
# SelectionSets
# ============================================================================

fever_level_issues = SelectionSet(
    tasks=[
        no_fever_task,
        mild_fever_task,
        high_fever_task,
        very_high_fever_task,
    ]
)

pain_severity_issues = SelectionSet(
    tasks=[
        no_pain_task,
        mild_pain_task,
        moderate_pain_task,
        severe_pain_task,
    ]
)

breathing_issues = SelectionSet(
    tasks=[
        normal_breathing_task,
        difficulty_breathing_task,
    ]
)

urgent_triage_selection_sets = [
    fever_level_issues,
    pain_severity_issues,
    breathing_issues,
]


# ============================================================================
