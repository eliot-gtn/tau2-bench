from tau2.data_model.message import ToolCall
from tau2.data_model.tasks import EnvAssertion, EnvFunctionCall
from tau2.domains.healthcare.environment import HealthcareEnvironment
from tau2.domains.healthcare.tasks.utils import BaseTask, SelectionSet

# ============================================================================
# PRESCRIPTION_REFILL_ISSUE Intent - SelectionSets 1-3
# ============================================================================

# ============================================================================
# ----------------------------------------------------------------------------
# SelectionSet 1: refills_status_issues
# ----------------------------------------------------------------------------

def init_no_refills_remaining(env: HealthcareEnvironment) -> list[EnvFunctionCall | EnvAssertion]:
    """Set prescription to have 0 refills remaining."""
    # Get prescription details from agent database
    rx = env.tools.db.prescriptions["rx_001"]
    doctor = env.tools.db.doctors[rx.doctor_id]

    return [
        # Agent-side: Update prescription refills
        EnvFunctionCall(
            env_type="assistant",
            func_name="set_prescription_refills",
            arguments={
                "prescription_id": "rx_001",
                "refills": 0
            }
        ),
        # User-side: Add medication bottle so patient can check it
        EnvFunctionCall(
            env_type="user",
            func_name="add_medication_at_home",
            arguments={
                "prescription_number": "rx_001",
                "medication_name": rx.medication_name,
                "dosage": rx.dosage,
                "refills_remaining": 0,  # Match agent-side refills
                "prescribing_doctor": f"Dr. {doctor.name.first_name} {doctor.name.last_name}",
                "pharmacy_name": "Community Pharmacy",
                "pharmacy_phone": "(555) 123-4567"
            }
        ),
        # Assertions
        EnvAssertion(
            env_type="assistant",
            func_name="assert_prescription_refills_remaining",
            arguments={
                "prescription_id": "rx_001",
                "expected_count": 0
            },
            assert_value=True
        )
    ]


def init_has_refills_available(env: HealthcareEnvironment) -> list[EnvFunctionCall | EnvAssertion]:
    """Set prescription to have refills available and create a pending refill request.

    We set refills to 3 to distinguish from the default state (refills=2).
    After request_prescription_refill is called, it will decrement to 2, returning to default.
    """
    # Get prescription details from agent database
    rx = env.tools.db.prescriptions["rx_001"]
    doctor = env.tools.db.doctors[rx.doctor_id]

    return [
        # Agent-side: Update prescription refills and status
        EnvFunctionCall(
            env_type="assistant",
            func_name="set_prescription_refills",
            arguments={
                "prescription_id": "rx_001",
                "refills": 3  # Non-default value to indicate pending request
            }
        ),
        EnvFunctionCall(
            env_type="assistant",
            func_name="set_prescription_status",
            arguments={
                "prescription_id": "rx_001",
                "status": "active"
            }
        ),
        # User-side: Add medication bottle so patient can check it
        EnvFunctionCall(
            env_type="user",
            func_name="add_medication_at_home",
            arguments={
                "prescription_number": "rx_001",
                "medication_name": rx.medication_name,
                "dosage": rx.dosage,
                "refills_remaining": 3,  # Match agent-side refills
                "prescribing_doctor": f"Dr. {doctor.name.first_name} {doctor.name.last_name}",
                "pharmacy_name": "Community Pharmacy",
                "pharmacy_phone": "(555) 123-4567"
            }
        ),
        # Assertions
        EnvAssertion(
            env_type="assistant",
            func_name="assert_prescription_refills_remaining",
            arguments={
                "prescription_id": "rx_001",
                "expected_count": 3
            },
            assert_value=True
        ),
        EnvAssertion(
            env_type="assistant",
            func_name="assert_prescription_status",
            arguments={
                "prescription_id": "rx_001",
                "expected_status": "active"
            },
            assert_value=True
        )
    ]


