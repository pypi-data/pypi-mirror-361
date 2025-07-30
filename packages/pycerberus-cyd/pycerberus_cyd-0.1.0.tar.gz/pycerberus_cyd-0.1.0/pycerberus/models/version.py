from pydantic import BaseModel
from .common import CerberusBase, CerberusGorilleCoreVersion

class CerberusVersionEngines(BaseModel):
    # TODO: improve gorille models with Pydantic models instead of generic dict
    die: str | None = None
    extract: dict[str, str] | None = None
    strings: str | None = None
    gorille_static: dict | None = None
    gorille_static_gcore: CerberusGorilleCoreVersion | None = None
    gorille_dynamic_gcore: CerberusGorilleCoreVersion | None = None
    gorille_sites_gcore: CerberusGorilleCoreVersion | None = None
    graph_3d: str | None = None
    clamav: str | None = None
    naming: str | None = None
    malware_metadata: str | None = None
    magic: str | None = None
    signature: str | None = None
    filter: str | None = None

class CerberusVersion(CerberusBase):
    cerberus: str
    engines: CerberusVersionEngines

