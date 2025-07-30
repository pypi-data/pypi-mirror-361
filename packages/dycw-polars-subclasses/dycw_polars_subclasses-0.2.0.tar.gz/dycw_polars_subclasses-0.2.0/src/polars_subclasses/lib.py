from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self, cast, override

from polars import DataFrame, Expr, Series
from polars.dataframe.group_by import GroupBy
from polars.datatypes import N_INFER_DEFAULT

if TYPE_CHECKING:
    from collections.abc import Callable, Collection, Iterable, Mapping, Sequence

    from numpy import ndarray
    from polars._typing import (
        ColumnNameOrSelector,
        FrameInitTypes,
        IntoExpr,
        IntoExprColumn,
        JoinStrategy,
        JoinValidation,
        MaintainOrderJoin,
        Orientation,
        PolarsDataType,
        SchemaDefinition,
        SchemaDict,
    )
    from polars.series.series import ArrayLike


class SeriesWithMetaData[MD, DF: DataFrameWithMetaData](Series):
    @override
    def __init__(
        self,
        name: str | ArrayLike | None = None,
        values: ArrayLike | None = None,
        dtype: PolarsDataType | None = None,
        *,
        strict: bool = True,
        nan_to_null: bool = False,
        metadata: MD,
    ) -> None:
        super().__init__(name, values, dtype, strict=strict, nan_to_null=nan_to_null)
        self.metadata = metadata

    @property
    def dataframe_with_metadata(self) -> type[DF]:
        return cast("type[DF]", DataFrameWithMetaData)


