from tau2.data_model.message import ToolCall
from tau2.data_model.tasks import EnvAssertion, EnvFunctionCall
from tau2.domains.healthcare.environment import HealthcareEnvironment
from tau2.domains.healthcare.tasks.utils import BaseTask, SelectionSet

# ============================================================================
# TEST_RESULTS_ACCESS Intent - SelectionSets 17-18
# ============================================================================

# ============================================================================
# ----------------------------------------------------------------------------
# SelectionSet 17: test_result_status_issues
# ----------------------------------------------------------------------------

def init_test_results_ready(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Test results are ready and available (baseline)."""
    # Set test result to ready status
    if "test_001" in env.tools.db.test_results:
        env.tools.db.test_results["test_001"].status = "ready"
        env.tools.db.test_results["test_001"].result = "Complete Blood Count (CBC) - All values within normal range"
        env.tools.db.test_results["test_001"].notes = "Results reviewed and appear normal"

    # Sync user-side portal to show test results are available
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="set_portal_info",
            arguments={
                "upcoming_appointments": [],
                "recent_visits": [],
                "test_results_available": True,
                "test_results": [
                    {
                        "test_name": "HbA1c (Diabetes screening)",
                        "test_date": "2024-05-10",
                        "result": "Complete Blood Count (CBC) - All values within normal range",
                        "notes": "Results reviewed and appear normal"
                    }
                ],
                "messages_count": 0,
                "outstanding_balance": 0
            }
        )
    ]


def init_test_results_pending(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Test results are still pending from lab."""
    # Set test result to pending status
    if "test_001" in env.tools.db.test_results:
        env.tools.db.test_results["test_001"].status = "pending"
        env.tools.db.test_results["test_001"].result = None
        env.tools.db.test_results["test_001"].notes = None

    # Create marker to indicate pending state and sync user-side portal
    return [
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_test_results_waiting",  # For pending results (non-fixable)
                "patient_id": "patient_001",
                "reason": "Pending test results - awaiting lab"
            }
        ),
        EnvFunctionCall(
            env_type="user",
            func_name="set_portal_info",
            arguments={
                "upcoming_appointments": [],
                "recent_visits": [],
                "test_results_available": False,
                "test_results": [],  # No results yet - still pending
                "messages_count": 0,
                "outstanding_balance": 0
            }
        )
    ]


