from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.auth import get_current_user, require_admin
from app.database import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.get("/", response_model=List[schemas.UserOut])
def list_users(
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    return db.query(models.User).all()
