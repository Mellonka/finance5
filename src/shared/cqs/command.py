from pydantic import BaseModel, ConfigDict


class CommandBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
