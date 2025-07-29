from typing import Self

from cognite.client.data_classes.data_modeling import (
    EdgeConnection,
    MappedProperty,
    View,
)
from cognite.client.data_classes.data_modeling.data_types import (
    ListablePropertyType,
)
from cognite.client.data_classes.data_modeling.views import (
    MultiReverseDirectRelation,
    SingleReverseDirectRelation,
)
from pydantic import BaseModel, Field, model_validator

from .config import InstanceSpaceConfig
from .constants import (
    aggregate_group_types,
    list_operators,
    mapping_types,
    prefix_operator,
    python_keywords,
    range_types,
)
from .helpers import to_camel, to_pascal, to_snake


class FieldDefinition(BaseModel):
    field_name: str
    field_alias: str | None
    field_type: str
    is_nullable: bool
    is_list: bool

    def __str__(self) -> str:
        type_ = self.field_type

        field_properties: dict[str, str] = {}
        if self.field_alias:
            field_properties["alias"] = f'"{self.field_alias}"'
        if self.is_list:
            field_properties["default_factory"] = f"list[{type_}]"
            type_ = f"list[{type_}]"
        if self.is_nullable and not self.is_list:
            field_properties["default"] = "None"
            type_ += " | None"

        result = f"{self.field_name}: {type_}"
        if not field_properties:
            return result

        if len(field_properties) == 1 and "default" in field_properties:
            result += " = None"
            return result

        field_properties_str = ", ".join(
            f"{key}={value}" for key, value in field_properties.items()
        )
        result += f" = Field({field_properties_str})"
        return result

    @property
    def operators(self) -> list[str]:
        if self.field_type == "Any":
            return []
        if self.is_list:
            return ["contains_all", "contains_any"]

        default_operators = ["eq", "in", "exists"]
        if self.field_type in range_types and not self.is_list:
            return default_operators + ["gt", "gte", "lt", "lte"]
        elif self.field_type == "str":
            return default_operators + ["prefix"]
        return default_operators


