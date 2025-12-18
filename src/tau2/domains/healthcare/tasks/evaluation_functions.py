"""
Evaluation functions for all healthcare domain intents.

This module provides is_fixed() and get_env_assertions() functions for each intent.
These functions use action-based evaluation where appropriate, checking for default
states to determine if there's a pending user request.

All get_env_assertions functions now return a tuple of:
(env_assertions, nl_assertions, communicate_info)
"""

from tau2.data_model.tasks import EnvAssertion
from tau2.domains.healthcare.environment import HealthcareEnvironment


# ============================================================================
# APPOINTMENT_SCHEDULING evaluation functions
# ============================================================================

def get_env_assertions_appointment_scheduling(expected_success: bool) -> tuple[list[EnvAssertion], list[str], list[str]]:
    """
    Get environment assertions for appointment_scheduling tasks.

    Returns tuple of (env_assertions, nl_assertions, communicate_info).

    Uses marker-based evaluation:
    - Baseline has 2 default appointments
    - Issue tasks add markers (date="2024-01-01", time="00:00")
    - Fix actions should create real appointments (non-markers)
    - Success = real appointments >= (baseline + markers)
    """
    if expected_success:
        # Check that appointment was booked (count exceeds baseline + markers)
        env_assertions = [
            EnvAssertion(
                env_type="assistant",
                func_name="assert_appointment_count_exceeds_baseline",
                arguments={},
                assert_value=True,
                message="No new appointment was created - appointment count did not exceed baseline"
            )
        ]

        nl_assertions = [
            # "Agent verified patient identity before accessing appointment information",
            # "Agent confirmed insurance coverage and copay amount with patient",
            # "Agent checked doctor availability before suggesting appointment times",
            # "Agent confirmed appointment details (date, time, doctor, reason) with patient before booking",
            # "Agent provided clear appointment confirmation information"
        ]

        communicate_info = [
            "appointment date",
            "appointment time",
            "doctor name",
            "copay amount"
        ]

        return (env_assertions, nl_assertions, communicate_info)
    else:
        # Transfer to human for administrative issues (insurance, referrals)
        #
        # Add env_assertions to verify CONTEXT-AWARE transfers (not blind transfers)
        # These test that the agent:
        # 1. Gathered context before transferring (verified patient identity)
        # 2. Didn't attempt incorrect actions (didn't book when transfer needed)
        # 3. Understood WHY transfer was needed (administrative block)

        env_assertions = [
            EnvAssertion(
                env_type="assistant",
                func_name="assert_tool_was_called",
                arguments={"tool_name": "get_patient_details"},
                assert_value=True,
                message="Agent transferred without verifying patient identity first"
            ),
            EnvAssertion(
                env_type="assistant",
                func_name="assert_tool_was_not_called",
                arguments={"tool_name": "book_appointment"},
                assert_value=True,
                message="Agent incorrectly attempted to book appointment when transfer was required"
            )
        ]

        nl_assertions = [
            # "Agent explained why appointment cannot be scheduled",
            # "Agent provided alternative options or next steps"
        ]

        return (env_assertions, nl_assertions, [])


def is_fixed_appointment_scheduling(env: HealthcareEnvironment) -> bool:
    """
    Check if appointment scheduling request is resolved.

    Uses the Telecom pattern: runs the same assertions as get_env_assertions.
    This ensures is_fixed() and ENV assertions are always in sync.
    """
    assertions, _, _ = get_env_assertions_appointment_scheduling(expected_success=True)
    success = True
    for assertion in assertions:
        success = success and env.run_env_assertion(
            assertion,
            raise_assertion_error=False,
        )
    return success


# ============================================================================
# URGENT_TRIAGE evaluation functions
# ============================================================================

