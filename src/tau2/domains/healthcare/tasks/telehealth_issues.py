from tau2.data_model.message import ToolCall
from tau2.data_model.tasks import EnvAssertion, EnvFunctionCall
from tau2.domains.healthcare.environment import HealthcareEnvironment
from tau2.domains.healthcare.tasks.utils import BaseTask, SelectionSet

# ============================================================================
# TELEHEALTH_SETUP_ISSUE Intent - SelectionSets 14-16
# ============================================================================

# ============================================================================
# ----------------------------------------------------------------------------
# SelectionSet 14: consent_issues
# ----------------------------------------------------------------------------

def init_consent_not_required(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """No consent required for this interaction (baseline)."""
    # Baseline: all consents are provided
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="provide_consent",
            arguments={"consent_type": "telehealth"}
        ),
        EnvFunctionCall(
            env_type="user",
            func_name="provide_consent",
            arguments={"consent_type": "data_sharing"}
        )
    ]


def init_telehealth_consent_needed(env: HealthcareEnvironment) -> list[EnvFunctionCall | EnvAssertion]:
    """Telehealth consent required but not yet provided."""
    # Only add data_sharing consent (missing telehealth)
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="provide_consent",
            arguments={"consent_type": "data_sharing"}
        )
    ]


def init_data_sharing_consent_needed(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Data sharing consent required for specialist referral."""
    # Only add telehealth consent (missing data_sharing)
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="provide_consent",
            arguments={"consent_type": "telehealth"}
        )
    ]


def fix_obtain_telehealth_consent(env: HealthcareEnvironment) -> list[ToolCall]:
    """Obtain telehealth consent from patient."""
    return [
        ToolCall(
            requestor="user",
            name="provide_consent",
            arguments={
                "consent_type": "telehealth"
            }
        )
    ]


def fix_obtain_data_sharing_consent(env: HealthcareEnvironment) -> list[ToolCall]:
    """Obtain data sharing consent from patient."""
    return [
        ToolCall(
            requestor="user",
            name="provide_consent",
            arguments={
                "consent_type": "data_sharing"
            }
        )
    ]


# ----------------------------------------------------------------------------
# SelectionSet 15: emergency_contact_issues
# ----------------------------------------------------------------------------

def init_emergency_contact_current(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Emergency contact is current and on file (baseline)."""
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="set_emergency_contact",
            arguments={
                "name": "Jane Smith",
                "phone": "555-0102",
                "relationship": "spouse"
            }
        )
    ]


def init_emergency_contact_missing(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """No emergency contact on file."""
    # Set an invalid emergency contact to signal missing state
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="set_emergency_contact",
            arguments={
                "name": "MISSING - No emergency contact on file",
                "phone": "000-0000",
                "relationship": "none"
            }
        )
    ]


def init_emergency_contact_outdated(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Emergency contact information is outdated."""
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="set_emergency_contact",
            arguments={
                "name": "Old Contact (disconnected)",
                "phone": "555-9999",
                "relationship": "friend"
            }
        )
    ]


def fix_update_emergency_contact(env: HealthcareEnvironment) -> list[ToolCall]:
    """Update emergency contact information."""
    return [
        ToolCall(
            requestor="user",
            name="update_emergency_contact",
            arguments={
                "name": "Jane Smith",
                "phone": "555-0102",
                "relationship": "spouse"
            }
        )
    ]


# ----------------------------------------------------------------------------
# SelectionSet 16: instruction_acknowledgment_issues
# ----------------------------------------------------------------------------

def init_no_instructions_needed(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """No special instructions required (baseline)."""
    # Baseline: all instructions are acknowledged
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="acknowledge_instructions",
            arguments={"instruction_type": "medication"}
        ),
        EnvFunctionCall(
            env_type="user",
            func_name="acknowledge_instructions",
            arguments={"instruction_type": "post_care"}
        ),
        EnvFunctionCall(
            env_type="user",
            func_name="acknowledge_instructions",
            arguments={"instruction_type": "pre_surgery"}
        )
    ]


def init_medication_instructions(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Medication instructions need acknowledgment."""
    # Add post_care and pre_surgery but not medication (missing medication)
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="acknowledge_instructions",
            arguments={"instruction_type": "post_care"}
        ),
        EnvFunctionCall(
            env_type="user",
            func_name="acknowledge_instructions",
            arguments={"instruction_type": "pre_surgery"}
        )
    ]


