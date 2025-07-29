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

class PersonGet(BrynQPanderaDataFrameModel):
    id: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Unique identifier for the person", alias="id")
    email: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Person's email address", alias="email")
    created_at: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Timestamp when the person record was created", alias="created_at")
    updated_at: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Timestamp when the person record was last updated", alias="updated_at")
    first_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Person's first name", alias="first_name")
    last_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Person's last name", alias="last_name")
    preferred_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Person's preferred name for daily use", alias="preferred_name")
    gender: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Person's gender", alias="gender")
    status: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Current employment status of the person", alias="status")
    custom_attributes: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="JSON string containing custom attributes for the person", alias="custom_attributes")
    employments: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="JSON string containing employment records for the person", alias="employments")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {}  # PersonGet is a parent entity with no foreign keys to other entities
