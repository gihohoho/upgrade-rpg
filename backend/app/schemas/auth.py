from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator, model_validator


USERNAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_]{3,23}$")


def normalize_username(value: str) -> str:
    normalized = str(value or "").strip().lower()
    if not USERNAME_PATTERN.fullmatch(normalized):
        raise ValueError("아이디는 영문 소문자 또는 숫자로 시작하고, 영문 소문자·숫자·_만 사용해 4~24자로 입력해주세요.")
    return normalized


def validate_password_value(value: SecretStr) -> SecretStr:
    password = value.get_secret_value()
    if len(password) < 8:
        raise ValueError("비밀번호는 8자 이상이어야 합니다.")
    if len(password.encode("utf-8")) > 72:
        raise ValueError("비밀번호는 UTF-8 기준 72바이트 이하여야 합니다.")
    if not any(character.isalpha() for character in password):
        raise ValueError("비밀번호에는 문자가 1개 이상 필요합니다.")
    if not any(character.isdigit() for character in password):
        raise ValueError("비밀번호에는 숫자가 1개 이상 필요합니다.")
    return value


class RegisterRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    username: str = Field(min_length=4, max_length=24)
    password: SecretStr
    password_confirm: SecretStr = Field(alias="passwordConfirm")

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        return normalize_username(value)

    @field_validator("password", "password_confirm")
    @classmethod
    def validate_password(cls, value: SecretStr) -> SecretStr:
        return validate_password_value(value)

    @model_validator(mode="after")
    def validate_password_confirmation(self) -> "RegisterRequest":
        if self.password.get_secret_value() != self.password_confirm.get_secret_value():
            raise ValueError("비밀번호 확인이 일치하지 않습니다.")
        return self


class LoginRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    username: str = Field(min_length=4, max_length=24)
    password: SecretStr

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        return normalize_username(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: SecretStr) -> SecretStr:
        password = value.get_secret_value()
        if not password or len(password.encode("utf-8")) > 72:
            raise ValueError("아이디 또는 비밀번호가 올바르지 않습니다.")
        return value


class AuthUser(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    username: str
    is_admin: bool = Field(alias="isAdmin")


class AuthToken(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    access_token: str = Field(alias="accessToken")
    token_type: str = Field(default="bearer", alias="tokenType")
    expires_in: int = Field(alias="expiresIn")
