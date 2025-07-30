from typing import Any, Dict, List, Optional, TypeVar, Union, TypeAlias, Generic
from enum import Enum
from dataclasses import dataclass
from pydantic import BaseModel, ConfigDict, Field
from pydantic.generics import GenericModel

from jsonapi._mixins.serializers import (
    DocumentSerializerMixin,
    ErrorSerializerMixin,
    ResourceSerializerMixin,
    QueryParamsSerializerMixin,
)
from jsonapi._mixins.validators import (
    DocumentValidatorMixin,
    ErrorSourceValidatorMixin,
    JSONAPIErrorValidatorMixin,
    LinkValidatorMixin,
    ResourceIdentifierValidatorMixin,
    ResourceValidatorMixin,
    QueryParamsValidatorMixin,
    QueryParamsParserMixin,
)

MetaObject: TypeAlias = Optional[Dict[str, Any]]
LinkValue: TypeAlias = Union[str, "LinkObject"]
RelationshipData: TypeAlias = Union[
    "ResourceIdentifier", List["ResourceIdentifier"], None
]
ErrorList: TypeAlias = List["JSONAPIError"]

JSONAPI_CONTENT_TYPE = "application/vnd.api+json"
JSONAPI_ACCEPT = "application/vnd.api+json"
JSONAPI_VERSION = "1.1"


def prune_empty(obj: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in obj.items() if v not in (None, [], {}, "")}


class JSONAPIInfo(BaseModel):
    version: str = Field(default=JSONAPI_VERSION)
    ext: Optional[List[str]] = None
    profile: Optional[List[str]] = None
    meta: MetaObject = None


class ErrorSource(BaseModel, ErrorSourceValidatorMixin):
    pointer: Optional[str] = None
    parameter: Optional[str] = None
    header: Optional[str] = None


class JSONAPIError(BaseModel, ErrorSerializerMixin, JSONAPIErrorValidatorMixin):
    id: Optional[str] = None
    links: Optional[Dict[str, LinkValue]] = None
    status: Optional[str] = None
    code: Optional[str] = None
    title: Optional[str] = None
    detail: Optional[str] = None
    source: Optional[ErrorSource] = None
    meta: MetaObject = None


class LinkObject(BaseModel, LinkValidatorMixin):
    href: str
    rel: Optional[str] = None
    describedby: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None
    hreflang: Optional[Union[str, List[str]]] = None
    meta: MetaObject = None


class Links(BaseModel):
    self: LinkValue
    related: Optional[LinkValue] = None
    first: Optional[LinkValue] = None
    last: Optional[LinkValue] = None
    prev: Optional[LinkValue] = None
    next: Optional[LinkValue] = None

    model_config = ConfigDict(extra="forbid")


class ResourceIdentifier(BaseModel, ResourceIdentifierValidatorMixin):
    type: str
    id: Optional[str] = None
    lid: Optional[str] = None
    meta: MetaObject = None


class Relationship(BaseModel):
    data: RelationshipData
    links: Optional[Links] = None
    meta: MetaObject = None


AttributesT = TypeVar("AttributesT", bound=BaseModel)


class Resource(
    ResourceIdentifier,
    ResourceSerializerMixin,
    ResourceValidatorMixin,
    GenericModel,
    Generic[AttributesT],
):
    attributes: Optional[AttributesT] = None
    relationships: Optional[Dict[str, Relationship]] = None
    links: Optional[Links] = None
    meta: MetaObject = None

    model_config = ConfigDict(extra="forbid")


class JSONAPIDocument(
    BaseModel,
    DocumentSerializerMixin,
    DocumentValidatorMixin,
    Generic[AttributesT],
):
    data: Optional[Union[Resource[AttributesT], List[Resource[AttributesT]]]] = None
    errors: Optional[ErrorList] = None
    meta: MetaObject = None
    jsonapi: Optional[JSONAPIInfo] = Field(default_factory=JSONAPIInfo)
    links: Optional[Links] = None
    included: Optional[List[Resource[BaseModel]]] = None


