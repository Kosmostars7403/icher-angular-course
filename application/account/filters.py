from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import ConfigDict, alias_generators, Field, field_validator

from application.account.models import User


class UserFilter(Filter):
    model_config = ConfigDict(alias_generator=alias_generators.to_camel, populate_by_name=True)

    first_name__ilike: str | None = Field(default='', alias="firstName")
    last_name__ilike: str | None = Field(default='', alias="lastName")
    city__ilike: str | None = Field(default='', alias="city")
    order_by: list[str] | None = Field(default=[], alias="orderBy")

    @field_validator("order_by", mode='before')
    def to_snake_params(cls, value):
        if value:
            return alias_generators.to_snake(value)

    class Constants(Filter.Constants):
        model = User
