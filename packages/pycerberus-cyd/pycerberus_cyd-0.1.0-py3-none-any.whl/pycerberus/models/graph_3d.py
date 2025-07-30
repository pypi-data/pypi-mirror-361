from .common import CerberusBase
from pydantic import Field, ConfigDict

class CerberusGraph3d(CerberusBase):
    # TODO: improve model
    graph_3d: dict = Field(alias='3d_graph')  # type: ignore
                                              # (Don't know why but Pyright says that "Alias name "3d_graph" is not a valid identifier" ...

    model_config = ConfigDict(populate_by_name=True)

class CerberusGraph3dScreenshots(CerberusBase):
    screenshots: list[str]