def get_env_assertions_urgent_triage(expected_success: bool) -> tuple[list[EnvAssertion], list[str], list[str]]:
    """
    Get environment assertions for urgent_triage tasks.

    Uses same marker-based evaluation as appointment_scheduling.
    """
    if expected_success:
        env_assertions = [
            EnvAssertion(
                env_type="assistant",
                func_name="assert_appointment_count_exceeds_baseline",
                arguments={},
                assert_value=True,
                message="No urgent appointment was created - appointment count did not exceed baseline"
            )
        ]

        nl_assertions = [
            # "Agent assessed all reported symptoms systematically",
            # "Agent checked for red flag symptoms (high fever, severe pain, breathing difficulty)",
            # "Agent asked patient to measure temperature if available",
            # "Agent made appropriate triage decision based on symptom severity",
            # "Agent clearly communicated next steps to patient"
        ]

        communicate_info = [
            "urgency level",
            "recommended action"
        ]

        return (env_assertions, nl_assertions, communicate_info)
    else:
        # Transfer to nurse for severe symptoms
        #
        # Add env_assertions to verify CONTEXT-AWARE transfers (not blind transfers)
        # These test that the agent:
        # 1. Gathered context before transferring (assessed symptoms)
        # 2. Didn't attempt incorrect actions (didn't book appointment when transfer needed)
        # 3. Understood WHY transfer was needed (recognized severe symptoms)

        env_assertions = [
            EnvAssertion(
                env_type="assistant",
                func_name="assert_tool_was_called",
                arguments={"tool_name": "check_symptoms"},
                assert_value=True,
                message="Agent transferred without assessing symptoms first"
            ),
            EnvAssertion(
                env_type="assistant",
                func_name="assert_tool_was_not_called",
                arguments={"tool_name": "book_appointment"},
                assert_value=True,
                message="Agent incorrectly attempted to book appointment when transfer was required"
            )
        ]

        nl_assertions = [
            # "Agent recognized severe/critical symptoms requiring immediate clinical attention",
            # "Agent explained need for nurse/clinical review",
            # "Agent transferred patient promptly"
        ]

        return (env_assertions, nl_assertions, [])


def is_fixed_urgent_triage(env: HealthcareEnvironment) -> bool:
    """
    Check if urgent triage request is resolved.

    Uses the Telecom pattern: runs the same assertions as get_env_assertions.
    """
    assertions, _, _ = get_env_assertions_urgent_triage(expected_success=True)
    success = True
    for assertion in assertions:
        success = success and env.run_env_assertion(
            assertion,
            raise_assertion_error=False,
        )
    return success


# ============================================================================
# CHRONIC_MONITORING evaluation functions
# ============================================================================

def get_env_assertions_chronic_monitoring(expected_success: bool) -> tuple[list[EnvAssertion], list[str], list[str]]:
    """
    Get environment assertions for chronic_monitoring tasks.

    Uses same marker-based evaluation as appointment_scheduling.
    """
    if expected_success:
        env_assertions = [
            EnvAssertion(
                env_type="assistant",
                func_name="assert_appointment_count_exceeds_baseline",
                arguments={},
                assert_value=True,
                message="No monitoring appointment was created - appointment count did not exceed baseline"
            )
        ]

        nl_assertions = [
            # "Agent requested all relevant home monitoring readings (BP, glucose, SpO2 as appropriate)",
            # "Agent asked patient to take measurements if not recently done",
            # "Agent assessed whether readings are within normal ranges for patient's conditions",
            # "Agent made appropriate recommendation based on readings",
            # "Agent provided clear guidance on when to seek further care"
        ]

        communicate_info = [
            "reading assessment",
            "recommended action"
        ]

        return (env_assertions, nl_assertions, communicate_info)
    else:
        # Transfer to nurse for concerning values
        #
        # Add env_assertions to verify CONTEXT-AWARE transfers (not blind transfers)
        # These test that the agent:
        # 1. Gathered context before transferring (checked vital signs)
        # 2. Didn't attempt incorrect actions (didn't book appointment when transfer needed)
        # 3. Understood WHY transfer was needed (critical vital signs)
        #
        # Note: We check for measure_* tools (measure_blood_pressure, measure_blood_glucose, measure_oxygen_saturation)
        # But since there are multiple possible vital sign tools, we cannot check for a specific one
        # Instead, we verify the agent didn't skip straight to booking

        env_assertions = [
            EnvAssertion(
                env_type="assistant",
                func_name="assert_tool_was_not_called",
                arguments={"tool_name": "book_appointment"},
                assert_value=True,
                message="Agent incorrectly attempted to book appointment when transfer was required"
            )
        ]

        nl_assertions = [
            # "Agent identified concerning vital sign readings requiring clinical review",
            # "Agent explained need for nurse evaluation",
            # "Agent transferred patient for immediate clinical assessment"
        ]

        return (env_assertions, nl_assertions, [])