def fix_has_refills_available(env: HealthcareEnvironment) -> list[ToolCall]:
    """Process refill for prescription with refills available.

    Multi-step dependent workflow:
    1. Verify patient identity
    2. Ask patient to check medication bottle for prescription info (depends on #1)
    3. Get prescription details to verify refills available (depends on #2)
    4. Request refill (depends on #3)
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
        # Step 2: Ask patient to check medication bottle
        ToolCall(
            requestor="user",
            name="check_medication_bottle",
            arguments={}
        ),
        # Step 3: Get prescription details to verify refills available
        ToolCall(
            requestor="assistant",
            name="get_prescription_details",
            arguments={
                "prescription_id": "rx_001"
            }
        ),
        # Step 4: Request refill
        ToolCall(
            requestor="assistant",
            name="request_prescription_refill",
            arguments={
                "patient_id": "patient_001",
                "prescription_id": "rx_001"
            }
        )
    ]


# ----------------------------------------------------------------------------
# SelectionSet 2: prescription_status_issues
# ----------------------------------------------------------------------------

def init_prescription_active(env: HealthcareEnvironment) -> list[EnvFunctionCall | EnvAssertion]:
    """Set prescription status to active (baseline)."""
    return [
        EnvFunctionCall(
            env_type="assistant",
            func_name="set_prescription_status",
            arguments={
                "prescription_id": "rx_001",
                "status": "active"
            }
        ),
        EnvAssertion(
            env_type="assistant",
            func_name="assert_prescription_status",
            arguments={
                "prescription_id": "rx_001",
                "expected_status": "active"
            },
            assert_value=True
        )
    ]


def init_prescription_expired(env: HealthcareEnvironment) -> list[EnvFunctionCall | EnvAssertion]:
    """Set prescription status to expired."""
    return [
        EnvFunctionCall(
            env_type="assistant",
            func_name="set_prescription_status",
            arguments={
                "prescription_id": "rx_001",
                "status": "expired"
            }
        ),
        EnvAssertion(
            env_type="assistant",
            func_name="assert_prescription_status",
            arguments={
                "prescription_id": "rx_001",
                "expected_status": "expired"
            },
            assert_value=True
        )
    ]


def init_prescription_discontinued(env: HealthcareEnvironment) -> list[EnvFunctionCall | EnvAssertion]:
    """Set prescription status to discontinued by doctor."""
    return [
        EnvFunctionCall(
            env_type="assistant",
            func_name="set_prescription_status",
            arguments={
                "prescription_id": "rx_001",
                "status": "discontinued"
            }
        ),
        EnvAssertion(
            env_type="assistant",
            func_name="assert_prescription_status",
            arguments={
                "prescription_id": "rx_001",
                "expected_status": "discontinued"
            },
            assert_value=True
        )
    ]


# ----------------------------------------------------------------------------
# SelectionSet 3: prescription_type_issues
# ----------------------------------------------------------------------------
# NOTE: This SelectionSet is for future extension. Currently, controlled
# substances would require modifying the data model to add an is_controlled field.
# For now, we can add a note field to mark it, or skip this SelectionSet in v1.

def init_regular_medication(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Initialize with regular non-controlled medication (baseline)."""
    # For now, this is just a marker - no state change needed
    # In future, could add metadata to prescription
    return []


