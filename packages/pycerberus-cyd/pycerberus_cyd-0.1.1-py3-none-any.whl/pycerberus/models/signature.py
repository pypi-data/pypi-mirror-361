from .common import CerberusBase

class CerberusSignature(CerberusBase):
    calculated_pe_checksum: str | None = None
    current_pe_checksum: str | None = None
    errors: dict
    signatures: list | None = None
    status: int
    status_desc: str
