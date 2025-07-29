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

class CompensationGet(BrynQPanderaDataFrameModel):
    id: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Unique identifier for the compensation record", alias="id")
    person: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="ID of the person receiving this compensation", alias="person")
    legal_entity: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="ID of the legal entity providing the compensation", alias="legal_entity")
    type: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Type of compensation (salary, bonus, etc.)", alias="type")
    amount: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Compensation amount", alias="amount")
    interval: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Payment interval (monthly, yearly, etc.)", alias="interval")
    effective_from: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Date from which this compensation is effective", alias="effective_from")
    weekly_working_hours: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Number of hours worked per week for this compensation", alias="weekly_working_hours")
    full_time_weekly_working_hours: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Standard full-time hours per week", alias="full_time_weekly_working_hours")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "person": {
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
