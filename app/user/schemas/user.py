from pydantic import BaseModel, Field


class GetUserListResponseSchema(BaseModel):
    id: int = Field(..., description="ID")
    email: str = Field(..., description="Email")
    nickname: str = Field(..., description="Nickname")

    class Config:
        orm_mode = True


class CreateUserRequestSchema(BaseModel):
    email: str = Field(..., description="Email")
    first_name: str = Field(..., description="First Name")
    last_name: str = Field(..., description="Last Name")
    password: str = Field(..., description="Password")


class CreateUserResponseSchema(BaseModel):
    email: str = Field(..., description="Email")
    first_name: str = Field(..., description="First Name")
    last_name: str = Field(..., description="Last Name")

    class Config:
        orm_mode = True


class LoginResponseSchema(BaseModel):
    token: str = Field(..., description="Token")
    refresh_token: str = Field(..., description="Refresh token")
