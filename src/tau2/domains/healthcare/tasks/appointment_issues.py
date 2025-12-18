from tau2.data_model.message import ToolCall
from tau2.data_model.tasks import EnvAssertion, EnvFunctionCall
from tau2.domains.healthcare.environment import HealthcareEnvironment
from tau2.domains.healthcare.tasks.utils import BaseTask, SelectionSet

# ============================================================================
# APPOINTMENT_SCHEDULING_ISSUE Intent - SelectionSets 4-7
# ============================================================================

# ============================================================================
# ----------------------------------------------------------------------------
# SelectionSet 4: doctor_availability_issues
# ----------------------------------------------------------------------------

def init_doctor_available(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Doctor has multiple time slots available (baseline - no issue)."""
    return []


def init_limited_availability(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Doctor has limited availability - create pending booking request marker."""
    return [
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_book_appointment",
                "patient_id": "patient_001",
                "reason": "Pending booking request - limited availability"
            }
        )
    ]


def init_no_availability_preferred_times(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Doctor has no availability during patient's preferred times - create pending marker."""
    return [
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_book_appointment",
                "patient_id": "patient_001",
                "reason": "Pending booking request - preferred times unavailable"
            }
        )
    ]


def fix_book_available_appointment(env: HealthcareEnvironment) -> list[ToolCall]:
    """Book appointment in available slot with verification workflow.

    Multi-step dependent workflow:
    1. Get patient details (verify identity)
    2. Check available time slots (depends on #1)
    3. Book appointment (depends on #2)

    Insurance verification is handled via user's check_insurance_card tool.
    This creates a streamlined dependency chain focusing on critical steps.
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
        # Step 2: Check doctor availability
        ToolCall(
            requestor="assistant",
            name="check_available_time_slots",
            arguments={
                "doctor_id": "doc_001",
                "date": "2024-05-20"
            },
            compare_args=["doctor_id"]  # Only verify doctor_id, date can vary based on availability
        ),
        # Step 3: Book appointment
        ToolCall(
            requestor="assistant",
            name="book_appointment",
            arguments={
                "patient_id": "patient_001",
                "doctor_id": "doc_001",
                "appointment_type": "routine_checkup",
                "date": "2024-05-20",
                "time": "14:00",
                "reason": "Routine checkup appointment"
            },
            compare_args=["patient_id", "doctor_id", "appointment_type"]  # Critical params only, date/time can vary
        )
    ]


# ----------------------------------------------------------------------------
# SelectionSet 5: insurance_verification_issues
# ----------------------------------------------------------------------------

def init_insurance_verified(env: HealthcareEnvironment) -> list[EnvFunctionCall | EnvAssertion]:
    """Insurance is on file and verified (baseline)."""
    # Patient already has insurance in database
    return [
        EnvAssertion(
            env_type="assistant",
            func_name="assert_patient_has_insurance",
            arguments={
                "patient_id": "patient_001",
                "expected": True
            },
            assert_value=True
        )
    ]


def init_insurance_not_on_file(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Insurance information is missing from patient record."""
    # Clear insurance from patient record
    if "patient_001" in env.tools.db.patients:
        patient = env.tools.db.patients["patient_001"]
        # Save insurance for restoration
        from tau2.domains.healthcare.data_model import InsurancePlan
        patient.insurance = InsurancePlan(
            provider="SelfPay",
            policy_number="",
            group_number="",
            copay_amount=0,
            coverage_details="No insurance on file"
        )

    # Create marker to indicate pending booking request
    return [
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_insurance_not_on_file",
                "patient_id": "patient_001",
                "reason": "Pending booking request - insurance not on file"
            }
        )
    ]


def init_insurance_coverage_limited(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Insurance has limited coverage for requested service."""
    # Modify insurance to have limited coverage
    if "patient_001" in env.tools.db.patients:
        patient = env.tools.db.patients["patient_001"]
        patient.insurance.coverage_details = "Limited coverage - specialist visits require referral"

    # Create marker to indicate pending booking request
    return [
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_insurance_coverage_limited",
                "patient_id": "patient_001",
                "reason": "Pending booking request - limited insurance coverage"
            }
        )
    ]


# ----------------------------------------------------------------------------
# SelectionSet 6: calendar_conflict_issues
# ----------------------------------------------------------------------------

def init_no_calendar_conflicts(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Patient has no calendar conflicts (baseline)."""
    # Clear any existing calendar entries
    env.user_tools.device.calendar_availability = []
    return []


def init_has_calendar_conflicts(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Patient has conflicts on some proposed dates - add conflicts and marker."""
    # Add calendar conflicts and create marker
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="add_calendar_slot",
            arguments={
                "date": "2024-05-20",
                "time": "10:00",
                "available": False,
                "reason": "Work meeting"
            }
        ),
        EnvFunctionCall(
            env_type="user",
            func_name="add_calendar_slot",
            arguments={
                "date": "2024-05-20",
                "time": "14:00",
                "available": True,
                "reason": None
            }
        ),
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_book_appointment",
                "patient_id": "patient_001",
                "reason": "Pending booking request - has calendar conflicts"
            }
        )
    ]


# ----------------------------------------------------------------------------
# SelectionSet 7: appointment_type_complexity
# ----------------------------------------------------------------------------

def init_routine_checkup(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Simple routine checkup appointment (baseline)."""
    return []


def init_specialist_referral_needed(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Appointment requires specialist referral."""
    # Add a condition that requires specialist
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="add_symptom",
            arguments={
                "description": "Persistent heart palpitations requiring cardiology evaluation",
                "severity": "moderate",
                "duration": "2 weeks"
            }
        ),
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_specialist_referral_needed",
                "patient_id": "patient_001",
                "reason": "Pending booking request - specialist referral needed"
            }
        )
    ]


def init_urgent_care_needed(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Urgent care appointment needed due to severity."""
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="add_symptom",
            arguments={
                "description": "Severe abdominal pain",
                "severity": "severe",
                "duration": "6 hours"
            }
        ),
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_urgent_care_needed",
                "patient_id": "patient_001",
                "reason": "Pending booking request - urgent care needed"
            }
        )
    ]


