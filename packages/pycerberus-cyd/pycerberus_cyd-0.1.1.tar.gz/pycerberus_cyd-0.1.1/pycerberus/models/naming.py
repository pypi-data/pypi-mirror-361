from .common import CerberusBase, Md5


class CerberusNaming(CerberusBase):
    md5 : Md5
    malware_name: str
    malware_types: dict[str, int]
    packer_name: str
    version : str

