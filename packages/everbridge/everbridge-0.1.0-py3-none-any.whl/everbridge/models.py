from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional


def parse_datetime(value):
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            return datetime.fromisoformat(value)
    return datetime.fromtimestamp(value / 1000)


class Sender(BaseModel):
    id: int


class Setting(BaseModel):
    requestImage: bool
    requestLocation: bool
    requestComment: bool
    allowShare: bool
    requireConfirm: bool


class State(BaseModel):
    read: bool
    shared: bool
    confirmed: bool
    active: bool


class Notification(BaseModel):
    id: int
    title: str
    body: str
    priority: bool
    sender: Sender
    source: str
    setting: Setting
    state: State
    enableIncidentChat: bool
    ittl: bool
    createdAt: datetime
    expiredAt: datetime

    @field_validator("createdAt", "expiredAt", mode="before")
    def convert_timestamp_to_datetime(cls, value):
        return parse_datetime(value)


class AccessToken(BaseModel):
    grantDate: datetime
    expireDate: datetime
    value: str

    @field_validator("grantDate", "expireDate", mode="before")
    def convert_timestamp_to_datetime(cls, value):
        return parse_datetime(value)


class RefreshToken(BaseModel):
    grantDate: datetime
    expireDate: datetime
    value: str

    @field_validator("grantDate", "expireDate", mode="before")
    def convert_timestamp_to_datetime(cls, value):
        return parse_datetime(value)


class AccessTokenResponse(BaseModel):
    clientId: str
    accessToken: AccessToken
    individualAccountId: str
    organizationId: Optional[str] = None
