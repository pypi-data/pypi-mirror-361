from .common import CerberusBase

class CerberusUsage(CerberusBase):
    status: dict
    version: dict
    usage: dict
    load_db: dict
    unload_db_gcore: dict
    load_db_gcore: dict
    is_alive: dict
    die: dict
    extract: dict
    strings: dict
    gorille_static: dict
    gorille_static_gcore: dict
    gorille_sites_gcore: dict
    graph_3d: dict
    clamav: dict
    naming: dict
    filter: dict
    malware_metadata: dict
    magic: dict
    signature: dict
