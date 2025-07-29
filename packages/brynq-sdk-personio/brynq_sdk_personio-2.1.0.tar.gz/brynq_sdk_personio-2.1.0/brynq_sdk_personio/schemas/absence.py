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

class AbsenscePeriodGet(BrynQPanderaDataFrameModel):
    id: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Unique identifier for the absence period", alias="id")
    person: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="ID of the person taking the absence", alias="person")
    starts_from: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Start date and time of the absence", alias="starts_from")
    ends_at: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="End date and time of the absence", alias="ends_at")
    timezone_id: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Timezone identifier for the absence period", alias="timezone_id")
    absence_type: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="ID of the absence type", alias="absence_type")
    approval: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="JSON string containing approval details", alias="approval")
    created_at: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Timestamp when the absence record was created", alias="created_at")
    updated_at: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Timestamp when the absence record was last updated", alias="updated_at")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "person": {
                "parent_schema": "PersonGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "absence_type": {
                "parent_schema": "AbsenceTypeGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }


class AbsenceTypeGet(BrynQPanderaDataFrameModel):
    id: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Unique identifier for the absence type", alias="id")
    name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Name of the absence type", alias="name")
    category: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Category of the absence type", alias="category")
    unit: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=False, description="Unit of measurement for this absence type (days, hours, etc.)", alias="unit")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {}  # AbsenceTypeGet is a reference entity with no foreign keys
