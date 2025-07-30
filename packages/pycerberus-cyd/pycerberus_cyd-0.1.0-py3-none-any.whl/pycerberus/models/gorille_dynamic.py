from .common import (
    CerberusGorilleAnalysis,
    CerberusGorilleGcoreAnalysis,
)
from pydantic import BaseModel

class CerberusScreenshot(BaseModel):
    img: str
    tick: float


class CerberusWave(BaseModel):
    number: int
    entry_point: str


class CerberusGorilleDynamic(CerberusGorilleAnalysis):
    screenshots: list[CerberusScreenshot]
    waves: list[CerberusWave]
    antidebugs: list[str]


class CerberusGorilleDynamicSandbox(BaseModel):
    screenshots: list[CerberusScreenshot]
    waves: list[CerberusWave]
    antidebugs: list[str]


class CerberusGorilleDynamicGcore(CerberusGorilleGcoreAnalysis):
    sandbox: CerberusGorilleDynamicSandbox
