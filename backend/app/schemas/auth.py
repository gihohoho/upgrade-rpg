from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator, model_validator


USERNAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_]{3,23}$")
OPAQUE_EMAIL_TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_-]{32,256}$")


class EmailValidationUnavailable(RuntimeError):
    """Raised when the approved email-validator package is not installed yet."""


@dataclass(frozen=True)
class NormalizedEmail:
    original: str
    canonical: str


def normalize_username(value: str) -> str:
    normalized = str(value or "").strip().lower()
    if not USERNAME_PATTERN.fullmatch(normalized):
        raise ValueError(
            "아이디는 영문 소문자 또는 숫자로 시작하고, "
            "영문 소문자·숫자·_만 사용해 4~24자로 입력해주세요."
        )
    return normalized


def normalize_email_identity(value: str) -> NormalizedEmail:
    """Validate and normalize an email without importing an unapproved package at startup."""
    original = str(value or "").strip()
    if not original or len(original) > 254 or "\r" in original or "\n" in original:
        raise ValueError("올바른 이메일 주소를 입력해주세요.")
    try:
        from email_validator import EmailNotValidError, validate_email
    except ImportError as exc:
        raise EmailValidationUnavailable("email_validator_dependency_missing") from exc

    try:
        validated = validate_email(original, check_deliverability=False)
    except EmailNotValidError as exc:
        raise ValueError("올바른 이메일 주소를 입력해주세요.") from exc
    canonical = str(validated.normalized or "").strip().casefold()
    if not canonical or len(canonical) > 254:
        raise ValueError("올바른 이메일 주소를 입력해주세요.")
    return NormalizedEmail(original=original, canonical=canonical)


def _validate_email_input(value: str) -> str:
    """Use full validation when installed; defer an unavailable dependency to HTTP 503."""
    original = str(value or "").strip()
    if not original or len(original) > 254 or "\r" in original or "\n" in original:
        raise ValueError("올바른 이메일 주소를 입력해주세요.")
    try:
        return normalize_email_identity(original).original
    except EmailValidationUnavailable:
        # The service repeats validation and converts this exact condition to a
        # fail-closed 503. Do not silently substitute a weaker email parser.
        return original


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


def validate_login_password(value: SecretStr) -> SecretStr:
    password = value.get_secret_value()
    if not password or len(password.encode("utf-8")) > 72:
        raise ValueError("아이디 또는 비밀번호가 올바르지 않습니다.")
    return value


def validate_opaque_email_token(value: SecretStr) -> SecretStr:
    token = value.get_secret_value().strip()
    if not OPAQUE_EMAIL_TOKEN_PATTERN.fullmatch(token):
        raise ValueError("메일 링크 토큰 형식이 올바르지 않습니다.")
    return SecretStr(token)


class RegisterRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True, extra="forbid")

    username: str = Field(min_length=4, max_length=24)
    email: str = Field(min_length=3, max_length=254)
    password: SecretStr
    password_confirm: SecretStr = Field(alias="passwordConfirm")

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        return normalize_username(value)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return _validate_email_input(value)

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
    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True, extra="forbid")

    identifier: str = Field(min_length=3, max_length=254)
    password: SecretStr

    @field_validator("identifier")
    @classmethod
    def validate_identifier(cls, value: str) -> str:
        normalized = str(value or "").strip()
        return _validate_email_input(normalized) if "@" in normalized else normalize_username(normalized)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: SecretStr) -> SecretStr:
        return validate_login_password(value)


class EmailRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    email: str = Field(min_length=3, max_length=254)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return _validate_email_input(value)


class EmailTokenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: SecretStr

    @field_validator("token")
    @classmethod
    def validate_token(cls, value: SecretStr) -> SecretStr:
        return validate_opaque_email_token(value)


class PasswordResetRequest(EmailTokenRequest):
    password: SecretStr
    password_confirm: SecretStr = Field(alias="passwordConfirm")

    @field_validator("password", "password_confirm")
    @classmethod
    def validate_password(cls, value: SecretStr) -> SecretStr:
        return validate_password_value(value)

    @model_validator(mode="after")
    def validate_password_confirmation(self) -> "PasswordResetRequest":
        if self.password.get_secret_value() != self.password_confirm.get_secret_value():
            raise ValueError("비밀번호 확인이 일치하지 않습니다.")
        return self


class AccountDeletionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    password: SecretStr

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: SecretStr) -> SecretStr:
        return validate_login_password(value)


class AccountDeletionConfirmRequest(EmailTokenRequest):
    confirm_text: Literal["계정 삭제"] = Field(alias="confirmText")


class AuthUser(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    username: str
    email: str | None = None
    email_verified: bool = Field(default=False, alias="emailVerified")
    is_admin: bool = Field(alias="isAdmin")


class AuthToken(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    access_token: str = Field(alias="accessToken")
    token_type: str = Field(default="bearer", alias="tokenType")
    expires_in: int = Field(alias="expiresIn")
