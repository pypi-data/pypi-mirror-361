from pydantic import ConfigDict, BaseModel


class RadarBaseModel(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
