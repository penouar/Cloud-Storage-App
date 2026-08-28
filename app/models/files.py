from sqlalchemy import (
    String,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class File(Base):
    __tablename__ = "files"

    file_id: Mapped[int] = mapped_column(
        primary_key=True
    )

    file_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    file_size: Mapped[int] = mapped_column(
        nullable=False
    )

    file_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    folder_id: Mapped[int | None] = mapped_column(
        ForeignKey("folder.folder_id", ondelete="CASCADE")
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False
    )

    # Folder relationship
    folder: Mapped["Folder | None"] = relationship(
        "Folder",
        back_populates="files"
    )

    # Owner relationship
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="files"
    )

    # Shares received by other users
    shares: Mapped[list["FileShare"]] = relationship(
        "FileShare",
        back_populates="file",
        passive_deletes="all",
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "folder_id",
            "file_name",
            name="uq_file_name"
        ),

        CheckConstraint(
            "file_size >= 0",
            name="chk_size"
        ),

        Index("ix_files_folder_id", "folder_id"),
        Index("ix_files_user_id", "user_id"),

        Index(
            "uq_root_file_name",
            "user_id",
            "file_name",
            unique=True,
            postgresql_where=folder_id.is_(None)
        ),
    )