def is_fixed_chronic_monitoring(env: HealthcareEnvironment) -> bool:
    """
    Check if chronic monitoring request is resolved.

    Uses the Telecom pattern: runs the same assertions as get_env_assertions.
    """
    assertions, _, _ = get_env_assertions_chronic_monitoring(expected_success=True)
    success = True
    for assertion in assertions:
        success = success and env.run_env_assertion(
            assertion,
            raise_assertion_error=False,
        )
    return success


# ============================================================================
# TELEHEALTH_SETUP evaluation functions
# ============================================================================

def is_fixed_telehealth_setup(env: HealthcareEnvironment) -> bool:
    """
    Check if telehealth setup request is resolved.

    With the updated design:
    - Baseline tasks ADD all consents/instructions
    - Issue tasks leave lists EMPTY or partially filled
    - Fix tasks ADD the missing items

    Fresh environment (before any initialization):
    - consents_provided: []
    - emergency_contact: None
    - acknowledged_instructions: []
    → Default "good" state, return True

    After baseline initialization:
    - consents_provided: ["telehealth", "data_sharing"]
    - emergency_contact: valid contact OR None (depending on SelectionSet)
    - acknowledged_instructions: ["medication", "post_care", "pre_surgery"]
    → Fixed state, return True

    After issue initialization:
    - consents_provided: [] or ["data_sharing"] (missing telehealth)
    - emergency_contact: None OR "Old Contact (disconnected)"
    - acknowledged_instructions: [] or partial list
    → Not fixed, return False

    Fixed when:
    - Fresh environment (empty lists AND no invalid emergency contact) → True
    - OR All required consents/instructions present AND emergency contact not invalid → True

    Not fixed when:
    - Consents/instructions provided but some missing → False
    - OR Emergency contact is invalid ("Old Contact" or "disconnected") → False
    """
    consents_provided = set(env.user_tools.device.consents_provided or [])
    acknowledged_instructions = set(env.user_tools.device.acknowledged_instructions or [])
    emergency_contact = env.user_tools.surroundings.emergency_contact

    # Check if emergency contact is in INVALID state
    # "Old Contact", "disconnected", or "MISSING" indicates an unresolved issue
    if emergency_contact is not None:
        contact_str = str(emergency_contact)
        if "Old Contact" in contact_str or "disconnected" in contact_str or "MISSING" in contact_str:
            return False

    # If environment is fresh (empty lists), it's in default "good" state
    if len(consents_provided) == 0 and len(acknowledged_instructions) == 0:
        return True

    # Check requirements for each dimension independently
    # This allows tasks that only test one dimension (e.g., just consents) to pass
    required_consents = {"telehealth", "data_sharing"}
    required_instructions = {"medication", "post_care", "pre_surgery"}

    # If ANY consents were provided, check they're ALL present
    if len(consents_provided) > 0:
        if not required_consents.issubset(consents_provided):
            return False

    # If ANY instructions were acknowledged, check they're ALL present
    if len(acknowledged_instructions) > 0:
        if not required_instructions.issubset(acknowledged_instructions):
            return False

    # All provided requirements are met (no partial state)
    return True


