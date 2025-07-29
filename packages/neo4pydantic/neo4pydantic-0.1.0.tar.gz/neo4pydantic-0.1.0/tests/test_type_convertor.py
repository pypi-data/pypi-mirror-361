from datetime import datetime, date, time, timedelta
from neo4pydantic.core import custom_pydantic_base_model
from neo4j import time as neo4jtime


class DummyModel(custom_pydantic_base_model.CustomBaseModel):
    dt: datetime = None
    d: date = None
    t: time = None
    td: timedelta = None
    point: dict = None
    node: dict = None
    rel: dict = None


def test_datetime_conversion():
    neo4j_dt = neo4jtime.DateTime(2023, 5, 6, 12, 30, 45, 123456)
    data = {"dt": neo4j_dt}
    result = DummyModel.model_validate(data)
    assert isinstance(result.dt, datetime)
    assert result.dt.year == 2023 and result.dt.hour == 12


def test_date_conversion():
    neo4j_date = neo4jtime.Date(2022, 1, 2)
    data = {"d": neo4j_date}
    result = DummyModel.model_validate(data)
    assert isinstance(result.d, date)
    assert result.d.month == 1


def test_time_conversion():
    neo4j_time = neo4jtime.Time(8, 15, 0, 123)
    data = {"t": neo4j_time}
    result = DummyModel.model_validate(data)
    assert isinstance(result.t, time)
    assert result.t.hour == 8
