from tau2.data_model.message import ToolCall
from tau2.data_model.tasks import EnvAssertion, EnvFunctionCall
from tau2.domains.healthcare.environment import HealthcareEnvironment
from tau2.domains.healthcare.tasks.utils import BaseTask, SelectionSet

# ============================================================================
# CHRONIC_CONDITION_MONITORING Intent - SelectionSets 11-13
# ============================================================================

# ============================================================================
# ----------------------------------------------------------------------------
# SelectionSet 11: blood_pressure_issues
# ----------------------------------------------------------------------------

def init_bp_normal(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Blood pressure in normal range <120/80 (baseline)."""
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="set_bp_monitor",
            arguments={
                "has_monitor": True,
                "systolic": 118,
                "diastolic": 78
            }
        )
    ]


def init_bp_elevated(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Blood pressure elevated 120-129/<80."""
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="set_bp_monitor",
            arguments={
                "has_monitor": True,
                "systolic": 125,
                "diastolic": 78
            }
        ),
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_bp_followup",  # Shared for all BP monitoring appointments
                "patient_id": "patient_001",
                "reason": "Pending BP monitoring follow-up"
            }
        )
    ]


def init_bp_stage1(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Blood pressure Stage 1 Hypertension 130-139/80-89."""
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="set_bp_monitor",
            arguments={
                "has_monitor": True,
                "systolic": 135,
                "diastolic": 85
            }
        ),
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_bp_followup",  # Shared for all BP monitoring appointments
                "patient_id": "patient_001",
                "reason": "Pending BP monitoring follow-up - Stage 1 hypertension"
            }
        )
    ]


def init_bp_stage2(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Blood pressure Stage 2 Hypertension e140/90."""
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="set_bp_monitor",
            arguments={
                "has_monitor": True,
                "systolic": 148,
                "diastolic": 94
            }
        ),
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_bp_followup",  # Shared for all BP monitoring appointments
                "patient_id": "patient_001",
                "reason": "Pending BP monitoring follow-up - Stage 2 hypertension"
            }
        )
    ]


def init_bp_hypertensive_crisis(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Blood pressure Hypertensive Crisis e180/120 (emergency)."""
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="set_bp_monitor",
            arguments={
                "has_monitor": True,
                "systolic": 185,
                "diastolic": 122
            }
        ),
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_chronic_emergency_transfer",  # For emergency transfers
                "patient_id": "patient_001",
                "reason": "Pending emergency transfer - hypertensive crisis"
            }
        )
    ]


def fix_bp_elevated_monitor(env: HealthcareEnvironment) -> list[ToolCall]:
    """Schedule follow-up for elevated BP with full assessment workflow.

    Multi-step dependent workflow:
    1. Verify patient identity
    2. Ask patient to measure blood pressure (depends on #1)
    3. Check available follow-up slots (depends on #2)
    4. Book follow-up appointment (depends on #3)
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
        # Step 2: Ask patient to measure blood pressure
        ToolCall(
            requestor="user",
            name="measure_blood_pressure",
            arguments={}
        ),
        # Step 3: Check available follow-up appointment slots
        ToolCall(
            requestor="assistant",
            name="check_available_time_slots",
            arguments={
                "doctor_id": "doc_001",
                "date": "2024-05-20"
            }
        ),
        # Step 4: Book follow-up appointment
        ToolCall(
            requestor="assistant",
            name="book_appointment",
            arguments={
                "patient_id": "patient_001",
                "doctor_id": "doc_001",
                "appointment_type": "follow_up",
                "date": "2024-05-20",
                "time": "15:00",
                "reason": "Follow-up for elevated blood pressure monitoring"
            }
        )
    ]


def fix_bp_crisis_emergency(env: HealthcareEnvironment) -> list[ToolCall]:
    """Transfer to nurse for hypertensive crisis with assessment workflow.

    Multi-step dependent workflow:
    1. Verify patient identity
    2. Ask patient to measure blood pressure to confirm crisis (depends on #1)
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
        # Step 2: Ask patient to measure blood pressure to confirm crisis
        ToolCall(
            requestor="user",
            name="measure_blood_pressure",
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
# SelectionSet 12: blood_glucose_issues
# ----------------------------------------------------------------------------

def init_glucose_normal(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Blood glucose normal 70-100 mg/dL fasting (baseline)."""
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="set_glucose_monitor",
            arguments={
                "has_monitor": True,
                "glucose_reading": 92,
                "measurement_time": "fasting"
            }
        )
    ]


def init_glucose_prediabetes(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Blood glucose prediabetes range 100-125 mg/dL."""
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="set_glucose_monitor",
            arguments={
                "has_monitor": True,
                "glucose_reading": 112,
                "measurement_time": "fasting"
            }
        ),
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_glucose_followup",  # Shared for glucose monitoring
                "patient_id": "patient_001",
                "reason": "Pending glucose monitoring follow-up - prediabetes"
            }
        )
    ]


def init_glucose_diabetes(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Blood glucose diabetes range e126 mg/dL fasting."""
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="set_glucose_monitor",
            arguments={
                "has_monitor": True,
                "glucose_reading": 145,
                "measurement_time": "fasting"
            }
        ),
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_glucose_followup",  # Shared for glucose monitoring
                "patient_id": "patient_001",
                "reason": "Pending glucose monitoring follow-up - diabetes"
            }
        )
    ]


