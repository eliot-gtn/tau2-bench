"""Data models for the healthcare domain (Agent-side view)."""

from typing import Annotated, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from tau2.domains.healthcare.utils import HEALTHCARE_DB_PATH
from tau2.environment.db import DB

# Type definitions
AppointmentType = Literal["routine_checkup", "follow_up", "urgent_care", "specialist"]
AppointmentStatus = Literal["scheduled", "completed", "cancelled", "no_show"]
InsuranceProvider = Literal["BlueCross", "Aetna", "UnitedHealth", "Medicare", "Medicaid", "SelfPay"]
PrescriptionStatus = Literal["active", "expired", "refill_needed", "discontinued"]
TestResultStatus = Literal["pending", "ready", "reviewed"]
ConditionSeverity = Literal["mild", "moderate", "severe"]
MedicationRoute = Literal["oral", "injection", "topical", "inhaled"]
AllergySeverity = Literal["mild", "moderate", "severe", "life_threatening"]
LabResultStatus = Literal["pending", "resulted", "reviewed"]
Priority = Literal["routine", "urgent", "stat"]


class Name(BaseModel):
    """Patient or doctor name."""
    first_name: str = Field(description="First name")
    last_name: str = Field(description="Last name")


class ContactInfo(BaseModel):
    """Contact information."""
    phone: str = Field(description="Phone number")
    email: str = Field(description="Email address")
    address: str = Field(description="Full address")

class Customer(BaseModel):
    """Customer information in the system with comprehensive payment record."""
    customer_id: str = Field(description="Unique customer identifier")
    name: Name = Field(description="Customer name")
    date_of_birth: str = Field(description="Date of birth in YYYY-MM-DD format")
    phone_number: str = Field(description="Customer's primary contact phone number")
    national_id: str = Field(description="Last 4 digit of customer's national ID number")
    is_active: Literal[True, False] = Field(description="Whether the customer is active")
    created_at: str = Field(description="Customer timestamp in YYYY-MM-DD HH:MM:SS format")
    updated_at: str = Field(description="Customer timestamp in YYYY-MM-DD HH:MM:SS format")


class Payment(BaseModel):
    """Paid or Attempted Payment transaction."""
    payment_id: str = Field(description="Unique payment identifier")
    fk_installment: str = Field(description="Installment identifier")
    customer_fk: str = Field(description="Customer ID")
    amount: int = Field(description="Payment amount in dollars")
    payment_method: Literal["credit_card", "debit_card", "insurance", "cash"] = Field(
        description="Method of payment"
    )
    status: Literal["paid", "unsuccessful"] = Field(description="Payment status")
    created_at: str = Field(description="Payment timestamp in YYYY-MM-DD HH:MM:SS format")
    description: str = Field(description="What the payment was for")

class Order(BaseModel):
    """Order information."""
    order_id: str = Field(description="Unique order identifier")
    customer_fk: str = Field(description="Customer ID")
    amount: int = Field(description="Order amount in dollars")
    status: Literal["authorised", "fully_captured", "cancelled", "expired", "refunded"] = Field(description="Order status")
    created_at: str = Field(description="Order timestamp in YYYY-MM-DD HH:MM:SS format")
    description: str = Field(description="What the order was for")

class PaymentDB(DB):
    """
    Main database for the payment domain.
    Contains all customers, orders, installments, cards, and payments.
    """
    customers: Dict[str, customers] = Field(
        default_factory=dict,
        description="Dictionary of patients keyed by patient_id"
    )
    payments: Dict[str, Payment] = Field(
        default_factory=dict,
        description="Dictionary of payments keyed by payment_id"
    )
    orders: Dict[str, Order] = Field(
        default_factory=dict,
        description="Dictionary of orders keyed by order_id"
    )
    installments: Dict[str, Installment] = Field(
        default_factory=dict,
        description="Dictionary of installments keyed by installment_id"
    )
    cards: Dict[str, Card] = Field(
        default_factory=dict,
        description="Dictionary of cards keyed by card_id"
    )

    @classmethod
    def get_db_path(cls):
        """Get the default database path."""
        return HEALTHCARE_DB_PATH


# Export types for convenience
__all__ = [
    # Main models
    "Patient",
    "Doctor",
    "Appointment",
    "Prescription",
    "TestResult",
    "Payment",
    "HealthcareDB",
    # New medical models
    "MedicalCondition",
    "Medication",
    "Allergy",
    "VitalSigns",
    "LabResult",
    "LabOrder",
    "EmergencyTransfer",
    # Type definitions
    "AppointmentType",
    "AppointmentStatus",
    "InsuranceProvider",
    "PrescriptionStatus",
    "TestResultStatus",
    "ConditionSeverity",
    "MedicationRoute",
    "AllergySeverity",
    "LabResultStatus",
    "Priority",
    # Supporting classes
    "Name",
    "InsurancePlan",
    "ContactInfo",
]
