from collections.abc import Callable
from pathlib import Path
from typing import Any, TYPE_CHECKING

import pytest

from hope_smart_import.readers import open_csv, open_xls, open_xls_multi, SheetNotError

if TYPE_CHECKING:
    from hope_smart_import.types import ValueMapper


XLS_DATA = [
    [{"gender": "M", "last_name": "Doe", "name": "John"}, {"gender": "F", "last_name": "Doe", "name": "Jane"}],
    [{"gender": "m", "last_name": "Doe1", "name": "John1"}, {"gender": "f", "last_name": "Doe1", "name": "Jane1"}],
]


@pytest.fixture
def xls() -> str:
    return str((Path(__file__).parent / "data" / "r1.xlsx").absolute())


@pytest.fixture
def csv() -> str:
    return str((Path(__file__).parent / "data" / "r1.csv").absolute())


@pytest.mark.parametrize("start_at", [0, 1])
def test_read_csv_headers(csv: str, start_at: int) -> None:
    for e in open_csv(csv, start_at_row=start_at, has_header=True):
        assert list(e.keys()) == ["name", "last_name", "gender"]


@pytest.mark.parametrize("start_at", [0, 1])
def test_read_csv_no_headers(csv: str, start_at: int) -> None:
    for e in open_csv(csv, start_at_row=start_at, has_header=False):
        assert list(e.keys()) == ["column1", "column2", "column3"]


@pytest.mark.parametrize(("mapper", "validator"), [(str.upper, str.isupper), (str.lower, str.islower)])
def test_read_csv_value_mapper(csv: str, mapper: "ValueMapper", validator: Callable[[Any], bool]) -> None:
    for row in open_csv(csv, has_header=True, value_mapper=mapper):
        assert all(map(validator, row.values()))


@pytest.mark.parametrize("start_at", [0, 1])
def test_read_xls_headers(xls: str, start_at: int) -> None:
    for e in open_xls(xls, start_at_row=start_at):
        assert list(e.keys()) == ["name", "last_name", "gender"]


@pytest.mark.parametrize("start_at", [0, 1])
def test_read_xls_no_headers(xls: str, start_at: int) -> None:
    for e in open_xls(xls, start_at_row=start_at, has_header=False):
        assert list(e.keys()) == ["column1", "column2", "column3"]


@pytest.mark.parametrize(("mapper", "validator"), [(str.upper, str.isupper), (str.lower, str.islower)])
def test_read_xls_value_mapper(xls: str, mapper: "ValueMapper", validator: Callable[[Any], bool]) -> None:
    for row in open_xls(xls, has_header=True, value_mapper=mapper):
        assert all(map(validator, row.values()))


@pytest.mark.parametrize("sheet_to_read_args", [{}, {"index_or_name": 0}, {"index_or_name": "f1"}])
def test_read_xls_sheet_to_read_args(xls: str, sheet_to_read_args: dict[str, int] | dict[str, str]) -> None:
    assert list(open_xls(xls, **sheet_to_read_args)) == XLS_DATA[0]


def test_read_xls_invalid_sheet_index(xls: str) -> None:
    with pytest.raises(SheetNotError):
        list(open_xls(xls, index_or_name=42))


def test_read_xls_invalid_sheet_name(xls: str) -> None:
    with pytest.raises(SheetNotError):
        list(open_xls(xls, index_or_name="foo"))


def test_read_xls_invalid_sheet_arg_type(xls: str) -> None:
    with pytest.raises(SheetNotError):
        list(open_xls(xls, index_or_name=object()))


@pytest.mark.parametrize("start_at", [0, 1])
def test_read_multi_xls_headers(xls: str, start_at: int) -> None:
    ret = []
    for e, sh in open_xls_multi(xls, indices_or_names=[0, 1], start_at_row=start_at, has_header=True):
        ret.extend([(e, row) for row in sh])
    if start_at == 0:
        # Sheet 0 - Row 0
        assert ret[0] == (0, XLS_DATA[0][0])
        # Sheet 0 - Row 1
        assert ret[1] == (0, XLS_DATA[0][1])
        # Sheet 1 - Row 0
        assert ret[2] == (1, XLS_DATA[1][0])
        # Sheet 1 - Row 1
        assert ret[3] == (1, XLS_DATA[1][1])
    if start_at == 1:
        # Sheet 0 - Row 1
        assert ret[0] == (0, XLS_DATA[0][1])
        # Sheet 1 - Row 1
        assert ret[1] == (1, XLS_DATA[1][1])


@pytest.mark.parametrize(("mapper", "validator"), [(str.upper, str.isupper), (str.lower, str.islower)])
def test_read_multi_xls_value_mapper(xls: str, mapper: "ValueMapper", validator: Callable[[Any], bool]) -> None:
    for _, sheet in open_xls_multi(xls, indices_or_names=[0, 1], has_header=True, value_mapper=mapper):
        for row in sheet:
            assert all(map(validator, row.values()))


@pytest.mark.parametrize("sheets_to_read_args", [{}, {"indices_or_names": [0]}, {"indices_or_names": ["f1"]}])
def test_read_multi_xls_sheet_to_read_args(
    xls: str, sheets_to_read_args: dict[str, list[int]] | dict[str, list[str]]
) -> None:
    assert [list(sheet) for i, sheet in open_xls_multi(xls, **sheets_to_read_args)] == [XLS_DATA[0]]


def test_read_multi_xls_invalid_sheet_index(xls: str) -> None:
    with pytest.raises(SheetNotError):
        list(open_xls_multi(xls, indices_or_names=[42]))


def test_read_multi_xls_invalid_sheet_name(xls: str) -> None:
    with pytest.raises(SheetNotError):
        list(open_xls_multi(xls, indices_or_names=["foo"]))