class ViewDefinition(BaseModel):
    view_name: str
    view_alias: str | None = None
    view_code: str | None = None

    view_module_name: str

    aggregate_fields: list[FieldDefinition] = Field(default_factory=list)
    search_fields: list[FieldDefinition] = Field(default_factory=list)
    regular_fields: list[FieldDefinition] = Field(default_factory=list)
    complete_fields: list[FieldDefinition] = Field(default_factory=list)

    instance_space_config: InstanceSpaceConfig | None

    @classmethod
    def from_view(
        cls, view: View, instance_space_config: InstanceSpaceConfig | None
    ) -> "ViewDefinition":
        aggregate_fields: list[FieldDefinition] = []
        search_fields: list[FieldDefinition] = []
        regular_fields: list[FieldDefinition] = []
        complete_fields: list[FieldDefinition] = []

        for property_name, property in view.properties.items():
            field_name = to_snake(property_name)
            is_reserved_name = field_name in python_keywords

            if is_reserved_name:
                field_name = f"{field_name}_"
            field_alias = (
                property_name
                if to_camel(field_name) != property_name or is_reserved_name
                else None
            )
            if isinstance(property, MappedProperty):
                base_type = mapping_types[property.type._type]
                is_nullable = property.nullable
                is_list = (
                    isinstance(property.type, ListablePropertyType)
                    and property.type.is_list
                )

                if (
                    not is_list
                    and property.type._type in aggregate_group_types
                    and field_name != "value"
                ):
                    aggregate_fields.append(
                        FieldDefinition(
                            field_name=field_name,
                            field_alias=field_alias,
                            field_type=base_type,
                            is_nullable=True,
                            is_list=False,
                        )
                    )

                search_fields.append(
                    FieldDefinition(
                        field_name=field_name,
                        field_alias=field_alias,
                        field_type=base_type,
                        is_nullable=is_nullable,
                        is_list=is_list,
                    )
                )

                target_view = property.source.external_id if property.source else None

                complete_fields.append(
                    FieldDefinition(
                        field_name=field_name,
                        field_alias=field_alias,
                        field_type=f"{to_pascal(target_view)}Search"
                        if target_view
                        else base_type,
                        is_nullable=is_nullable,
                        is_list=is_list,
                    )
                )

            elif isinstance(
                property,
                SingleReverseDirectRelation
                | MultiReverseDirectRelation
                | EdgeConnection,
            ):
                is_nullable = isinstance(property, SingleReverseDirectRelation)
                is_list = not isinstance(property, SingleReverseDirectRelation)
                regular_fields.append(
                    FieldDefinition(
                        field_name=field_name,
                        field_alias=field_alias,
                        field_type="InstanceId",
                        is_nullable=is_nullable,
                        is_list=is_list,
                    )
                )

                complete_fields.append(
                    FieldDefinition(
                        field_name=field_name,
                        field_alias=field_alias,
                        field_type=f"{to_pascal(property.source.external_id)}Search",
                        is_nullable=is_nullable,
                        is_list=is_list,
                    )
                )
            else:
                raise ValueError(f"Unsupported property type: {type(property)}")

        view_name = to_pascal(view.external_id)

        view_code = cls._extract_view_code(view)

        return cls(
            view_name=view_name,
            view_alias=(view.external_id if view_name != view.external_id else None),
            view_code=view_code,
            view_module_name=to_snake(view_name),
            aggregate_fields=aggregate_fields,
            search_fields=search_fields,
            regular_fields=regular_fields,
            complete_fields=complete_fields,
            instance_space_config=instance_space_config,
        )

    @classmethod
    def _extract_view_code(
        cls, view: View, code_annotation: str = "@code"
    ) -> str | None:
        if not view.description:
            return None
        description_metadata = view.description.split()
        if not description_metadata or code_annotation not in description_metadata:
            return None

        code_idx = description_metadata.index(code_annotation)
        if code_idx + 1 > len(description_metadata):
            return None

        view_code = description_metadata[code_idx + 1].strip()
        return view_code if len(view_code) > 0 else None

    @property
    def view_config(self) -> str:
        fields = {
            "view_external_id": f'"{self.view_alias or self.view_name}"',
        }
        if self.view_code:
            fields["view_code"] = f'"{self.view_code}"'
        if self.instance_space_config and self.instance_space_config.instance_spaces:
            fields["instance_spaces"] = (
                "["
                + ",".join(
                    [
                        f'"{space}"'
                        for space in self.instance_space_config.instance_spaces
                    ]
                )
                + "]"
            )
        elif (
            self.instance_space_config
            and self.instance_space_config.instance_spaces_prefix
        ):
            fields["instance_spaces_prefix"] = (
                f'"{self.instance_space_config.instance_spaces_prefix}"'
            )

        fields_str = ", ".join(f"{key}={value}" for key, value in fields.items())

        return f"view_config = ViewInstanceConfig({fields_str})"

    @property
    def request_fields(self) -> list[str]:
        filter_fields = FilterField.default_filter_fields()

        for search_field in self.search_fields:
            property_ = search_field.field_alias or to_camel(search_field.field_name)
            for operator in search_field.operators:
                filter_fields.append(
                    FilterField(
                        field_name=f"{search_field.field_name}_{operator}",
                        property=property_,
                        operator=prefix_operator.get(operator, operator),
                        field_type=search_field.field_type,
                    )
                )

        return sorted([str(filter_field) for filter_field in filter_fields])

    @property
    def query_property_field(self) -> str:
        fields: list[str] = []
        for search_field in self.search_fields:
            if not search_field.is_list and search_field.field_type == "str":
                fields.append(
                    search_field.field_alias or to_camel(search_field.field_name)
                )

        fields_as_str = ", ".join([f'"{field}"' for field in fields])
        literal_def = f"Literal[{fields_as_str}]" if fields else "str"

        return f"query_properties: list[{literal_def}] | None = None"

    @property
    def group_by_field(self) -> str:
        fields: list[str] = []
        for aggregate_field in self.aggregate_fields:
            fields.append(
                aggregate_field.field_alias or to_camel(aggregate_field.field_name)
            )

        fields_as_str = ", ".join([f'"{field}"' for field in fields])
        literal_def = f"Literal[{fields_as_str}]" if fields else "str"

        return f"group_by_properties: list[{literal_def}] | None = None"


class FilterField(BaseModel):
    field_name: str
    property: str
    operator: str
    field_type: str

    @model_validator(mode="after")
    def check_model(self) -> Self:
        if self.operator in list_operators:
            self.field_type = f"list[{self.field_type}]"
        elif self.operator == "exists":
            self.field_type = "bool"
        return self

    def __str__(self) -> str:
        return f'{self.field_name}: Annotated[{self.field_type} | None, QueryParam(property="{self.property}", operator="{self.operator}")] = None'  # noqa: E501

    @classmethod
    def default_filter_fields(cls) -> list["FilterField"]:
        return [
            cls(
                field_name="external_id_in",
                property="externalId",
                operator="in",
                field_type="str",
            ),
            cls(
                field_name="external_id_eq",
                property="externalId",
                operator="==",
                field_type="str",
            ),
            cls(
                field_name="external_id_prefix",
                property="externalId",
                operator="prefix",
                field_type="str",
            ),
            cls(
                field_name="space_in",
                property="space",
                operator="in",
                field_type="str",
            ),
            cls(
                field_name="space_eq", property="space", operator="==", field_type="str"
            ),
        ]
