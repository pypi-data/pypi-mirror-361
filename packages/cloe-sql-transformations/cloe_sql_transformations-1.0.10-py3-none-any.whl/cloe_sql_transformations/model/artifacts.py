import re

from cloe_sql_transformations.model.sql_syntax import SQLSyntax


class VersionArtifact:
    def __init__(self, sink_table_identifier: str, sql_syntax: SQLSyntax) -> None:
        self._sql_syntax = sql_syntax
        self.ver_sink_table_identifier: str = sink_table_identifier
        self.ver_source_insert: list[str] = []
        self.ver_sink_insert: list[str] = []
        self.ver_sink_source_field_comparison: list[str] = []
        self.ver_lu_sink_source_join: list[str] = []

    def finalize_environment(self) -> dict[str, str]:
        table_addon = {}
        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                table_addon[key] = value
            if isinstance(value, list):
                if key in ("ver_sink_source_field_comparison"):
                    table_addon[f"{key}_artifact"] = (
                        self._sql_syntax.combine_conditions_or(value)
                    )
                elif key in ("ver_lu_sink_source_join"):
                    table_addon[f"{key}_artifact"] = (
                        self._sql_syntax.join_separator.join(value)
                    )
                else:
                    table_addon[f"{key}_artifact"] = self._sql_syntax.combine_columns(
                        value
                    )
            else:
                table_addon[f"{key}_artifact"] = value
        return table_addon


class Artifacts:
    def __init__(
        self,
        sql_syntax: SQLSyntax,
        include_dq1: bool,
        include_dq2: bool,
        include_dq3: bool,
        ver_artifacts: dict[str, VersionArtifact] = {},
    ) -> None:
        self._sql_syntax = sql_syntax
        self.include_dq1 = include_dq1
        self.include_dq2 = include_dq2
        self.include_dq3 = include_dq3
        self.sink_table_identifier_artifact: str | None = None
        self.source_table_identifier_artifact: str | None = None
        self.source_insert: list[str] = []
        self.source_lu_used_columns: list[str] = []
        self.sink_insert: list[str] = []
        self.sink_source_update: list[str] = []
        self.sink_source_field_comparison: list[str] = []
        self.dq1_view_select_as_raw: list[str] = []
        self.dq2_view_select_as_raw: list[str] = []
        self.dq3_view_select_as_raw: list[str] = []
        self.dq1_view_select_as_name: list[str] = []
        self.dq2_view_select_as_name: list[str] = []
        self.dq3_view_select_as_name: list[str] = []
        self.dq1_log_select: list[str] = []
        self.dq2_view_where: list[str] = []
        self.dq2_log_where: list[str] = []
        self.dq2_log_select: list[str] = []
        self.lu_source_insert: list[str] = []
        self.lu_sink_insert: list[str] = []
        self.lu_sink_source_update: list[str] = []
        self.lu_sink_source_join: list[str] = []
        self.dq3_log_select: list[str] = []
        self.dq3_log_where: list[str] = []
        self.dq3_log_lu_sink_source_join: list[str] = []
        self.versioning_artifacts: dict[str, VersionArtifact] = ver_artifacts

    def clean_lookup_artifacts(self) -> None:
        self.lu_source_insert.clear()
        self.lu_sink_insert.clear()
        self.lu_sink_source_update.clear()
        self.lu_sink_source_join.clear()

    def _finalize_environment_versioning(
        self, snippets: dict[str, VersionArtifact]
    ) -> list[dict[str, str]]:
        """Combines all versioning snippets.

        Args:
            snippets (dict): _description_

        Returns:
            list: _description_
        """
        versioning_addon = []
        for table_snippets in snippets.values():
            versioning_addon.append(table_snippets.finalize_environment())
        return versioning_addon

    def finalize_snippets(self, key: str, snippets: list[str]) -> dict[str, str]:
        addon_environment = {}
        if len(snippets) > len(set(snippets)) and (
            re.match(r"dq\d_view_select", key) or key in ("source_lu_used_columns")
        ):
            snippets = sorted(set(snippets), reverse=True)
        if key in (
            "sink_source_field_comparison",
            "dq2_view_where",
            "dq2_log_where",
            "dq3_log_where",
        ):
            addon_environment[f"{key}_artifact"] = (
                self._sql_syntax.combine_conditions_or(snippets)
            )
        elif key in ("lu_sink_source_join", "dq3_log_lu_sink_source_join"):
            addon_environment[f"{key}_artifact"] = self._sql_syntax.join_separator.join(
                snippets
            )
        else:
            addon_environment[f"{key}_artifact"] = self._sql_syntax.combine_columns(
                snippets
            )
        return addon_environment

    def finalize_environment(self) -> dict[str, str | list[dict[str, str]]]:
        """Combines all dataflow snippets."""
        addon_environment = {}
        for key, values in self.__dict__.items():
            if not key.startswith("_"):
                addon_environment[key] = values
            if not key.startswith("_") and isinstance(values, list):
                addon_environment |= self.finalize_snippets(key, values)
            if key == "versioning_artifacts":
                values = self._finalize_environment_versioning(values)
                addon_environment["versioning_artifacts"] = values
        return addon_environment
