from .common import CerberusBase

class CerberusMagic(CerberusBase):
    raw: str
    arch: str
    format: str
    tags: list[str]
    version: str

    def is_dot_net(self) -> bool:
        if self.arch in ["x86_64", "i386"]:
            if self.format in ["PE", "PE+"]:
                if ".NET" in self.tags:
                    return True
        return False