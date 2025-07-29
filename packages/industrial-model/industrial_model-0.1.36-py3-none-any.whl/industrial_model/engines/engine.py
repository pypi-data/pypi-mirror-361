from typing import Any

from cognite.client import CogniteClient

from industrial_model.cognite_adapters import CogniteAdapter
from industrial_model.config import DataModelId
from industrial_model.models import (
    PaginatedResult,
    TAggregatedViewInstance,
    TViewInstance,
    TWritableViewInstance,
    ValidationMode,
    include_edges,
)
from industrial_model.statements import (
    AggregationStatement,
    SearchStatement,
    Statement,
)


class Engine:
    def __init__(
        self,
        cognite_client: CogniteClient,
        data_model_id: DataModelId,
    ):
        self._cognite_adapter = CogniteAdapter(cognite_client, data_model_id)

    def search(
        self,
        statement: SearchStatement[TViewInstance],
        validation_mode: ValidationMode = "raiseOnError",
    ) -> list[TViewInstance]:
        """
        Note:
            External ID searches work as prefix searches.
            This method does not include edges or direct relations in the result model.
            Filter does not support nested properties.
        """
        data = self._cognite_adapter.search(statement)
        return self._validate_data(statement.entity, data, validation_mode)

    def query(
        self,
        statement: Statement[TViewInstance],
        validation_mode: ValidationMode = "raiseOnError",
    ) -> PaginatedResult[TViewInstance]:
        data, next_cursor = self._cognite_adapter.query(statement, False)

        return PaginatedResult(
            data=self._validate_data(statement.entity, data, validation_mode),
            next_cursor=next_cursor,
            has_next_page=next_cursor is not None,
        )

    def query_all_pages(
        self,
        statement: Statement[TViewInstance],
        validation_mode: ValidationMode = "raiseOnError",
    ) -> list[TViewInstance]:
        if statement.get_values().cursor:
            raise ValueError("Cursor should be none when querying all pages")

        data, _ = self._cognite_adapter.query(statement, True)

        return self._validate_data(statement.entity, data, validation_mode)

    def aggregate(
        self, statement: AggregationStatement[TAggregatedViewInstance]
    ) -> list[TAggregatedViewInstance]:
        data = self._cognite_adapter.aggregate(statement)

        return [statement.entity.model_validate(item) for item in data]

    def upsert(
        self, entries: list[TWritableViewInstance], replace: bool = False
    ) -> None:
        if not entries:
            return

        return self._cognite_adapter.upsert(entries, replace)

    def delete(self, nodes: list[TViewInstance]) -> None:
        self._cognite_adapter.delete(
            nodes,
        )

    def _validate_data(
        self,
        entity: type[TViewInstance],
        data: list[dict[str, Any]],
        validation_mode: ValidationMode,
    ) -> list[TViewInstance]:
        result: list[TViewInstance] = []
        for item in data:
            try:
                validated_item = entity.model_validate(item)
                include_edges(item, validated_item)
                result.append(validated_item)
            except Exception:
                if validation_mode == "ignoreOnError":
                    continue
                raise
        return result