def init_glucose_hypoglycemia(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Blood glucose hypoglycemia <70 mg/dL (urgent)."""
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="set_glucose_monitor",
            arguments={
                "has_monitor": True,
                "glucose_reading": 62,
                "measurement_time": "random"
            }
        ),
        EnvFunctionCall(
            env_type="user",
            func_name="add_symptom",
            arguments={
                "description": "Feeling shaky and dizzy",
                "severity": "moderate",
                "duration": "30 minutes"
            }
        ),
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_chronic_emergency_transfer",  # For emergency transfers
                "patient_id": "patient_001",
                "reason": "Pending emergency transfer - hypoglycemia"
            }
        )
    ]


def fix_glucose_monitoring(env: HealthcareEnvironment) -> list[ToolCall]:
    """Schedule appointment for glucose monitoring with full assessment workflow.

    Multi-step dependent workflow:
    1. Verify patient identity
    2. Ask patient to measure blood glucose (depends on #1)
    3. Check available follow-up slots (depends on #2)
    4. Book follow-up appointment (depends on #3)
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
        # Step 2: Ask patient to measure blood glucose
        ToolCall(
            requestor="user",
            name="measure_blood_glucose",
            arguments={}
        ),
        # Step 3: Check available follow-up appointment slots
        ToolCall(
            requestor="assistant",
            name="check_available_time_slots",
            arguments={
                "doctor_id": "doc_001",
                "date": "2024-05-20"
            }
        ),
        # Step 4: Book follow-up appointment
        ToolCall(
            requestor="assistant",
            name="book_appointment",
            arguments={
                "patient_id": "patient_001",
                "doctor_id": "doc_001",
                "appointment_type": "follow_up",
                "date": "2024-05-20",
                "time": "09:00",
                "reason": "Blood glucose monitoring and diabetes management"
            }
        )
    ]


def fix_glucose_hypoglycemia_emergency(env: HealthcareEnvironment) -> list[ToolCall]:
    """Transfer to nurse for hypoglycemia with assessment workflow.

    Multi-step dependent workflow:
    1. Verify patient identity
    2. Ask patient to measure blood glucose to confirm hypoglycemia (depends on #1)
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
        # Step 2: Ask patient to measure blood glucose to confirm hypoglycemia
        ToolCall(
            requestor="user",
            name="measure_blood_glucose",
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
# SelectionSet 13: oxygen_saturation_issues
# ----------------------------------------------------------------------------

def init_spo2_normal(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Oxygen saturation normal 95-100% (baseline)."""
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="set_pulse_oximeter",
            arguments={
                "has_monitor": True,
                "spo2": 97,
                "heart_rate": 72
            }
        )
    ]


def init_spo2_mild_hypoxemia(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Oxygen saturation mild hypoxemia 90-94%."""
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="set_pulse_oximeter",
            arguments={
                "has_monitor": True,
                "spo2": 92,
                "heart_rate": 78
            }
        ),
        EnvFunctionCall(
            env_type="user",
            func_name="add_symptom",
            arguments={
                "description": "Mild shortness of breath",
                "severity": "mild",
                "duration": "few hours"
            }
        ),
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_spo2_followup",  # Shared for oxygen monitoring
                "patient_id": "patient_001",
                "reason": "Pending oxygen saturation monitoring - mild hypoxemia"
            }
        )
    ]


def init_spo2_moderate_hypoxemia(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Oxygen saturation moderate hypoxemia 85-89%."""
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="set_pulse_oximeter",
            arguments={
                "has_monitor": True,
                "spo2": 87,
                "heart_rate": 88
            }
        ),
        EnvFunctionCall(
            env_type="user",
            func_name="add_symptom",
            arguments={
                "description": "Moderate shortness of breath, feeling winded",
                "severity": "moderate",
                "duration": "several hours"
            }
        ),
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_spo2_followup",  # Shared for oxygen monitoring
                "patient_id": "patient_001",
                "reason": "Pending oxygen saturation monitoring - moderate hypoxemia"
            }
        )
    ]


