from pydantic import BaseModel, Field


class GetUserListResponseSchema(BaseModel):
    id: int = Field(..., description="ID")
    email: str = Field(..., description="Email")
    nickname: str = Field(..., description="Nickname")

    class Config:
        orm_mode = True


class GetUserByIdResponseSchema(BaseModel):
    id: int = Field(..., description="ID")
    email: str = Field(..., description="Email")
    first_name: str = Field(..., description="First Name")
    last_name: str = Field(..., description="Last Name")

    class Config:
        orm_mode = True


class RegisterRequestSchema(BaseModel):
    email: str = Field(..., description="Email")
    first_name: str = Field(..., description="First Name")
    last_name: str = Field(..., description="Last Name")
    password: str = Field(..., description="Password")


class RegisterResponseSchema(BaseModel):
    token: str = Field(..., description="Token")
    refresh_token: str = Field(..., description="Refresh Token")


class VerifyOTPRequestSchema(BaseModel):
    otp: str = Field(..., description="OTP")


class VerifyOTPResponseSchema(BaseModel):
    email: str = Field(..., description="Email")
    first_name: str = Field(..., description="First Name")
    last_name: str = Field(..., description="Last Name")


class LoginResponseSchema(BaseModel):
    token: str = Field(..., description="Token")
    refresh_token: str = Field(..., description="Refresh Token")


class ResendOTPResponseSchema(BaseModel):
    token: str = Field(..., description="Token")
    refresh_token: str = Field(..., description="Refresh Token")


class VerifyEmailRequestSchema(BaseModel):
    email: str = Field(..., description="Email")


class VerifyEmailResponseSchema(BaseModel):
    token: str = Field(..., description="Token")
    refresh_token: str = Field(..., description="Refresh Token")
