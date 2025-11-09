from typing import Annotated
from pydantic import Field
from domain.user.model import EnumUserStatus, UserDescription, UserID, UserName, UserTags


type SchemaUserID = UserID
type SchemaUserName = Annotated[UserName, Field(min_length=1)]
type SchemaUserDescription = Annotated[UserDescription, Field(default=None)]
type SchemaUserStatus = Annotated[EnumUserStatus, Field(default=EnumUserStatus.ACTIVE)]
type SchemaUserTags = Annotated[UserTags, Field(default_factory=list)]
