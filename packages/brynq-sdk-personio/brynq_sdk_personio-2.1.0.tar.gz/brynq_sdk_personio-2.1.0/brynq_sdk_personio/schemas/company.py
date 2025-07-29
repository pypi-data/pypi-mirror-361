# Auto-generated Pandera schemas from dump.json

import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Int, Float, Bool
from typing import Any

try:
    from brynq_sdk_functions import BrynQPanderaDataFrameModel
except ImportError:
    class BrynQPanderaDataFrameModel(pa.DataFrameModel):
        pass

class LegalEntitiesGet(BrynQPanderaDataFrameModel):
    id: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Unique identifier for the legal entity", alias="id")
    status: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Current status of the legal entity", alias="status")
    is_main: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=False, description="Indicates if this is the main legal entity", alias="is_main")
    valid_from: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Date from which the legal entity is valid", alias="valid_from")
    assigned_employees: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="JSON string containing IDs of assigned employees", alias="assigned_employees")
    country: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Country where the legal entity is registered", alias="country")
    name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Name of the legal entity", alias="name")
    type: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Type of legal entity", alias="type")
    registration_number: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Official registration number of the legal entity", alias="registration_number")
    industry_sector: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Industry sector the legal entity operates in", alias="industry_sector")
    email: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Contact email for the legal entity", alias="email")
    phone: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Contact phone number for the legal entity", alias="phone")
    address: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="JSON string containing the legal entity's address", alias="address")
    contact_person: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="ID of the contact person for the legal entity", alias="contact_person")
    bank_details: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="JSON string containing bank account details", alias="bank_details")
    mailing_address: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="JSON string containing the mailing address", alias="mailing_address")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "contact_person": {
                "parent_schema": "PersonGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }


class OrgUnitsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Unique identifier for the organizational unit", alias="id")
    name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Name of the organizational unit", alias="name")
    type: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Type of organizational unit", alias="type")
    abbreviation: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Abbreviation or short code for the organizational unit", alias="abbreviation")
    description: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Description of the organizational unit", alias="description")
    resource_uri: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Resource URI for accessing the organizational unit", alias="resource_uri")
    create_time: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Timestamp when the organizational unit was created", alias="create_time")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {}  # OrgUnitsGet is a reference entity with no foreign keys


class CostCentersGet(BrynQPanderaDataFrameModel):
    id: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Unique identifier for the cost center", alias="id")
    name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Name of the cost center", alias="name")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {}  # CostCentersGet is a reference entity with no foreign keys