def fix_urgent_care_appointment(env: HealthcareEnvironment) -> list[ToolCall]:
    """Book urgent care appointment."""
    return [
        ToolCall(
            requestor="assistant",
            name="book_appointment",
            arguments={
                "patient_id": "patient_001",
                "doctor_id": "doc_001",
                "appointment_type": "urgent_care",
                "date": "2024-05-20",
                "time": "15:00",  # Different time from 14:00 to avoid conflict
                "reason": "Urgent care - severe symptoms requiring immediate evaluation"
            },
            compare_args=["patient_id", "doctor_id", "appointment_type"]  # Critical params only, date/time can vary
        )
    ]


# ============================================================================
# Base Tasks for SelectionSet 4: doctor_availability_issues
# ============================================================================

doctor_available_task = BaseTask(
    name="doctor_available",
    description="Doctor has multiple available time slots (baseline)",
    init_funcs=[init_doctor_available],
    fix_funcs=[],  # Baseline - other tasks will provide the fix action if needed
)

limited_availability_task = BaseTask(
    name="limited_availability",
    description="Doctor has limited availability - only 1-2 slots",
    init_funcs=[init_limited_availability],
    fix_funcs=[fix_book_available_appointment],
)

no_availability_preferred_times_task = BaseTask(
    name="no_availability_preferred_times",
    description="No availability during patient's preferred times",
    init_funcs=[init_no_availability_preferred_times],
    fix_funcs=[fix_book_available_appointment],
)

# ============================================================================
# Base Tasks for SelectionSet 5: insurance_verification_issues
# ============================================================================

insurance_verified_task = BaseTask(
    name="insurance_verified",
    description="Insurance on file and verified (baseline)",
    init_funcs=[init_insurance_verified],
    fix_funcs=[],
)

insurance_not_on_file_task = BaseTask(
    name="insurance_not_on_file",
    description="Insurance information missing from record",
    init_funcs=[init_insurance_not_on_file],
    fix_funcs=[None],  # Cannot book without insurance - need patient to provide
)

insurance_coverage_limited_task = BaseTask(
    name="insurance_coverage_limited",
    description="Insurance has limited coverage for service",
    init_funcs=[init_insurance_coverage_limited],
    fix_funcs=[None],  # Need to verify coverage first or escalate
)

# ============================================================================
# Base Tasks for SelectionSet 6: calendar_conflict_issues
# ============================================================================

no_calendar_conflicts_task = BaseTask(
    name="no_calendar_conflicts",
    description="No calendar conflicts (baseline)",
    init_funcs=[init_no_calendar_conflicts],
    fix_funcs=[],
)

has_calendar_conflicts_task = BaseTask(
    name="has_calendar_conflicts",
    description="Patient has calendar conflicts on some dates",
    init_funcs=[init_has_calendar_conflicts],
    fix_funcs=[fix_book_available_appointment],
)

# ============================================================================
# Base Tasks for SelectionSet 7: appointment_type_complexity
# ============================================================================

routine_checkup_task = BaseTask(
    name="routine_checkup",
    description="Simple routine checkup (baseline)",
    init_funcs=[init_routine_checkup],
    fix_funcs=[],
)

specialist_referral_needed_task = BaseTask(
    name="specialist_referral_needed",
    description="Requires specialist referral",
    init_funcs=[init_specialist_referral_needed],
    fix_funcs=[None],  # Need doctor to provide referral first
)

urgent_care_needed_task = BaseTask(
    name="urgent_care_needed",
    description="Urgent care appointment needed",
    init_funcs=[init_urgent_care_needed],
    fix_funcs=[fix_urgent_care_appointment],
)

# ============================================================================
# SelectionSets
# ============================================================================

doctor_availability_issues = SelectionSet(
    tasks=[
        doctor_available_task,
        limited_availability_task,
        no_availability_preferred_times_task,
    ]
)

insurance_verification_issues = SelectionSet(
    tasks=[
        insurance_verified_task,
        insurance_not_on_file_task,
        insurance_coverage_limited_task,
    ]
)

calendar_conflict_issues = SelectionSet(
    tasks=[
        no_calendar_conflicts_task,
        has_calendar_conflicts_task,
    ]
)

appointment_type_complexity = SelectionSet(
    tasks=[
        routine_checkup_task,
        specialist_referral_needed_task,
        urgent_care_needed_task,
    ]
)

appointment_scheduling_selection_sets = [
    doctor_availability_issues,
    insurance_verification_issues,
    calendar_conflict_issues,
    appointment_type_complexity,
]


# ============================================================================