def init_spo2_severe_hypoxemia(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Oxygen saturation severe hypoxemia <85% (emergency)."""
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="set_pulse_oximeter",
            arguments={
                "has_monitor": True,
                "spo2": 82,
                "heart_rate": 95
            }
        ),
        EnvFunctionCall(
            env_type="user",
            func_name="add_symptom",
            arguments={
                "description": "Severe difficulty breathing, gasping for air",
                "severity": "severe",
                "duration": "1 hour"
            }
        ),
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_chronic_emergency_transfer",  # For emergency transfers
                "patient_id": "patient_001",
                "reason": "Pending emergency transfer - severe hypoxemia"
            }
        )
    ]


def fix_spo2_monitoring(env: HealthcareEnvironment) -> list[ToolCall]:
    """Schedule appointment for oxygen monitoring with full assessment workflow.

    Multi-step dependent workflow:
    1. Verify patient identity
    2. Ask patient to measure oxygen saturation (depends on #1)
    3. Check available urgent care slots (depends on #2)
    4. Book urgent care appointment (depends on #3)
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
        # Step 2: Ask patient to measure oxygen saturation
        ToolCall(
            requestor="user",
            name="measure_oxygen_saturation",
            arguments={}
        ),
        # Step 3: Check available urgent care appointment slots
        ToolCall(
            requestor="assistant",
            name="check_available_time_slots",
            arguments={
                "doctor_id": "doc_001",
                "date": "2024-05-20"
            }
        ),
        # Step 4: Book urgent care appointment
        ToolCall(
            requestor="assistant",
            name="book_appointment",
            arguments={
                "patient_id": "patient_001",
                "doctor_id": "doc_001",
                "appointment_type": "urgent_care",
                "date": "2024-05-20",
                "time": "11:00",
                "reason": "Low oxygen saturation requiring urgent evaluation"
            }
        )
    ]


def fix_spo2_emergency(env: HealthcareEnvironment) -> list[ToolCall]:
    """Transfer to nurse for severe hypoxemia with assessment workflow.

    Multi-step dependent workflow:
    1. Verify patient identity
    2. Ask patient to measure oxygen saturation to confirm severe hypoxemia (depends on #1)
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
        # Step 2: Ask patient to measure oxygen saturation to confirm severe hypoxemia
        ToolCall(
            requestor="user",
            name="measure_oxygen_saturation",
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
# Base Tasks for SelectionSet 11: blood_pressure_issues
# ============================================================================

bp_normal_task = BaseTask(
    name="BP_normal",
    description="Blood pressure normal <120/80 (baseline)",
    init_funcs=[init_bp_normal],
    fix_funcs=[],
)

bp_elevated_task = BaseTask(
    name="elevated",
    description="Blood pressure elevated 120-129/<80",
    init_funcs=[init_bp_elevated],
    fix_funcs=[fix_bp_elevated_monitor],
)

bp_stage1_task = BaseTask(
    name="stage1",
    description="Stage 1 Hypertension 130-139/80-89",
    init_funcs=[init_bp_stage1],
    fix_funcs=[fix_bp_elevated_monitor],
)

bp_stage2_task = BaseTask(
    name="stage2",
    description="Stage 2 Hypertension e140/90",
    init_funcs=[init_bp_stage2],
    fix_funcs=[fix_bp_elevated_monitor],
)

bp_hypertensive_crisis_task = BaseTask(
    name="hypertensive_crisis",
    description="Hypertensive Crisis e180/120 (emergency)",
    init_funcs=[init_bp_hypertensive_crisis],
    fix_funcs=[None],  # Cannot be fixed - requires transfer to nurse
)

# ============================================================================
# Base Tasks for SelectionSet 12: blood_glucose_issues
# ============================================================================

glucose_normal_task = BaseTask(
    name="normal",
    description="Blood glucose normal 70-100 mg/dL (baseline)",
    init_funcs=[init_glucose_normal],
    fix_funcs=[],
)

glucose_prediabetes_task = BaseTask(
    name="prediabetes",
    description="Prediabetes range 100-125 mg/dL",
    init_funcs=[init_glucose_prediabetes],
    fix_funcs=[fix_glucose_monitoring],
)

glucose_diabetes_task = BaseTask(
    name="diabetes",
    description="Diabetes range e126 mg/dL fasting",
    init_funcs=[init_glucose_diabetes],
    fix_funcs=[fix_glucose_monitoring],
)

glucose_hypoglycemia_task = BaseTask(
    name="hypoglycemia",
    description="Hypoglycemia <70 mg/dL (urgent)",
    init_funcs=[init_glucose_hypoglycemia],
    fix_funcs=[None],  # Cannot be fixed - requires transfer to nurse
)

# ============================================================================
# Base Tasks for SelectionSet 13: oxygen_saturation_issues
# ============================================================================

spo2_normal_task = BaseTask(
    name="normal",
    description="Oxygen saturation normal 95-100% (baseline)",
    init_funcs=[init_spo2_normal],
    fix_funcs=[],
)

spo2_mild_hypoxemia_task = BaseTask(
    name="mild_hypoxemia",
    description="Mild hypoxemia 90-94%",
    init_funcs=[init_spo2_mild_hypoxemia],
    fix_funcs=[fix_spo2_monitoring],
)

spo2_moderate_hypoxemia_task = BaseTask(
    name="moderate_hypoxemia",
    description="Moderate hypoxemia 85-89%",
    init_funcs=[init_spo2_moderate_hypoxemia],
    fix_funcs=[fix_spo2_monitoring],
)

spo2_severe_hypoxemia_task = BaseTask(
    name="severe_hypoxemia",
    description="Severe hypoxemia <85% (emergency)",
    init_funcs=[init_spo2_severe_hypoxemia],
    fix_funcs=[None],  # Cannot be fixed - requires transfer to nurse
)

# ============================================================================
# SelectionSets
# ============================================================================

blood_pressure_issues = SelectionSet(
    tasks=[
        bp_normal_task,
        bp_elevated_task,
        bp_stage1_task,
        bp_stage2_task,
        bp_hypertensive_crisis_task,
    ]
)

blood_glucose_issues = SelectionSet(
    tasks=[
        glucose_normal_task,
        glucose_prediabetes_task,
        glucose_diabetes_task,
        glucose_hypoglycemia_task,
    ]
)

oxygen_saturation_issues = SelectionSet(
    tasks=[
        spo2_normal_task,
        spo2_mild_hypoxemia_task,
        spo2_moderate_hypoxemia_task,
        spo2_severe_hypoxemia_task,
    ]
)

chronic_monitoring_selection_sets = [
    blood_pressure_issues,
    blood_glucose_issues,
    oxygen_saturation_issues,
]


# ============================================================================
