from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class User:
	id: int
	username: str
	email: str
	full_name: Optional[str]
	bio: Optional[str]
	location: Optional[str]
	website: Optional[str]
	company: Optional[str]
	avatar_url: Optional[str]
	is_active: bool
