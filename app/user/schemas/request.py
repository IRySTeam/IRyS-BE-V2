from pydantic import BaseModel, Field


class RegisterRequestSchema(BaseModel):
    email: str = Field(..., description="Email")
    first_name: str = Field(..., description="First Name")
    last_name: str = Field(..., description="Last Name")
    password: str = Field(..., description="Password")


class LoginRequestSchema(BaseModel):
    email: str = Field(..., description="Email")
    password: str = Field(..., description="Password")
    

class VerifyOTPRequestSchema(BaseModel):
    otp: str = Field(..., description="OTP")


class VerifyEmailRequestSchema(BaseModel):
    email: str = Field(..., description="Email")


class SendForgotPasswordOTPRequestSchema(BaseModel):
    email: str = Field(..., description="Email")


class VerifyForgotPasswordOTPRequestSchema(BaseModel):
    otp: str = Field(..., description="OTP")


class ChangePasswordRequestSchema(BaseModel):
    new_password: str = Field(..., description="New Password")
    confirm_new_password: str = Field(..., description="Confirm New Password")


