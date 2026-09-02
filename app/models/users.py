from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        primary_key=True
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    # Things owned by this user
    folders: Mapped[list["Folder"]] = relationship(
        "Folder",
        back_populates="owner",
        passive_deletes="all",
    )

    files: Mapped[list["File"]] = relationship(
        "File",
        back_populates="owner",
        passive_deletes="all",
    )

    # Shares received by this user
    file_shares_received: Mapped[list["FileShare"]] = relationship(
        "FileShare",
        back_populates="user",
        passive_deletes="all",
    )

    folder_shares_received: Mapped[list["FolderShare"]] = relationship(
        "FolderShare",
        back_populates="user",
        passive_deletes="all",
    )