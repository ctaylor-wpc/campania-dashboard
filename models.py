"""
models.py

Core data model for Campania Order Dashboard.

This defines a single source of truth for:
- Order structure
- Default values
- Serialization helpers
"""

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional
import uuid

import config


# =====================================================
# HELPERS
# =====================================================

def now_timestamp() -> str:
    """Return consistent timestamp string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def generate_request_id(last_id: Optional[str] = None) -> str:
    """
    Generate sequential request IDs.

    Format:
    CAM-0001
    CAM-0002
    """
    if not last_id:
        return "CAM-0001"

    try:
        number = int(last_id.split("-")[1])
        return f"CAM-{number + 1:04d}"
    except Exception:
        return f"CAM-{uuid.uuid4().hex[:4].upper()}"


# =====================================================
# ORDER MODEL
# =====================================================

@dataclass
class CampaniaOrder:
    """
    Core order object used throughout the application.
    """

    # -------------------------
    # SYSTEM FIELDS
    # -------------------------
    request_id: str
    created_timestamp: str
    last_modified_timestamp: str
    created_by: str
    last_modified_by: str

    # -------------------------
    # CUSTOMER INFO
    # -------------------------
    customer_name: str
    customer_phone: str
    customer_email: str = ""

    street_address: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""

    # -------------------------
    # ORDER INFO
    # -------------------------
    product_requested: str = ""
    campania_sku: str = ""
    quantity: int = 1
    notes: str = ""

    # -------------------------
    # FINANCIALS
    # -------------------------
    customer_price: float = 0.0
    campania_cost: float = 0.0
    deposit_amount: float = 0.0

    # -------------------------
    # DELIVERY
    # -------------------------
    delivery_required: bool = False
    delivery_cost: float = 0.0
    delivery_status: str = "Not Needed"

    # -------------------------
    # STATUS
    # -------------------------
    payment_status: str = "No Quote Provided"
    order_status: str = "Awaiting Quote"

    expected_arrival_date: str = ""

    # =====================================================
    # FACTORY METHODS
    # =====================================================

    @staticmethod
    def new(customer_name: str,
            customer_phone: str,
            created_by: str,
            product_requested: str = "",
            customer_email: str = "",
            notes: str = "") -> "CampaniaOrder":
        """
        Create a new order with defaults applied.
        """

        timestamp = now_timestamp()

        return CampaniaOrder(
            request_id="TEMP",  # replaced by database layer
            created_timestamp=timestamp,
            last_modified_timestamp=timestamp,
            created_by=created_by,
            last_modified_by=created_by,

            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            product_requested=product_requested,
            notes=notes
        )

    # =====================================================
    # SERIALIZATION
    # =====================================================

    def to_dict(self) -> dict:
        """
        Convert model to dictionary for Google Sheets.
        """
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "CampaniaOrder":
        """
        Convert Google Sheet row to model.
        """
        return CampaniaOrder(
            request_id=data.get("Request ID", ""),
            created_timestamp=data.get("Created Timestamp", ""),
            last_modified_timestamp=data.get("Last Modified Timestamp", ""),
            created_by=data.get("Created By", ""),
            last_modified_by=data.get("Last Modified By", ""),

            customer_name=data.get("Customer Name", ""),
            customer_phone=data.get("Customer Phone", ""),
            customer_email=data.get("Customer Email", ""),

            street_address=data.get("Street Address", ""),
            city=data.get("City", ""),
            state=data.get("State", ""),
            zip_code=data.get("Zip Code", ""),

            product_requested=data.get("Product Requested", ""),
            campania_sku=data.get("Campania SKU", ""),
            quantity=int(data.get("Quantity") or 1),
            notes=data.get("Notes", ""),

            customer_price=float(data.get("Customer Price") or 0),
            campania_cost=float(data.get("Campania Cost") or 0),
            deposit_amount=float(data.get("Deposit Amount") or 0),

            delivery_required=str(data.get("Delivery Required", "False")).lower() == "true",
            delivery_cost=float(data.get("Delivery Cost") or 0),
            delivery_status=data.get("Delivery Status", "Not Needed"),

            payment_status=data.get("Payment Status", "No Quote Provided"),
            order_status=data.get("Order Status", "Awaiting Quote"),

            expected_arrival_date=data.get("Expected Arrival Date", "")
        )