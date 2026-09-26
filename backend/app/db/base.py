# app/db/base.py

from sqlalchemy.orm import DeclarativeBase  # type: ignore[reportMissingImports]


class Base(DeclarativeBase):
    pass