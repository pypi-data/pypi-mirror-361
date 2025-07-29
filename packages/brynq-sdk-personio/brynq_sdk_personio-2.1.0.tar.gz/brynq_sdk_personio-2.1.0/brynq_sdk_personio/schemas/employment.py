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

class EmploymentsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Unique identifier for the employment record", alias="id")
    status: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Current status of the employment", alias="status")
    weekly_working_hours: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Number of hours worked per week", alias="weekly_working_hours")
    probation_end_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Date when probation period ends", alias="probation_end_date")
    employment_start_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Date when employment started", alias="employment_start_date")
    full_time_weekly_working_hours: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Standard full-time hours per week", alias="full_time_weekly_working_hours")
    employment_end_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Date when employment ended (if applicable)", alias="employment_end_date")
    type: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Type of employment contract", alias="type")
    contract_end_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Date when contract ends", alias="contract_end_date")
    created_at: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Timestamp when the employment record was created", alias="created_at")
    updated_at: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Timestamp when the employment record was last updated", alias="updated_at")
    position: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Job position/title", alias="position")
    supervisor: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="ID of the person's supervisor", alias="supervisor")
    office: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Office location", alias="office")
    legal_entity: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="ID of the legal entity", alias="legal_entity")
    sub_company: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Sub-company identifier", alias="sub_company")
    org_units: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="JSON string containing organizational unit IDs", alias="org_units")
    cost_centers: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="JSON string containing cost center IDs", alias="cost_centers")
    person: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="ID of the person this employment belongs to", alias="person")
    termination: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="JSON string containing termination details", alias="termination")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "person": {
                "parent_schema": "PersonGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "supervisor": {
                "parent_schema": "PersonGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "legal_entity": {
                "parent_schema": "LegalEntitiesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }
