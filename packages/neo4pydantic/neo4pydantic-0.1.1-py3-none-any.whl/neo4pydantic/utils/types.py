"""
Neo4j to Python type converters for Pydantic models
"""

from datetime import datetime, date, time
from typing import Dict, Callable, Type
import neo4j.time
import neo4j.graph

neo4j_type_convertor: Dict[Type, Callable] = {
    # Neo4j temporal types
    neo4j.time.DateTime: lambda v: datetime(
        year=v.year,
        month=v.month,
        day=v.day,
        hour=v.hour,
        minute=v.minute,
        second=v.second,
        microsecond=v.nanosecond,
    ),
    neo4j.time.Date: lambda v: date(year=v.year, month=v.month, day=v.day),
    neo4j.time.Time: lambda v: time(
        hour=v.hour, minute=v.minute, second=v.second, microsecond=v.nanosecond
    ),
}
