from sqlalchemy import ForeignKey, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from .permission import PermissionType


class FolderShare(Base):
    __tablename__ = "foldershare"

    folder_id: Mapped[int] = mapped_column(
        ForeignKey("folder.folder_id", ondelete="CASCADE"),
        primary_key=True
    )

    to_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True
    )

    permission: Mapped[PermissionType] = mapped_column(
        Enum(
            PermissionType,
            name="perm_type"
        ),
        nullable=False
    )

    # Folder being shared
    folder: Mapped["Folder"] = relationship(
        "Folder",
        back_populates="shares"
    )

    # User receiving the share
    user: Mapped["User"] = relationship(
        "User",
        back_populates="folder_shares_received"
    )

    __table_args__ = (
        Index(
            "ix_foldershare_to_user_id",
            "to_user_id"
        ),
    )