# Copyright Sierra
from pathlib import Path
from typing import Optional, cast

from tau2.data_model.tasks import Task
from tau2.domains.healthcare.data_model import HealthcareDB
from tau2.domains.healthcare.tools import HealthcareTools
from tau2.domains.healthcare.user_data_model import HealthcareUserDB
from tau2.domains.healthcare.user_tools import HealthcareUserTools
from tau2.domains.healthcare.utils import (
    HEALTHCARE_DB_PATH,
    HEALTHCARE_POLICY_PATH,
    HEALTHCARE_TASK_SET_PATH,
    HEALTHCARE_USER_DB_PATH,
)
from tau2.environment.environment import Environment
from tau2.utils import load_file


class HealthcareEnvironment(Environment):
    """
    Healthcare environment with bidirectional tool support.
    Syncs agent-side and patient-side information.
    """
    tools: HealthcareTools
    user_tools: HealthcareUserTools

    def __init__(
        self,
        domain_name: str,
        policy: str,
        tools: HealthcareTools,
        user_tools: HealthcareUserTools,
    ):
        super().__init__(domain_name, policy, tools, user_tools)

    def make_tool_call(self, tool_name: str, requestor: str = "assistant", **kwargs):
        """
        Override to track assistant tool calls in real-time for behavioral assertions.
        """
        # Track assistant tool calls before execution
        if requestor == "assistant":
            self.tools.db.tool_call_history.append(tool_name)

        # Execute the tool call via parent class
        return super().make_tool_call(tool_name, requestor, **kwargs)

    def set_state(self, initialization_data, initialization_actions, message_history):
        """
        Override to track tool calls for behavioral assertions.
        """
        # First, let parent class do the standard state replay
        super().set_state(initialization_data, initialization_actions, message_history)

        # Then extract and store tool call history in the database
        from tau2.data_model.message import AssistantMessage, UserMessage

        tool_calls = []
        for message in message_history:
            if isinstance(message, (AssistantMessage, UserMessage)) and message.is_tool_call():
                for tc in message.tool_calls:
                    # Only track assistant tool calls for protocol validation
                    if tc.requestor == "assistant":
                        tool_calls.append(tc.name)

        # Store in database for assertion functions to access
        self.tools.db.tool_call_history = tool_calls

    def sync_tools(self):
        """
        Sync the agent tools with the patient's user tools.
        This ensures consistency between what the patient has access to
        and what the agent's system shows.

        Examples of syncing:
        - If patient makes payment via user tool, update payment records
        - Keep patient info consistent between agent and user views
        """
        # Get patient ID from user surroundings
        patient_id = self.user_tools.surroundings.patient_id

        # Verify patient exists in agent database
        if patient_id not in self.tools.db.patients:
            # This is a scenario setup issue, not a runtime error
            return

        patient = self.tools.db.patients[patient_id]

        # Sync identity information (ensure consistency)
        # The patient's insurance card should match what's in the system
        user_insurance = self.user_tools.device.insurance_card
        system_insurance = patient.insurance

        # In a real system, we might want to validate these match
        # For now, we assume they're set up consistently in the task data

        # Sync portal information if patient has accessed it
        if self.user_tools.device.portal_info:
            portal = self.user_tools.device.portal_info

            # Update upcoming appointments in portal view
            upcoming_apts = []
            for apt_id in patient.appointment_ids:
                if apt_id in self.tools.db.appointments:
                    apt = self.tools.db.appointments[apt_id]
                    if apt.status == "scheduled":
                        upcoming_apts.append(
                            f"{apt.date} at {apt.time} - {apt.appointment_type} with Dr. {self.tools.db.doctors[apt.doctor_id].name.last_name}"
                        )

            # Keep only most recent 3 appointments
            portal.upcoming_appointments = upcoming_apts[:3]

            # Update outstanding balance
            total_balance = 0
            for payment in self.tools.db.payments.values():
                if payment.patient_id == patient_id:
                    # In a real system, this would calculate unpaid balances
                    # For simplicity, we'll just show 0 for now
                    pass
            portal.outstanding_balance = total_balance


def get_environment(
    db: Optional[HealthcareDB] = None,
    user_db: Optional[HealthcareUserDB] = None,
    solo_mode: bool = False,
) -> HealthcareEnvironment:
    """
    Create a healthcare environment instance.

    Args:
        db: Optional agent-side database. If None, loads from default path.
        user_db: Optional user-side database. If None, loads from default path.
        solo_mode: Whether to run in solo mode (no user interaction)

    Returns:
        Configured HealthcareEnvironment instance
    """
    # Load databases
    if db is None:
        db = cast(HealthcareDB, HealthcareDB.load(str(HEALTHCARE_DB_PATH)))

    tools = HealthcareTools(db)

    # User tools only needed in normal mode (not solo)
    if not solo_mode:
        if user_db is None:
            # Load default user_db
            user_db = cast(HealthcareUserDB, HealthcareUserDB.load(str(HEALTHCARE_USER_DB_PATH)))
        user_tools = HealthcareUserTools(user_db)
    else:
        # Solo mode not yet implemented for healthcare
        # Would need to be implemented similar to airline/retail solo modes
        raise ValueError("Healthcare domain does not yet support solo mode")

    # Load policy
    with open(HEALTHCARE_POLICY_PATH, "r") as fp:
        policy = fp.read()

    # Create environment
    env = HealthcareEnvironment(
        domain_name="healthcare",
        policy=policy,
        tools=tools,
        user_tools=user_tools,
    )

    return env


def get_tasks(task_split_name: Optional[str] = "base") -> list[Task]:
    """
    Load healthcare tasks from the task file.

    Args:
        task_split_name: Optional task split name. Currently only "base" is supported.

    Returns:
        List of Task objects
    """
    tasks = load_file(HEALTHCARE_TASK_SET_PATH)
    tasks = [Task.model_validate(task) for task in tasks]

    if task_split_name is None:
        return tasks

    # For now, we only have one split
    # In the future, could add train/val/test splits
    if task_split_name != "base":
        raise ValueError(
            f"Invalid task split name: {task_split_name}. Currently only 'base' is supported."
        )

    return tasks