def init_post_care_instructions(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Post-care instructions need acknowledgment."""
    # Add medication and pre_surgery but not post_care (missing post_care)
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="acknowledge_instructions",
            arguments={"instruction_type": "medication"}
        ),
        EnvFunctionCall(
            env_type="user",
            func_name="acknowledge_instructions",
            arguments={"instruction_type": "pre_surgery"}
        )
    ]


def init_pre_surgery_instructions(env: HealthcareEnvironment) -> list[EnvFunctionCall]:
    """Pre-surgery instructions need acknowledgment."""
    # Add medication and post_care but not pre_surgery (missing pre_surgery)
    return [
        EnvFunctionCall(
            env_type="user",
            func_name="acknowledge_instructions",
            arguments={"instruction_type": "medication"}
        ),
        EnvFunctionCall(
            env_type="user",
            func_name="acknowledge_instructions",
            arguments={"instruction_type": "post_care"}
        )
    ]


def fix_acknowledge_medication(env: HealthcareEnvironment) -> list[ToolCall]:
    """Acknowledge medication instructions."""
    return [
        ToolCall(
            requestor="user",
            name="acknowledge_instructions",
            arguments={
                "instruction_type": "medication"
            }
        )
    ]


def fix_acknowledge_post_care(env: HealthcareEnvironment) -> list[ToolCall]:
    """Acknowledge post-care instructions."""
    return [
        ToolCall(
            requestor="user",
            name="acknowledge_instructions",
            arguments={
                "instruction_type": "post_care"
            }
        )
    ]


def fix_acknowledge_pre_surgery(env: HealthcareEnvironment) -> list[ToolCall]:
    """Acknowledge pre-surgery instructions."""
    return [
        ToolCall(
            requestor="user",
            name="acknowledge_instructions",
            arguments={
                "instruction_type": "pre_surgery"
            }
        )
    ]


# ============================================================================
# Base Tasks for SelectionSet 14: consent_issues
# ============================================================================

consent_not_required_task = BaseTask(
    name="not_required",
    description="No consent required (baseline)",
    init_funcs=[],  # Baseline - fresh environment is already in good state
    fix_funcs=[],
)

telehealth_consent_needed_task = BaseTask(
    name="telehealth_consent_needed",
    description="Telehealth consent required",
    init_funcs=[init_telehealth_consent_needed],
    fix_funcs=[fix_obtain_telehealth_consent],
)

data_sharing_consent_needed_task = BaseTask(
    name="data_sharing_consent_needed",
    description="Data sharing consent required",
    init_funcs=[init_data_sharing_consent_needed],
    fix_funcs=[fix_obtain_data_sharing_consent],
)

# ============================================================================
# Base Tasks for SelectionSet 15: emergency_contact_issues
# ============================================================================

emergency_contact_current_task = BaseTask(
    name="current",
    description="Emergency contact current and on file (baseline)",
    init_funcs=[],  # Baseline - fresh environment is already in good state
    fix_funcs=[],
)

emergency_contact_missing_task = BaseTask(
    name="missing",
    description="No emergency contact on file",
    init_funcs=[init_emergency_contact_missing],
    fix_funcs=[fix_update_emergency_contact],
)

emergency_contact_outdated_task = BaseTask(
    name="outdated",
    description="Emergency contact information outdated",
    init_funcs=[init_emergency_contact_outdated],
    fix_funcs=[fix_update_emergency_contact],
)

# ============================================================================
# Base Tasks for SelectionSet 16: instruction_acknowledgment_issues
# ============================================================================

no_instructions_needed_task = BaseTask(
    name="no_instructions_needed",
    description="No special instructions required (baseline)",
    init_funcs=[],  # Baseline - fresh environment is already in good state
    fix_funcs=[],
)

medication_instructions_task = BaseTask(
    name="medication_instructions",
    description="Medication instructions need acknowledgment",
    init_funcs=[init_medication_instructions],
    fix_funcs=[fix_acknowledge_medication],
)

post_care_instructions_task = BaseTask(
    name="post_care_instructions",
    description="Post-care instructions need acknowledgment",
    init_funcs=[init_post_care_instructions],
    fix_funcs=[fix_acknowledge_post_care],
)

pre_surgery_instructions_task = BaseTask(
    name="pre_surgery_instructions",
    description="Pre-surgery instructions need acknowledgment",
    init_funcs=[init_pre_surgery_instructions],
    fix_funcs=[fix_acknowledge_pre_surgery],
)

# ============================================================================
# SelectionSets
# ============================================================================

consent_issues = SelectionSet(
    tasks=[
        consent_not_required_task,
        telehealth_consent_needed_task,
        data_sharing_consent_needed_task,
    ]
)

emergency_contact_issues = SelectionSet(
    tasks=[
        emergency_contact_current_task,
        emergency_contact_missing_task,
        emergency_contact_outdated_task,
    ]
)

instruction_acknowledgment_issues = SelectionSet(
    tasks=[
        no_instructions_needed_task,
        medication_instructions_task,
        post_care_instructions_task,
        pre_surgery_instructions_task,
    ]
)

telehealth_setup_selection_sets = [
    consent_issues,
    emergency_contact_issues,
    instruction_acknowledgment_issues,
]


# ============================================================================