class DataFrameWithMetaData[MD, SR: SeriesWithMetaData](DataFrame):
    @override
    def __init__(
        self,
        data: FrameInitTypes | None = None,
        schema: SchemaDefinition | None = None,
        *,
        schema_overrides: SchemaDict | None = None,
        strict: bool = True,
        orient: Orientation | None = None,
        infer_schema_length: int | None = N_INFER_DEFAULT,
        nan_to_null: bool = False,
        metadata: MD,
    ) -> None:
        super().__init__(
            data,
            schema,
            schema_overrides=schema_overrides,
            strict=strict,
            orient=orient,
            infer_schema_length=infer_schema_length,
            nan_to_null=nan_to_null,
        )
        self.metadata = metadata

    @override
    def drop(
        self,
        *columns: ColumnNameOrSelector | Iterable[ColumnNameOrSelector],
        strict: bool = True,
    ) -> Self:
        return type(self)(
            data=super().drop(*columns, strict=strict), metadata=self.metadata
        )

    @override
    def drop_nans(
        self,
        subset: ColumnNameOrSelector | Collection[ColumnNameOrSelector] | None = None,
    ) -> Self:
        return type(self)(data=super().drop_nans(subset), metadata=self.metadata)

    @override
    def drop_nulls(
        self,
        subset: ColumnNameOrSelector | Collection[ColumnNameOrSelector] | None = None,
    ) -> Self:
        return type(self)(data=super().drop_nulls(subset), metadata=self.metadata)

    @override
    def explode(
        self, columns: str | Expr | Sequence[str | Expr], *more_columns: str | Expr
    ) -> Self:
        return type(self)(
            data=super().explode(columns, *more_columns), metadata=self.metadata
        )

    @override
    def filter(
        self,
        *predicates: (
            IntoExprColumn
            | Iterable[IntoExprColumn]
            | bool
            | list[bool]
            | ndarray[Any, Any]
        ),
        **constraints: Any,
    ) -> Self:
        return type(self)(
            data=super().filter(*predicates, **constraints), metadata=self.metadata
        )

    @override
    def group_by(
        self,
        *by: IntoExpr | Iterable[IntoExpr],
        maintain_order: bool = False,
        **named_by: IntoExpr,
    ) -> GroupByWithMetaData[MD, Self]:
        group_by = super().group_by(*by, maintain_order=maintain_order, **named_by)
        return GroupByWithMetaData(
            group_by.df,
            *group_by.by,
            maintain_order=group_by.maintain_order,
            _cls=type(self),
            _metadata=self.metadata,
            **group_by.named_by,
        )

    @override
    def head(self, n: int = 5) -> Self:
        return type(self)(data=super().head(n), metadata=self.metadata)

    @override
    def join(
        self,
        other: DataFrame,
        on: str | Expr | Sequence[str | Expr] | None = None,
        how: JoinStrategy = "inner",
        *,
        left_on: str | Expr | Sequence[str | Expr] | None = None,
        right_on: str | Expr | Sequence[str | Expr] | None = None,
        suffix: str = "_right",
        validate: JoinValidation = "m:m",
        nulls_equal: bool = False,
        coalesce: bool | None = None,
        maintain_order: MaintainOrderJoin | None = None,
    ) -> Self:
        return type(self)(
            data=super().join(
                other,
                on,
                how,
                left_on=left_on,
                right_on=right_on,
                suffix=suffix,
                validate=validate,
                nulls_equal=nulls_equal,
                coalesce=coalesce,
                maintain_order=maintain_order,
            ),
            metadata=self.metadata,
        )

    @override
    def rename(
        self, mapping: Mapping[str, str] | Callable[[str], str], *, strict: bool = True
    ) -> Self:
        return type(self)(
            data=super().rename(mapping, strict=strict), metadata=self.metadata
        )

    @override
    def reverse(self) -> Self:
        return type(self)(data=super().reverse(), metadata=self.metadata)

    @override
    def sample(
        self,
        n: int | Series | None = None,
        *,
        fraction: float | Series | None = None,
        with_replacement: bool = False,
        shuffle: bool = False,
        seed: int | None = None,
    ) -> Self:
        return type(self)(
            data=super().sample(
                n,
                fraction=fraction,
                with_replacement=with_replacement,
                shuffle=shuffle,
                seed=seed,
            ),
            metadata=self.metadata,
        )

    @override
    def select(
        self, *exprs: IntoExpr | Iterable[IntoExpr], **named_exprs: IntoExpr
    ) -> Self:
        return type(self)(
            data=super().select(*exprs, **named_exprs), metadata=self.metadata
        )

    @override
    def shift(self, n: int = 1, *, fill_value: IntoExpr | None = None) -> Self:
        return type(self)(
            data=super().shift(n, fill_value=fill_value), metadata=self.metadata
        )

    @override
    def tail(self, n: int = 5) -> Self:
        return type(self)(data=super().tail(n), metadata=self.metadata)

    @override
    def to_series(self, index: int = 0) -> SR:
        return self.series_with_metadata(
            values=super().to_series(index), metadata=self.metadata
        )

    @override
    def with_columns(
        self, *exprs: IntoExpr | Iterable[IntoExpr], **named_exprs: IntoExpr
    ) -> Self:
        return type(self)(
            data=super().with_columns(*exprs, **named_exprs), metadata=self.metadata
        )

    @override
    def with_row_index(self, name: str = "index", offset: int = 0) -> Self:
        return type(self)(
            data=super().with_row_index(name, offset), metadata=self.metadata
        )

    @property
    def series_with_metadata(self) -> type[SR]:
        return cast("type[SR]", SeriesWithMetaData)


class GroupByWithMetaData[MD, DF: DataFrameWithMetaData](GroupBy):
    @override
    def __init__(
        self,
        df: DataFrame,
        *by: IntoExpr | Iterable[IntoExpr],
        maintain_order: bool,
        _cls: type[DF],
        _metadata: MD,
        **named_by: IntoExpr,
    ) -> None:
        super().__init__(df, *by, maintain_order=maintain_order, **named_by)
        self.cls = _cls
        self.metadata = _metadata

    @override
    def agg(self, *aggs: IntoExpr | Iterable[IntoExpr], **named_aggs: IntoExpr) -> DF:
        return self.cls(data=super().agg(*aggs, **named_aggs), metadata=self.metadata)


__all__ = ["DataFrameWithMetaData", "SeriesWithMetaData"]
