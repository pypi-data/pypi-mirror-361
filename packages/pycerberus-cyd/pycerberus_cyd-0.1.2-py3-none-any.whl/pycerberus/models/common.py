from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import BaseModel, GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, core_schema


class Md5(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v: Any):
        if not isinstance(v, str):
            raise TypeError("Invalid MD5 (not a string)")
        if not re.findall("^[0-9a-f]{32}$", v):
            raise ValueError("Invalid MD5 (wrong format)")
        return cls(v)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        # Use the same schema that would be used for `str`
        return handler(core_schema.str_schema())


class Sha256(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v: Any) -> Sha256:
        if not isinstance(v, str):
            raise TypeError("Invalid SHA256 (not a string)")
        if not re.findall("^[0-9a-f]{64}$", v):
            raise ValueError("Invalid SHA256 (wrong format)")
        return cls(v)


    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        # Use the same schema that would be used for `str`
        return handler(core_schema.str_schema())


class CerberusTime(BaseModel):
    handling_request: int
    waiting_available_worker: int

# Base model for any Cerberus response
class CerberusBase(BaseModel):
    time: CerberusTime


class CerberusMatch(BaseModel):
    refUniqueMatchSitesNumber: int
    refUniqueSitesNumber: int
    refName: str  # Matched file MD5
    refRealName: str  # Name given by the naming DB
    refTypes: dict[str, int] = {}  # Malware types with priority


class CerberusMatchGcore(BaseModel):
    name: str  # Matched file MD5
    real_name: str  # Name given by the naming DB
    shared_sites: int
    types: dict[str, int] = {}  # Malware types with priority


class CerberusDynData(BaseModel):
    antidebugs: int
    waves: int


class CerberusDistGcore(BaseModel):
    filepath: str
    filename: str
    node_info: dict[str, int] = {}
    site_info: dict[str, dict[str, int] | dict[str, dict[str, int]] | int] = {}
    matches: dict[str, dict[str, list[CerberusMatchGcore]]] = {}
    dyn_data: CerberusDynData | None = None
    status: int
    errmsg: str | None = None


class CerberusGraph(BaseModel):
    matchNodesNumber: int | None = None
    smallNodesNumber: int | None = None
    specificNodesNumber: int | None = None
    totalNodesNumber: int | None = None
    whiteNodesNumber: int | None = None

class CerberusDist(BaseModel):
    filename: str
    graph: CerberusGraph = CerberusGraph()
    uniqueSitesNumber: int | None = None
    uniqueMatchSitesNumber: int | None = None
    dyn_data: CerberusDynData | None = None
    status: int
    matches: list[CerberusMatch] | None = None
    errmsg: str | None = None
    time_dist: int | None = None


class CerberusDatabases(BaseModel):
    db_type: str
    db_version: str | None = None
    db_md5: Md5 | Literal['unset']
    filter_db_md5: Md5 | Literal['unset']



# Define the raw result given by Cerberus
# after a static, gpacker or dynamic analysis request
class CerberusGorilleAnalysis(CerberusBase):
    version: dict
    type: str
    files: dict[str, CerberusDist]

class CerberusGorilleCoreDatabaseVersion(BaseModel):
    label: str
    arch: str
    color: str
    tag: str
    type: str
    format: str
    timestamp: int
    datetime: str

class CerberusGorilleCoreVersion(BaseModel):
    libgorillecore: str
    databases: dict[str, CerberusGorilleCoreDatabaseVersion] = {}

# Define the raw result given by Cerberus
# after a static, gpacker or dynamic analysis request
class CerberusGorilleGcoreAnalysis(CerberusBase):
    version: CerberusGorilleCoreVersion
    files: dict[str, CerberusDistGcore]