def init_controlled_substance(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Initialize with controlled substance requiring special handling."""
    return [
        EnvFunctionCall(
            env_type="assistant",
            func_name="set_prescription_medication",
            arguments={
                "prescription_id": "rx_001",
                "medication_name": "Oxycodone",
                "dosage": "5mg every 6 hours as needed"
            }
        )
    ]


# ============================================================================
# Base Tasks for SelectionSet 1: refills_status_issues
# ============================================================================

no_refills_remaining_task = BaseTask(
    name="no_refills_remaining",
    description="Patient has 0 refills left on prescription",
    init_funcs=[init_no_refills_remaining],
    fix_funcs=[None],  # Cannot be fixed - need doctor to prescribe new Rx
)

has_refills_available_task = BaseTask(
    name="has_refills_available",
    description="Patient has refills available (baseline/control)",
    init_funcs=[init_has_refills_available],
    fix_funcs=[fix_has_refills_available],
)

# ============================================================================
# Base Tasks for SelectionSet 2: prescription_status_issues
# ============================================================================

prescription_active_task = BaseTask(
    name="prescription_active",
    description="Prescription is active (baseline)",
    init_funcs=[init_prescription_active],
    fix_funcs=[],  # No fix needed - baseline state
)

prescription_expired_task = BaseTask(
    name="prescription_expired",
    description="Prescription has expired",
    init_funcs=[init_prescription_expired],
    fix_funcs=[None],  # Cannot be fixed - need new prescription from doctor
)

prescription_discontinued_task = BaseTask(
    name="prescription_discontinued",
    description="Prescription was discontinued by doctor",
    init_funcs=[init_prescription_discontinued],
    fix_funcs=[None],  # Cannot be fixed - doctor discontinued it
)

# ============================================================================
# Base Tasks for SelectionSet 3: prescription_type_issues
# ============================================================================

regular_medication_task = BaseTask(
    name="regular_medication",
    description="Regular non-controlled medication (baseline)",
    init_funcs=[init_regular_medication],
    fix_funcs=[],  # No fix needed - baseline state
)

controlled_substance_task = BaseTask(
    name="controlled_substance",
    description="Controlled substance requiring special handling",
    init_funcs=[init_controlled_substance],
    fix_funcs=[None],  # Requires transfer to nurse for in-person visit
)

# ============================================================================
# SelectionSets
# ============================================================================

refills_status_issues = SelectionSet(
    tasks=[
        no_refills_remaining_task,
        has_refills_available_task,
    ]
)

prescription_status_issues = SelectionSet(
    tasks=[
        prescription_active_task,
        prescription_expired_task,
        prescription_discontinued_task,
    ]
)

prescription_type_issues = SelectionSet(
    tasks=[
        regular_medication_task,
        controlled_substance_task,
    ]
)

prescription_refill_selection_sets = [
    refills_status_issues,
    prescription_status_issues,
    prescription_type_issues,
]


# ============================================================================
# Evaluation Functions for prescription_refill intent
# ============================================================================

def is_fixed_prescription_refill(env: HealthcareEnvironment) -> bool:
    """
    Check if the prescription refill issue is resolved.

    This function checks if the prescription is in its DEFAULT state (refills=2, status="active").
    If the prescription has been modified from the default (by task initialization), it means
    there's a pending user request, so it's NOT fixed.

    The prescription is considered "fixed" (no pending request) when:
    - rx_001 doesn't exist, OR
    - rx_001 is in default state (refills=2, status="active"), OR
    - rx_001 has been successfully modified by fix actions (refills decreased from initial value)

    Note: This is a simplified heuristic. The actual evaluation relies on ACTION_CHECK and
    ENV_ASSERTION to verify correct behavior.

    Returns:
        True if prescription is in a good/default state, False if there's a pending request
    """
    if "rx_001" not in env.tools.db.prescriptions:
        return True

    rx = env.tools.db.prescriptions["rx_001"]

    # Default state for rx_001 is: refills=2, status="active", medication="Lisinopril"
    # If prescription matches default, there's no pending task
    is_default_state = (
        rx.refills_remaining == 2
        and rx.status == "active"
        and rx.medication_name == "Lisinopril"
    )

    return is_default_state


def get_env_assertions_prescription_refill(expected_success: bool) -> tuple[list[EnvAssertion], list[str], list[str]]:
    """
    Get environment assertions for prescription_refill tasks.

    This function provides additional state verification beyond is_fixed().

    For expected_success=True (fixable tasks):
    - ENV_ASSERTIONS: Prescription has at least 1 refill remaining, status is "active"
    - NL_ASSERTIONS: Behavioral checks for patient interaction quality
    - COMMUNICATE_INFO: Required information to communicate to patient

    For expected_success=False (non-fixable tasks):
    - Returns empty lists since ACTION_CHECK verifies the transfer was called

    Args:
        expected_success: Whether the task is expected to be successfully resolved
                         (True = refill should succeed, False = should escalate)

    Returns:
        Tuple of (env_assertions, nl_assertions, communicate_info)
    """
    if expected_success:
        # Task should be fixable - verify prescription state after refill
        # After processing a refill from init state (refills=3), we expect refills=2 (default state)
        env_assertions = [
            EnvAssertion(
                env_type="assistant",
                func_name="assert_prescription_status",
                arguments={
                    "prescription_id": "rx_001",
                    "expected_status": "active"
                },
                assert_value=True,
                message="Prescription status should be active for successful refill"
            ),
            EnvAssertion(
                env_type="assistant",
                func_name="assert_prescription_refills_remaining",
                arguments={
                    "prescription_id": "rx_001",
                    "expected_count": 2  # After refill from 3, should return to default (2)
                },
                assert_value=True,
                message="Prescription should have 2 refills remaining after processing one refill"
            )
        ]

        # Natural language behavioral assertions
        nl_assertions = [
            # "Agent verified patient identity before processing prescription refill",
            # "Agent confirmed medication name and dosage with patient",
            # "Agent informed patient of pharmacy location for pickup",
            # "Agent communicated estimated pickup timeline to patient"
        ]

        # Required information to communicate
        communicate_info = [
            "Community Pharmacy",  # Pharmacy name
            "2-4 hours"  # Pickup timeline
        ]

        return (env_assertions, nl_assertions, communicate_info)
    else:
        # Task is NOT fixable - agent should have escalated to nurse
        #
        # Add env_assertions to verify CONTEXT-AWARE transfers (not blind transfers)
        # These test that the agent:
        # 1. Gathered context before transferring (checked prescription details)
        # 2. Didn't attempt incorrect actions (didn't try to refill when it shouldn't)
        # 3. Understood WHY transfer was needed (protocol compliance)

        env_assertions = [
            EnvAssertion(
                env_type="assistant",
                func_name="assert_tool_was_called",
                arguments={"tool_name": "get_prescription_details"},
                assert_value=True,
                message="Agent transferred without checking prescription details first"
            ),
            EnvAssertion(
                env_type="assistant",
                func_name="assert_tool_was_not_called",
                arguments={"tool_name": "request_prescription_refill"},
                assert_value=True,
                message="Agent incorrectly attempted to refill prescription that requires nurse escalation"
            )
        ]

        nl_assertions = []

        return (env_assertions, nl_assertions, [])
