from pydantic import BaseModel
from .common import CerberusBase

class CerberusStatusEngines(BaseModel):
    core: dict
    die: dict | None = None
    extract: dict | None = None
    strings: dict | None = None
    gorille_static: dict | None = None
    gorille_static_gcore: dict | None = None
    gorille_sites_gcore: dict | None = None
    graph_3d: dict | None = None
    clamav: dict | None = None
    naming: dict | None = None
    filter: dict | None = None
    malware_metadata: dict | None = None
    magic: dict | None = None
    signature: dict | None = None

class CerberusStatus(CerberusBase):
    engines: CerberusStatusEngines
    filter_manager: dict | None = None
    malware_metadata_manager: str | None = None
    naming_manager: dict | None = None
    gorille_core_manager: dict  | None = None
    mdec_manager: dict  | None = None
