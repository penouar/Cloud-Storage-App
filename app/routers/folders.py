from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session


from app.database import get_db
from app.models.users import User
from app.models.folders import Folder
from app.models.foldershare import FolderShare
from app.schemas.folders import FolderCreate, FolderResponse, FolderUpdate
from app.schemas.foldershare import FolderShareCreate, FolderShareResponse, FolderShareUpdate
from app.security import get_current_user
from app.models.permission import PermissionType

router = APIRouter(
    prefix="/folders",
    tags=["Folder"]
)


def user_has_folder_access(allowed_permissions: list[PermissionType], folder: Folder, current_user: User, db: Session) -> bool:
    current = folder

    while current is not None:
        if current.user_id==current_user.user_id:
            return True

        the_share=db.query(FolderShare).filter(
            FolderShare.folder_id==current.folder_id,
            FolderShare.to_user_id==current_user.user_id
        ).first()

        if the_share:
            if the_share.permission in allowed_permissions:
                return True
            else:
                return False
        else:
            current=db.query(Folder).filter(
                Folder.folder_id==current.parent_folder_id
            ).first()
    
    return False


@router.post("/create", response_model=FolderResponse)
def create(folder_data: FolderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if folder_data.parent_folder_id is not None:
        existing_folder=db.query(Folder).filter(
            (Folder.folder_name == folder_data.folder_name),
            (Folder.parent_folder_id == folder_data.parent_folder_id)
        ).first()

        existing_parent_folder=db.query(Folder).filter(
            (Folder.folder_id==folder_data.parent_folder_id)
        ).first()

        if not existing_parent_folder or existing_parent_folder.user_id != current_user.user_id:
            raise HTTPException(
                status_code=404,
                detail="Parent folder not found")

    else:
        existing_folder=db.query(Folder).filter(
            (Folder.folder_name == folder_data.folder_name)
        ).first()

    if existing_folder and existing_folder.user_id==current_user.user_id:
        raise HTTPException(
            status_code=409,
            detail="Folder Already exists, Rename it please"
        )
    
    new_folder = Folder(

        folder_name=folder_data.folder_name,
        parent_folder_id=folder_data.parent_folder_id,
        user_id= current_user.user_id
    )

    db.add(new_folder)
    db.commit()
    db.refresh(new_folder)

    return new_folder

@router.get("/{folder_id}", response_model=FolderResponse)
def get_folder(folder_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    the_folder = db.query(Folder).filter(
        Folder.folder_id == folder_id
    ).first()

    if the_folder is None:
        raise HTTPException(
            status_code=404, 
            detail="Folder not Found")

    has_access = user_has_folder_access([PermissionType.READ, PermissionType.EDIT], the_folder, current_user, db)

    if not has_access:
        raise HTTPException(status_code=404,
        detail="Folder not Found")

    return the_folder

@router.get("", response_model=list[FolderResponse])
def get_folders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    folders = db.query(Folder).filter(
        Folder.user_id==current_user.user_id
    ).all()
    
    shared_folder_links = db.query(FolderShare).filter(
        FolderShare.to_user_id == current_user.user_id,
        FolderShare.permission.in_([PermissionType.READ, PermissionType.EDIT])
        ).all()

    shared_folders = [link.folder for link in shared_folder_links]

    return folders + shared_folders



@router.patch("/{folder_id}", response_model=FolderResponse)
def update_folder(
    folder_id: int,
    folder_data: FolderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Get the folder
    folder = db.query(Folder).filter(
        Folder.folder_id == folder_id
    ).first()

    if folder is None:
        raise HTTPException(
            status_code=404,
            detail="Folder not Found"
        )

    # 2. Check access
    has_access = user_has_folder_access(
        [PermissionType.EDIT],
        folder,
        current_user,
        db
    )

    if not has_access:
        raise HTTPException(
            status_code=404,
            detail="Folder not Found"
        )

    # 3. Get only fields that were actually provided
    updates = folder_data.model_dump(exclude_unset=True)

    # 4. Validate new parent
    if "parent_folder_id" in updates:
        new_parent_id = updates["parent_folder_id"]

        # Cannot be its own parent
        if new_parent_id == folder.folder_id:
            raise HTTPException(
                status_code=400,
                detail="A folder cannot be its own parent"
            )

        if new_parent_id is not None:

            # Parent must exist and belong to current user
            parent_folder = db.query(Folder).filter(
                Folder.folder_id == new_parent_id,
                Folder.user_id == current_user.user_id
            ).first()

            if parent_folder is None:
                raise HTTPException(
                    status_code=404,
                    detail="Parent folder not found"
                )

            # Check for circular hierarchy
            current_parent = parent_folder

            while current_parent is not None:

                if current_parent.folder_id == folder.folder_id:
                    raise HTTPException(
                        status_code=400,
                        detail="Cannot create circular folder hierarchy"
                    )

                if current_parent.parent_folder_id is None:
                    break

                current_parent = db.query(Folder).filter(
                    Folder.folder_id == current_parent.parent_folder_id
                ).first()

    # 5. Determine final values
    new_name = updates.get(
        "folder_name",
        folder.folder_name
    )

    new_parent_id = updates.get(
        "parent_folder_id",
        folder.parent_folder_id
    )

    # 6. Check duplicate name in same parent
    duplicate = db.query(Folder).filter(
        Folder.user_id == current_user.user_id,
        Folder.folder_name == new_name,
        Folder.parent_folder_id == new_parent_id,
        Folder.folder_id != folder.folder_id
    ).first()

    if duplicate:
        raise HTTPException(
            status_code=409,
            detail="A folder with this name already exists in this parent folder"
        )

    # 7. Apply updates
    for field, value in updates.items():
        setattr(folder, field, value)

    # 8. Save
    db.commit()
    db.refresh(folder)

    return folder

@router.delete("/{folder_id}", status_code=204)
def delete_folder(folder_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    the_folder= db.query(Folder).filter(
            Folder.folder_id==folder_id
        ).first()
    if (the_folder is None) or (the_folder.user_id != current_user.user_id):
        raise HTTPException(
            status_code=404,
            detail="Folder not Found"
        )
    db.delete(the_folder)
    db.commit()

@router.post("/{folder_id}/share", response_model= FolderShareResponse)
def create_foldershare(folder_id: int, user_data: FolderShareCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    the_folder= db.query(Folder).filter(
            Folder.folder_id==folder_id
        ).first()
    if (the_folder is None) or (the_folder.user_id != current_user.user_id):
        raise HTTPException(
            status_code=404,
            detail="Folder not Found"
        )
    if user_data.to_user_id == current_user.user_id:
        raise HTTPException(
            status_code=400, #Check the status code
            detail="Cannot share folder to yourself"
        )
    the_user=db.query(User).filter(
        User.user_id==user_data.to_user_id
    ).first()
    if the_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not Found"
        )
    the_share=db.query(FolderShare).filter(
            FolderShare.folder_id==folder_id,
            FolderShare.to_user_id==user_data.to_user_id
            ).first()
    if the_share:
        raise HTTPException(
            status_code=409,
            detail="Share already exists"
        )
    new_foldershare = FolderShare(
        folder_id=folder_id,
        to_user_id=user_data.to_user_id,
        permission=user_data.permission
    )
    
    db.add(new_foldershare)
    db.commit()
    db.refresh(new_foldershare)
    
    return new_foldershare

@router.get("/{folder_id}/shares", response_model=list[FolderShareResponse])
def get_folder_shares(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    folder = db.query(Folder).filter(
        Folder.folder_id == folder_id
    ).first()

    if folder is None or folder.user_id != current_user.user_id:
        raise HTTPException(
            status_code=404,
            detail="Folder not found"
        )

    shares = db.query(FolderShare).filter(
        FolderShare.folder_id == folder_id
    ).all()

    return shares

@router.patch(
    "/{folder_id}/shares/{to_user_id}",
    response_model=FolderShareResponse
)
def update_folder_share(
    folder_id: int,
    to_user_id: int,
    share_data: FolderShareUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Find folder
    folder = db.query(Folder).filter(
        Folder.folder_id == folder_id
    ).first()

    # Only owner can manage shares
    if folder is None or folder.user_id != current_user.user_id:
        raise HTTPException(
            status_code=404,
            detail="Folder not found"
        )

    # Find share
    share = db.query(FolderShare).filter(
        FolderShare.folder_id == folder_id,
        FolderShare.to_user_id == to_user_id
    ).first()

    if share is None:
        raise HTTPException(
            status_code=404,
            detail="Share not found"
        )

    # Update permission
    share.permission = share_data.permission

    db.commit()
    db.refresh(share)

    return share

@router.delete("/{folder_id}/shares/{to_user_id}", status_code=204)
def delete_folder_share(
    folder_id: int,
    to_user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Find folder
    folder = db.query(Folder).filter(
        Folder.folder_id == folder_id
    ).first()

    # Only owner can revoke access
    if folder is None or folder.user_id != current_user.user_id:
        raise HTTPException(
            status_code=404,
            detail="Folder not found"
        )

    # Find share
    share = db.query(FolderShare).filter(
        FolderShare.folder_id == folder_id,
        FolderShare.to_user_id == to_user_id
    ).first()

    if share is None:
        raise HTTPException(
            status_code=404,
            detail="Share not found"
        )

    db.delete(share)
    db.commit()
