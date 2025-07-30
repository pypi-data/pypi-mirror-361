from __future__ import annotations

from typing import override

from hypothesis import assume, given
from hypothesis.strategies import DrawFn, booleans, composite, lists, tuples
from polars import DataFrame, Int64, String, col
from utilities.hypothesis import int64s, text_ascii

from polars_subclasses.lib import DataFrameWithMetaData, SeriesWithMetaData


class SeriesWithBool(SeriesWithMetaData[bool, "DataFrameWithBool"]):
    @property
    @override
    def dataframe_with_metadata(self) -> type[DataFrameWithBool]:
        return DataFrameWithBool


class DataFrameWithBool(DataFrameWithMetaData[bool, "SeriesWithBool"]):
    @property
    @override
    def series_with_metadata(self) -> type[SeriesWithBool]:
        return SeriesWithBool


@composite
def dataframes_with_bool(draw: DrawFn, /) -> DataFrameWithBool:
    rows = draw(lists(tuples(int64s(), text_ascii())))
    bool_ = draw(booleans())
    return DataFrameWithBool(
        data=rows, schema={"x": Int64, "y": String}, orient="row", metadata=bool_
    )


class TestDataFrameWithMetaData:
    @given(df=dataframes_with_bool())
    def test_main(self, *, df: DataFrameWithBool) -> None:
        assert isinstance(df, DataFrameWithBool)
        assert isinstance(df, DataFrameWithMetaData)
        assert isinstance(df, DataFrame)

    @given(df=dataframes_with_bool())
    def test_drop(self, *, df: DataFrameWithBool) -> None:
        self._assert_dataframe(df.drop(), df)

    @given(df=dataframes_with_bool())
    def test_drop_nans(self, *, df: DataFrameWithBool) -> None:
        self._assert_dataframe(df.drop_nans(), df)

    @given(df=dataframes_with_bool())
    def test_drop_nulls(self, *, df: DataFrameWithBool) -> None:
        self._assert_dataframe(df.drop_nulls(), df)

    @given(df=dataframes_with_bool())
    def test_explode(self, *, df: DataFrameWithBool) -> None:
        self._assert_dataframe(
            df.group_by("x").agg(col("x").alias("xs")).explode("xs"), df
        )

    @given(df=dataframes_with_bool())
    def test_filter(self, *, df: DataFrameWithBool) -> None:
        self._assert_dataframe(df.filter(), df)

    @given(df=dataframes_with_bool())
    def test_head(self, *, df: DataFrameWithBool) -> None:
        self._assert_dataframe(df.head(), df)

    @given(df1=dataframes_with_bool(), df2=dataframes_with_bool())
    def test_join(self, *, df1: DataFrameWithBool, df2: DataFrameWithBool) -> None:
        self._assert_dataframe(df1.join(df2, on=["x"]), df1)

    @given(df=dataframes_with_bool())
    def test_rename(self, *, df: DataFrameWithBool) -> None:
        self._assert_dataframe(df.rename({"x": "x"}), df)

    @given(df=dataframes_with_bool())
    def test_reverse(self, *, df: DataFrameWithBool) -> None:
        self._assert_dataframe(df.reverse(), df)

    @given(df=dataframes_with_bool())
    def test_sample(self, *, df: DataFrameWithBool) -> None:
        _ = assume(not df.is_empty())
        self._assert_dataframe(df.sample(), df)

    @given(df=dataframes_with_bool())
    def test_select(self, *, df: DataFrameWithBool) -> None:
        self._assert_dataframe(df.select(), df)

    @given(bool_=booleans())
    def test_series_with_metadata(self, *, bool_: bool) -> None:
        assert (
            DataFrameWithMetaData(metadata=bool_).series_with_metadata
            is SeriesWithMetaData
        )

    @given(df=dataframes_with_bool())
    def test_shift(self, *, df: DataFrameWithBool) -> None:
        self._assert_dataframe(df.shift(), df)

    @given(df=dataframes_with_bool())
    def test_tail(self, *, df: DataFrameWithBool) -> None:
        self._assert_dataframe(df.tail(), df)

    @given(df=dataframes_with_bool())
    def test_to_series(self, *, df: DataFrameWithBool) -> None:
        self._assert_series(df.to_series(), df)

    @given(df=dataframes_with_bool())
    def test_with_columns(self, *, df: DataFrameWithBool) -> None:
        self._assert_dataframe(df.with_columns(), df)

    @given(df=dataframes_with_bool())
    def test_with_row_index(self, *, df: DataFrameWithBool) -> None:
        self._assert_dataframe(df.with_row_index(), df)

    def _assert_dataframe(
        self, result: DataFrameWithBool, df: DataFrameWithBool, /
    ) -> None:
        assert isinstance(result, DataFrameWithBool)
        assert result.metadata is df.metadata

    def _assert_series(self, result: SeriesWithBool, df: DataFrameWithBool, /) -> None:
        assert isinstance(result, SeriesWithBool)
        assert result.metadata is df.metadata


class TestSeriesWithMetaData:
    @given(bool_=booleans())
    def test_dataframe_with_metadata(self, *, bool_: bool) -> None:
        assert (
            SeriesWithMetaData(metadata=bool_).dataframe_with_metadata
            is DataFrameWithMetaData
        )
