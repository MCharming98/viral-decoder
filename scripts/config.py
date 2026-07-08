import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class XConfig:
    bearer_token: str | None
    api_key: str | None
    api_secret: str | None
    access_token: str | None
    access_token_secret: str | None
    base_url: str = "https://api.x.com/2"

    @classmethod
    def from_env(cls) -> "XConfig":
        return cls(
            bearer_token=os.getenv("X_BEARER_TOKEN"),
            api_key=os.getenv("X_API_KEY"),
            api_secret=os.getenv("X_API_SECRET"),
            access_token=os.getenv("X_ACCESS_TOKEN"),
            access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET"),
        )

    def require_bearer_token(self) -> str:
        if not self.bearer_token:
            raise ValueError("X_BEARER_TOKEN is required for read-only API access")
        return self.bearer_token
