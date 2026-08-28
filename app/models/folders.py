from sqlalchemy import String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Folder(Base):
    __tablename__ = "folder"

    folder_id: Mapped[int] = mapped_column(
        primary_key=True
    )

    folder_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    parent_folder_id: Mapped[int | None] = mapped_column(
        ForeignKey("folder.folder_id", ondelete="CASCADE")
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False
    )

    # Parent folder
    parent: Mapped["Folder | None"] = relationship(
        "Folder",
        back_populates="children",
        remote_side=[folder_id]
    )

    # Child folders
    children: Mapped[list["Folder"]] = relationship(
        "Folder",
        back_populates="parent",
        passive_deletes="all",
    )

    # Owner
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="folders"
    )

    # Files inside this folder
    files: Mapped[list["File"]] = relationship(
        "File",
        back_populates="folder",
        passive_deletes="all",
    )

    # Shares of this folder
    shares: Mapped[list["FolderShare"]] = relationship(
        "FolderShare",
        back_populates="folder",
        passive_deletes="all",
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "parent_folder_id",
            "folder_name",
            name="uq_folder_name"
        ),

        Index(
            "uq_root_folder_name",
            "user_id",
            "folder_name",
            unique=True,
            postgresql_where=parent_folder_id.is_(None)
        ),

        Index(
            "ix_folder_parent_folder_id",
            "parent_folder_id"
        ),

        Index(
            "ix_folder_user_id",
            "user_id"
        ),
    )