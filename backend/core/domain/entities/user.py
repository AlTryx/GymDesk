from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UserEntity:
    id: Optional[int]
    email: str
    first_name: str
    last_name: str
    password_hash: str
    role: str
    created_at: Optional[datetime] = None

    def __post_init__(self):
        self._validate()

    def _validate(self):
        # Only validate strictly for newly created entities (id is None).
        # When mapping from the database (existing users), skip strict
        # validation because legacy records or admin-created users may
        # have empty first/last names.
        if self.id is None:
            # Email validation
            if not self.email or '@' not in self.email:
                raise ValueError("Email трябва да съдържа @")

            # Name validation
            if not self.first_name or len(self.first_name.strip()) < 2:
                raise ValueError("Името трябва да е поне 2 символа")

            if not self.last_name or len(self.last_name.strip()) < 2:
                raise ValueError("Фамилията трябва да е поне 2 символа")

            # Role validation
            if self.role not in ['USER', 'ADMIN']:
                raise ValueError(f"Role трябва да е USER или ADMIN, а не '{self.role}'")

            # Password hash validation
            if not self.password_hash:
                raise ValueError("Password hash не може да е празен")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def is_admin(self) -> bool:
        return self.role == 'ADMIN'

    def can_manage_resources(self) -> bool:
        return self.is_admin()

    def can_view_all_reservations(self) -> bool:
        return self.is_admin()