def init_test_results_reviewed_by_doctor(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Test results ready but awaiting doctor review before release."""
    # Set test result to reviewed status
    if "test_001" in env.tools.db.test_results:
        env.tools.db.test_results["test_001"].status = "reviewed"
        env.tools.db.test_results["test_001"].result = "Lipid Panel - Elevated cholesterol levels noted"
        env.tools.db.test_results["test_001"].notes = "Doctor review required before release - follow-up needed"

    # Create marker to indicate pending doctor review and sync user-side portal
    return [
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_test_results_doctor_review",  # For reviewed results (non-fixable)
                "patient_id": "patient_001",
                "reason": "Pending test results - awaiting doctor review"
            }
        ),
        EnvFunctionCall(
            env_type="user",
            func_name="set_portal_info",
            arguments={
                "upcoming_appointments": [],
                "recent_visits": [],
                "test_results_available": False,  # Not released to patient yet
                "test_results": [],  # Not released to patient - awaiting doctor review
                "messages_count": 0,
                "outstanding_balance": 0
            }
        )
    ]


def fix_provide_test_results(env: HealthcareEnvironment) -> list[ToolCall]:
    """Provide ready test results to patient with full verification workflow.

    Multi-step dependent workflow:
    1. Verify patient identity
    2. Check test results status (depends on #1)
    3. Provide results to patient (depends on #2)
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
        # Step 2: Check test results status
        ToolCall(
            requestor="assistant",
            name="check_test_results",
            arguments={
                "patient_id": "patient_001",
                "test_id": "test_001"
            }
        )
        # Step 3 is implicit - agent provides results via communication
    ]


# ----------------------------------------------------------------------------
# SelectionSet 18: abnormal_results_issues
# ----------------------------------------------------------------------------

def init_results_normal(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Test results are normal (baseline)."""
    # Set test results to normal
    if "test_001" in env.tools.db.test_results:
        env.tools.db.test_results["test_001"].status = "ready"
        env.tools.db.test_results["test_001"].result = "All test values within normal reference ranges"
        env.tools.db.test_results["test_001"].notes = "No abnormalities detected"

    # Sync user-side portal to show test results are available
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="set_portal_info",
            arguments={
                "upcoming_appointments": [],
                "recent_visits": [],
                "test_results_available": True,
                "test_results": [
                    {
                        "test_name": "HbA1c (Diabetes screening)",
                        "test_date": "2024-05-10",
                        "result": "All test values within normal reference ranges",
                        "notes": "No abnormalities detected"
                    }
                ],
                "messages_count": 0,
                "outstanding_balance": 0
            }
        )
    ]


def init_results_abnormal_minor(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Test results show minor abnormalities requiring follow-up."""
    # Set test results to have minor abnormalities
    if "test_001" in env.tools.db.test_results:
        env.tools.db.test_results["test_001"].status = "ready"
        env.tools.db.test_results["test_001"].result = "Slightly elevated cholesterol (220 mg/dL) - recommend dietary modifications"
        env.tools.db.test_results["test_001"].notes = "Minor abnormality - follow-up in 3 months recommended"

    return [
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_test_results_followup",  # For scheduling follow-up
                "patient_id": "patient_001",
                "reason": "Pending test results follow-up - minor abnormalities"
            }
        ),
        EnvFunctionCall(
            env_type="user",
            func_name="set_portal_info",
            arguments={
                "upcoming_appointments": [],
                "recent_visits": [],
                "test_results_available": True,  # Results are ready and available to patient
                "test_results": [
                    {
                        "test_name": "HbA1c (Diabetes screening)",
                        "test_date": "2024-05-10",
                        "result": "Slightly elevated cholesterol (220 mg/dL) - recommend dietary modifications",
                        "notes": "Minor abnormality - follow-up in 3 months recommended"
                    }
                ],
                "messages_count": 0,
                "outstanding_balance": 0
            }
        )
    ]


def init_results_abnormal_critical(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Test results show critical abnormalities requiring immediate action."""
    # Set test results to critical
    if "test_001" in env.tools.db.test_results:
        env.tools.db.test_results["test_001"].status = "reviewed"
        env.tools.db.test_results["test_001"].result = "CRITICAL: Severely elevated glucose (450 mg/dL) and abnormal kidney function"
        env.tools.db.test_results["test_001"].notes = "URGENT - Patient requires immediate medical evaluation"

    return [
        EnvFunctionCall(
            env_type="assistant",
            func_name="create_appointment_marker",
            arguments={
                "appointment_id": "pending_test_results_critical_transfer",  # For emergency transfer
                "patient_id": "patient_001",
                "reason": "Pending test results - critical findings requiring immediate attention"
            }
        ),
        EnvFunctionCall(
            env_type="user",
            func_name="set_portal_info",
            arguments={
                "upcoming_appointments": [],
                "recent_visits": [],
                "test_results_available": False,  # Critical results not released to patient, needs nurse review
                "test_results": [],  # Critical results not released - requires nurse review
                "messages_count": 0,
                "outstanding_balance": 0
            }
        )
    ]


def fix_schedule_followup_minor(env: HealthcareEnvironment) -> list[ToolCall]:
    """Schedule follow-up appointment for minor abnormalities with full workflow.

    Multi-step dependent workflow:
    1. Verify patient identity
    2. Check test results
    3. Verify insurance for follow-up
    4. Book follow-up appointment (depends on #1-3)
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
        # Step 2: Check test results
        ToolCall(
            requestor="assistant",
            name="check_test_results",
            arguments={
                "patient_id": "patient_001",
                "test_id": "test_001"
            }
        ),
        # Step 3: Verify insurance coverage for follow-up
        ToolCall(
            requestor="assistant",
            name="verify_insurance_coverage",
            arguments={
                "patient_id": "patient_001",
                "procedure_type": "follow_up"
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
                "date": "2024-05-30",
                "time": "10:00",
                "reason": "Follow-up for abnormal test results - discuss findings and treatment plan"
            }
        )
    ]


def fix_escalate_critical_results(env: HealthcareEnvironment) -> list[ToolCall]:
    """Escalate critical test results to clinical staff with verification.

    Multi-step dependent workflow:
    1. Verify patient identity
    2. Check test results to confirm critical status (depends on #1)
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
        # Step 2: Check test results to confirm critical status
        ToolCall(
            requestor="assistant",
            name="check_test_results",
            arguments={
                "patient_id": "patient_001",
                "test_id": "test_001"
            }
        ),
        # Step 3: Transfer to nurse for immediate clinical review
        ToolCall(
            requestor="assistant",
            name="transfer_to_nurse",
            arguments={}
        )
    ]


# ============================================================================
# Base Tasks for SelectionSet 17: test_result_status_issues
# ============================================================================

test_results_ready_task = BaseTask(
    name="ready",
    description="Test results ready and available (baseline)",
    init_funcs=[init_test_results_ready],
    fix_funcs=[],  # Baseline task - results are ready, no fix needed
)

test_results_pending_task = BaseTask(
    name="pending",
    description="Test results still pending from lab",
    init_funcs=[init_test_results_pending],
    fix_funcs=[None],  # Cannot provide results that aren't ready yet
)

test_results_reviewed_by_doctor_task = BaseTask(
    name="reviewed_by_doctor",
    description="Results awaiting doctor review before release",
    init_funcs=[init_test_results_reviewed_by_doctor],
    fix_funcs=[None],  # Must wait for doctor review before releasing
)

# ============================================================================
# Base Tasks for SelectionSet 18: abnormal_results_issues
# ============================================================================

results_normal_task = BaseTask(
    name="normal",
    description="Test results normal (baseline)",
    init_funcs=[init_results_normal],
    fix_funcs=[],
)

results_abnormal_minor_task = BaseTask(
    name="abnormal_minor",
    description="Minor abnormalities requiring follow-up",
    init_funcs=[init_results_abnormal_minor],
    fix_funcs=[fix_schedule_followup_minor],
)

results_abnormal_critical_task = BaseTask(
    name="abnormal_critical",
    description="Critical abnormalities requiring immediate action",
    init_funcs=[init_results_abnormal_critical],
    fix_funcs=[None],  # Cannot be fixed - requires transfer to nurse
)

# ============================================================================
# SelectionSets
# ============================================================================

test_result_status_issues = SelectionSet(
    tasks=[
        test_results_ready_task,
        test_results_pending_task,
        test_results_reviewed_by_doctor_task,
    ]
)

abnormal_results_issues = SelectionSet(
    tasks=[
        results_normal_task,
        results_abnormal_minor_task,
        results_abnormal_critical_task,
    ]
)

test_results_selection_sets = [
    test_result_status_issues,
    abnormal_results_issues,
]


# ============================================================================
