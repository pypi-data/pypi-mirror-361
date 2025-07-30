from .common import CerberusBase

class CerberusLoadDbGcore(CerberusBase):
    # TODO: improve model in deep
    databases: dict
    status: str
    loaded_db_on_gorillecore_server: int


