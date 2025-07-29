import datetime as dt
import typing

import pydantic

from ....core.datetime_utils import serialize_datetime

##### NOTE : Not used yet as the API returns a single string on get, but 
# modifying the API to return a Secret object would fit better the 
# design principles of the langfuse SDK
class Secret(pydantic.BaseModel):
    id: str
    name: str
    value: typing.Optional[str] = None
    project_id: str = pydantic.Field(alias="projectId")
    created_at: dt.datetime = pydantic.Field(alias="createdAt")
    updated_at: dt.datetime = pydantic.Field(alias="updatedAt")

    def json(self, **kwargs: typing.Any) -> str:
        kwargs_with_defaults: typing.Any = {
            "by_alias": True,
            "exclude_unset": True,
            **kwargs,
        }
        return super().json(**kwargs_with_defaults)

    def dict(self, **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        kwargs_with_defaults: typing.Any = {
            "by_alias": True,
            "exclude_unset": True,
            **kwargs,
        }
        return super().dict(**kwargs_with_defaults)

    class Config:
        frozen = True
        smart_union = True
        allow_population_by_field_name = True
        populate_by_name = True
        extra = pydantic.Extra.allow
        json_encoders = {dt.datetime: serialize_datetime} 