from .common import CerberusBase

class CerberusUnloadDbGcore(CerberusBase):
    databases: dict
    status: str
    loaded_db_on_gorillecore_server: int