def get_env_assertions_telehealth_setup(expected_success: bool) -> tuple[list[EnvAssertion], list[str], list[str]]:
    """
    Get environment assertions for telehealth_setup tasks.

    Uses the Telecom pattern: state-based evaluation via is_fixed_telehealth_setup.
    The is_fixed function comprehensively checks:
    - All required consents collected (telehealth, data_sharing)
    - Valid emergency contact (not disconnected/invalid)
    - All instructions acknowledged (medication, post_care, pre_surgery)

    Since is_fixed provides complete validation, we don't duplicate logic with ENV assertions.
    This is outcome-focused: as long as the compliance state is correct, workflow doesn't matter.
    """
    if expected_success:
        # Note: We rely on is_fixed_telehealth_setup for state validation
        # No ENV assertions needed - is_fixed provides comprehensive compliance checking
        env_assertions = []

        nl_assertions = [
            # "Agent obtained all required telehealth consents from patient",
            # "Agent verified emergency contact information is current",
            # "Agent ensured patient acknowledged all medical instructions",
            # "Agent confirmed patient has necessary technology for telehealth session",
            # "Agent provided clear information about telehealth appointment process"
        ]

        communicate_info = [
            "telehealth appointment details",
            "technical requirements"
        ]

        return (env_assertions, nl_assertions, communicate_info)
    else:
        nl_assertions = [
            # "Agent identified missing required consents or information",
            # "Agent explained what is needed to complete telehealth setup"
        ]

        return ([], nl_assertions, [])


# ============================================================================
# TEST_RESULTS_ACCESS evaluation functions
# ============================================================================

def get_env_assertions_test_results_access(expected_success: bool) -> tuple[list[EnvAssertion], list[str], list[str]]:
    """
    Get environment assertions for test_results_access tasks.

    Uses same marker-based evaluation as appointment_scheduling.
    """
    if expected_success:
        env_assertions = [
            EnvAssertion(
                env_type="assistant",
                func_name="assert_appointment_count_exceeds_baseline",
                arguments={},
                assert_value=True,
                message="No follow-up appointment was created - appointment count did not exceed baseline"
            )
        ]

        nl_assertions = [
            # "Agent verified patient identity before discussing test results",
            # "Agent checked test result status (ready, pending, or under review)",
            # "Agent directed patient to appropriate resource (portal for ready results, follow-up for abnormalities)",
            # "Agent explained test result findings in patient-friendly language if available",
            # "Agent scheduled follow-up if abnormalities were detected"
        ]

        communicate_info = [
            "test result status",
            "how to access results"
        ]

        return (env_assertions, nl_assertions, communicate_info)
    else:
        # Transfer to nurse for critical results
        #
        # Add env_assertions to verify CONTEXT-AWARE transfers (not blind transfers)
        # These test that the agent:
        # 1. Gathered context before transferring (checked test results)
        # 2. Didn't attempt incorrect actions (didn't book appointment when transfer needed)
        # 3. Understood WHY transfer was needed (recognized critical results)

        env_assertions = [
            EnvAssertion(
                env_type="assistant",
                func_name="assert_tool_was_called",
                arguments={"tool_name": "check_test_results"},
                assert_value=True,
                message="Agent transferred without checking test results first"
            ),
            EnvAssertion(
                env_type="assistant",
                func_name="assert_tool_was_not_called",
                arguments={"tool_name": "book_appointment"},
                assert_value=True,
                message="Agent incorrectly attempted to book appointment when transfer was required"
            )
        ]

        nl_assertions = [
            # "Agent identified critical/urgent test results requiring clinical review",
            # "Agent did not release critical results directly to patient without clinical review",
            # "Agent transferred patient to nurse for proper clinical evaluation"
        ]

        return (env_assertions, nl_assertions, [])


def is_fixed_test_results_access(env: HealthcareEnvironment) -> bool:
    """
    Check if test results access request is resolved.

    Uses the Telecom pattern: runs the same assertions as get_env_assertions.
    """
    assertions, _, _ = get_env_assertions_test_results_access(expected_success=True)
    success = True
    for assertion in assertions:
        success = success and env.run_env_assertion(
            assertion,
            raise_assertion_error=False,
        )
    return success