class JSONAPIHeader(BaseModel):
    version: str = Field(default=JSONAPI_VERSION, alias="jsonapi-version")
    accept: str = Field(default=JSONAPI_ACCEPT)
    content_type: str = Field(default=JSONAPI_CONTENT_TYPE, alias="content-type")


class JSONAPIRequestBody(GenericModel, Generic[AttributesT]):
    data: Union[Resource[AttributesT], List[Resource[AttributesT]]]
    meta: MetaObject = None

    model_config = ConfigDict(extra="forbid")


class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


class FilterOperator(str, Enum):
    EQ = "eq"
    NE = "ne"
    LT = "lt"
    LE = "le"
    GT = "gt"
    GE = "ge"
    LIKE = "like"
    IN_ = "in"
    NOT_IN = "not_in"


@dataclass
class SortField:
    field: str
    direction: SortDirection = SortDirection.ASC

    @classmethod
    def from_string(cls, sort_string: str) -> "SortField":
        return cls(
            field=sort_string.lstrip("-"),
            direction=SortDirection.DESC
            if sort_string.startswith("-")
            else SortDirection.ASC,
        )

    def to_string(self) -> str:
        return f"{'-' if self.direction == SortDirection.DESC else ''}{self.field}"


@dataclass
class FilterCondition:
    field: str
    operator: FilterOperator
    value: Union[str, List[str]]

    def __post_init__(self):
        if self.operator in [
            FilterOperator.IN_,
            FilterOperator.NOT_IN,
        ] and not isinstance(self.value, list):
            self.value = [self.value] if self.value else []


@dataclass
class PaginationParams:
    number: Optional[int] = 1
    size: Optional[int] = 20
    offset: Optional[int] = None
    limit: Optional[int] = 20
    cursor: Optional[str] = None

    def __post_init__(self):
        if self.number and self.number < 1:
            raise ValueError("Page number must be >= 1")
        if self.size and self.size < 1:
            raise ValueError("Page size must be >= 1")
        if self.offset and self.offset < 0:
            raise ValueError("Offset must be >= 0")
        if self.limit and self.limit < 1:
            raise ValueError("Limit must be >= 1")

    @classmethod
    def from_dict(cls, raw: Dict[str, Union[str, int]]) -> "PaginationParams":
        return cls(
            number=int(raw.get("number", 1)) if "number" in raw else None,
            size=int(raw.get("size", 20)) if "size" in raw else None,
            offset=int(raw.get("offset", 0)) if "offset" in raw else None,
            limit=int(raw.get("limit", 20)) if "limit" in raw else None,
            cursor=str(raw.get("cursor")) if "cursor" in raw else None,
        )


class JSONAPIQueryParams(
    BaseModel,
    QueryParamsParserMixin,
    QueryParamsValidatorMixin,
    QueryParamsSerializerMixin,
):
    include: Optional[List[str]] = None
    sort: Optional[List[Dict[str, str]]] = None
    filters: Optional[List[Dict[str, Any]]] = None
    fields: Optional[Dict[str, List[str]]] = None
    pagination: Optional[Dict[str, Union[int, str]]] = None
    extra_params: Optional[Dict[str, Any]] = None

    def get_sort_fields(self) -> Dict[str, SortField]:
        return {
            item["field"]: SortField(
                field=item["field"],
                direction=SortDirection(item["direction"]),
            )
            for item in self.sort or []
        }

    def get_filter_conditions(self) -> Dict[str, FilterCondition]:
        return {
            item["field"]: FilterCondition(
                field=item["field"],
                operator=FilterOperator(item["operator"]),
                value=item["value"],
            )
            for item in self.filters or []
        }

    def get_pagination_params(self) -> PaginationParams:
        return PaginationParams.from_dict(self.pagination or {})

    def get_sparse_fields(self, resource_type: str) -> List[str]:
        return self.fields.get(resource_type, []) if self.fields else []

    def get_included_resources(self) -> List[str]:
        return self.include or []
