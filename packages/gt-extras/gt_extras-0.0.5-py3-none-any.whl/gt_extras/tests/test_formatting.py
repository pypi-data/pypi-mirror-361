import numpy as np
import pandas as pd
import polars as pl
import pyarrow as pa
import pytest
from great_tables import GT

from gt_extras.formatting import fmt_pct_extra, gt_duplicate_column
from gt_extras.tests.conftest import assert_rendered_body


def test_fmt_pct_extra_snap(snapshot, mini_gt):
    res = fmt_pct_extra(mini_gt, columns="num", scale=1, decimals=0)
    assert_rendered_body(snapshot, gt=res)


def test_fmt_pct_extra_basic(mini_gt):
    html = fmt_pct_extra(mini_gt, columns="num", scale=1).as_raw_html()

    assert "<span style='color:grey;'><1%</span>" in html
    assert "2.2%" in html
    assert "33.3%" in html


def test_fmt_pct_extra_threshold_low(mini_gt):
    html = fmt_pct_extra(mini_gt, columns="num", scale=100, threshold=10).as_raw_html()

    assert "11.1%" in html
    assert "222.2%" in html
    assert "3333.0%" in html


def test_fmt_pct_extra_threshold_high(mini_gt):
    html = fmt_pct_extra(
        mini_gt, columns="num", scale=100, threshold=4000
    ).as_raw_html()

    assert html.count("<span style='color:grey;'><4000%</span>") == 3


def test_fmt_pct_extra_custom_color(mini_gt):
    html = fmt_pct_extra(
        mini_gt, columns="num", color="red", threshold=50
    ).as_raw_html()

    assert html.count("<span style='color:red;'><50%</span>") == 1


def test_fmt_pct_extra_decimals(mini_gt):
    html_0 = fmt_pct_extra(mini_gt, columns="num", decimals=0).as_raw_html()
    assert "11%" in html_0  # 0.1111 * 100 = 11.11% rounded
    assert "222%" in html_0


def test_fmt_pct_extra_negative_values():
    df = pd.DataFrame({"num": [-0.005, -0.25, 0.15]})
    gt_test = GT(df)

    html = fmt_pct_extra(gt=gt_test, columns="num", threshold=1.0).as_raw_html()

    assert "<span style='color:grey;'><1%</span>" in html
    assert "-25.0%" in html
    assert "15.0%" in html


def test_fmt_pct_extra_zero_values():
    df = pd.DataFrame({"num": [0.0, 0.005, 0.02]})
    gt_test = GT(df)
    html = fmt_pct_extra(gt=gt_test, columns="num").as_raw_html()

    assert html.count("<span style='color:grey;'><1%</span>") == 2
    assert "2.0%" in html


def test_fmt_pct_extra_edge_case_threshold():
    df = pd.DataFrame({"num": [0.01, 0.0099, 0.0101]})
    gt_test = GT(df)

    html = fmt_pct_extra(
        gt=gt_test, columns="num", scale=100, threshold=1.0, decimals=2
    ).as_raw_html()

    assert "1.00%" in html
    assert "<span style='color:grey;'><1%</span>" in html
    assert "1.01%" in html


def test_fmt_pct_extra_with_none_values():
    df = pd.DataFrame({"num": [0.005, None, 0.25, np.nan]})
    gt_test = GT(df)

    result = fmt_pct_extra(gt=gt_test, columns="num")
    html = result.as_raw_html()

    assert isinstance(result, GT)
    assert "25%" in html


def test_gt_duplicate_column_snap(snapshot, mini_gt):
    res = gt_duplicate_column(mini_gt, column="num")
    assert_rendered_body(snapshot, gt=res)


def test_gt_duplicate_column_basic(mini_gt):
    res = gt_duplicate_column(mini_gt, column="num", append_text="_copy")
    html = res.as_raw_html()

    assert "num_copy" in res._tbl_data.columns
    assert "num_copy" in html
    assert all(res._tbl_data["num"] == res._tbl_data["num_copy"])


def test_gt_duplicate_column_custom_name(mini_gt):
    res = gt_duplicate_column(mini_gt, column="num", dupe_name="duplicated_num")
    html = res.as_raw_html()

    assert "duplicated_num" in res._tbl_data.columns
    assert "duplicated_num" in html
    assert all(res._tbl_data["num"] == res._tbl_data["duplicated_num"])


def test_gt_duplicate_column_position(mini_gt):
    res = gt_duplicate_column(mini_gt, column="num", after="char")
    html = res.as_raw_html()

    assert "num_dupe" in res._tbl_data.columns
    assert "num_dupe" in html

    columns = list(res._boxhead)
    assert columns[2].column_label == "num_dupe"


def test_gt_duplicate_column_polars():
    df = pl.DataFrame({"num": [1, 2, 3], "char": ["a", "b", "c"]})
    gt_test = GT(df)

    res = gt_duplicate_column(gt_test, column="num", append_text="_copy")
    html = res.as_raw_html()

    assert "num_copy" in res._tbl_data.columns
    assert "num_copy" in html

    original_values = res._tbl_data.get_column("num").to_list()
    duplicated_values = res._tbl_data.get_column("num_copy").to_list()
    assert original_values == duplicated_values


def test_gt_duplicate_column_invalid_type():
    data = pa.table({"num": [1, 2, 3], "char": ["a", "b", "c"]})
    gt_test = GT(data)

    with pytest.raises(TypeError, match="Unsupported type"):
        gt_duplicate_column(gt_test, column="num")


def test_gt_duplicate_column_invalid_name(mini_gt):
    with pytest.raises(
        ValueError, match="cannot be the same as the original column name"
    ):
        gt_duplicate_column(mini_gt, column="num", dupe_name="num")
