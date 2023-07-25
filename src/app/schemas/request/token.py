from pydantic import BaseModel


class RefreshSchema(BaseModel):
    refresh_token: str
    # TODO: coming soon
    # grant_type: str
    # client_id: int
    # client_secret


class AccessSchema(BaseModel):
    access_token: str
