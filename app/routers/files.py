from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.users import User
from app.models.files import File
from app.models.folders import Folder
from app.schemas.files import FileCreate, FileResponse, FileUpdate
from app.security import get_current_user

from app.models.fileshare import FileShare
from app.schemas.fileshare import FileShareCreate, FileShareUpdate, FileShareResponse
from app.models.permission import PermissionType
from app.routers.folders import user_has_folder_access



router = APIRouter(
    prefix="/files",
    tags=["File"]
)



def user_has_file_access(allowed_permissions: list[PermissionType], file: File, current_user: User, db: Session) -> bool:
    if file.user_id==current_user.user_id:
        return True

    the_share=db.query(FileShare).filter(
        FileShare.file_id==file.file_id,
        FileShare.to_user_id==current_user.user_id
    ).first()

    if the_share:
        if the_share.permission in allowed_permissions:
            return True
        else:
            return False
    the_folder=db.query(Folder).filter(
        Folder.folder_id==file.folder_id
    ).first()
    if the_folder:
        return user_has_folder_access(allowed_permissions, the_folder, current_user, db)
    else:
        return False



@router.post("/create", response_model=FileResponse)
def create_file(file_data: FileCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    if file_data.folder_id is not None:

        existing_folder = db.query(Folder).filter(
            Folder.folder_id == file_data.folder_id,
            Folder.user_id == current_user.user_id
        ).first()

        if existing_folder is None:
            raise HTTPException(
                status_code=404,
                detail="Folder not found"
            )

    existing_file = db.query(File).filter(
        File.file_name == file_data.file_name,
        File.folder_id == file_data.folder_id,
        File.user_id == current_user.user_id
    ).first()

    if existing_file:
        raise HTTPException(
            status_code=409,
            detail="A file with this name already exists in this folder"
        )

    # Create the file
    new_file = File(
        file_name=file_data.file_name,
        file_size=file_data.file_size,
        file_type=file_data.file_type,
        folder_id=file_data.folder_id,
        user_id=current_user.user_id
    )

    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    return new_file


@router.get("/{file_id}", response_model=FileResponse)
def get_file(file_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 1. Fetch the file by ID
    the_file = db.query(File).filter(
        File.file_id == file_id
    ).first()

    # 2. File doesn't exist
    if the_file is None:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    # 3. Check whether the user has READ or EDIT access
    has_access = user_has_file_access([PermissionType.READ, PermissionType.EDIT], the_file, current_user, db)

    # 4. User doesn't have permission
    if not has_access:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    return the_file


@router.get("", response_model=list[FileResponse])
def get_files(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    files = db.query(File).filter(
        File.user_id == current_user.user_id
    ).all()
    shared_files_links =db.query(FileShare).filter(
        FileShare.to_user_id == current_user.user_id,
        FileShare.permission.in_([PermissionType.READ, PermissionType.EDIT])
        ).all()
    
    shared_files = [link.file for link in shared_files_links]

    return files + shared_files
   

@router.patch("/{file_id}", response_model=FileResponse)
def update_file(
    file_id: int,
    file_data: FileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Fetch the file by ID only
    the_file = db.query(File).filter(
        File.file_id == file_id
    ).first()

    # 2. File doesn't exist
    if the_file is None:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    # 3. User must have EDIT permission
    has_access = user_has_file_access(
        [PermissionType.EDIT],
        the_file,
        current_user,
        db
    )

    # 4. No EDIT access
    if not has_access:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    updates = file_data.model_dump(exclude_unset=True)

    if "folder_id" in updates:
        new_folder_id = updates["folder_id"]

        if new_folder_id is not None:
            new_folder = db.query(Folder).filter(
                Folder.folder_id == new_folder_id,
                Folder.user_id == current_user.user_id
            ).first()

            if new_folder is None:
                raise HTTPException(
                    status_code=404,
                    detail="Folder not found"
                )

    new_name = updates.get(
        "file_name",
        the_file.file_name
    )

    new_folder_id = updates.get(
        "folder_id",
        the_file.folder_id
    )

    duplicate = db.query(File).filter(
        File.user_id == current_user.user_id,
        File.file_name == new_name,
        File.folder_id == new_folder_id,
        File.file_id != the_file.file_id
    ).first()

    if duplicate:
        raise HTTPException(
            status_code=409,
            detail="A file with this name already exists in this folder"
        )

    # Apply updates
    for field, value in updates.items():
        setattr(the_file, field, value)

    db.commit()
    db.refresh(the_file)

    return the_file


@router.delete("/{file_id}", status_code=204)
def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Find the file and verify ownership
    the_file = db.query(File).filter(
        File.file_id == file_id,
        File.user_id == current_user.user_id
    ).first()

    if the_file is None:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    db.delete(the_file)
    db.commit()


@router.post("/{file_id}/share", response_model=FileShareResponse)
def create_fileshare(file_id: int, user_data: FileShareCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    the_file = db.query(File).filter(
        File.file_id == file_id
    ).first()

    if the_file is None or the_file.user_id != current_user.user_id:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    if user_data.to_user_id == current_user.user_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot share file to yourself"
        )

    the_user = db.query(User).filter(
        User.user_id == user_data.to_user_id
    ).first()

    if the_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    the_share = db.query(FileShare).filter(
        FileShare.file_id == file_id,
        FileShare.to_user_id == user_data.to_user_id
    ).first()

    if the_share:
        raise HTTPException(
            status_code=409,
            detail="Share already exists"
        )

    new_fileshare = FileShare(
        file_id=file_id,
        to_user_id=user_data.to_user_id,
        permission=user_data.permission
    )

    db.add(new_fileshare)
    db.commit()
    db.refresh(new_fileshare)

    return new_fileshare


@router.get("/{file_id}/shares", response_model=list[FileShareResponse])
def get_file_shares(file_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    the_file = db.query(File).filter(
        File.file_id == file_id
    ).first()

    if the_file is None or the_file.user_id != current_user.user_id:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    shares = db.query(FileShare).filter(
        FileShare.file_id == file_id
    ).all()

    return shares


@router.patch("/{file_id}/shares/{to_user_id}", response_model=FileShareResponse)
def update_file_share(file_id: int, to_user_id: int, share_data: FileShareUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    the_file = db.query(File).filter(
        File.file_id == file_id
    ).first()

    if the_file is None or the_file.user_id != current_user.user_id:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    the_share = db.query(FileShare).filter(
        FileShare.file_id == file_id,
        FileShare.to_user_id == to_user_id
    ).first()

    if the_share is None:
        raise HTTPException(
            status_code=404,
            detail="Share not found"
        )

    the_share.permission = share_data.permission

    db.commit()
    db.refresh(the_share)

    return the_share


@router.delete("/{file_id}/shares/{to_user_id}", status_code=204)
def delete_file_share(file_id: int, to_user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    the_file = db.query(File).filter(
        File.file_id == file_id
    ).first()

    if the_file is None or the_file.user_id != current_user.user_id:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    the_share = db.query(FileShare).filter(
        FileShare.file_id == file_id,
        FileShare.to_user_id == to_user_id
    ).first()

    if the_share is None:
        raise HTTPException(
            status_code=404,
            detail="Share not found"
        )

    db.delete(the_share)
    db.commit()

