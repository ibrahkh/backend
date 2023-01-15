from fastapi import APIRouter, status, Depends, HTTPException, UploadFile, File
import schemas, models, oauth2
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import get_db
from datetime import date
import secrets
from sqlalchemy import and_

def get_age(birth_date):
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/User", tags=["User"])


def show_user(id:int,db:Session):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with the id {id} is not available")
    return user


@router.post("/", status_code=status.HTTP_201_CREATED)
def create(request : schemas.User , db: Session = Depends(get_db)):
    email = db.query(models.User).filter(models.User.email==request.email).first()
    if email : 
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="User is already exist")
    new_user=models.User(username=request.username, email=request.email, hashed_password=pwd_context.hash(request.hashed_password),  birth_date=request.birth_date, sexe=request.sexe)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get('/user_id', status_code=status.HTTP_200_OK)
def get_user_id(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_active_user)):
    return current_user.id



@router.get('/{id}',response_model=schemas.ShowUser, status_code=status.HTTP_200_OK)
def get_user(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_active_user)):
    user = show_user(current_user.id, db)
    user_age = get_age(user.birth_date)
    return {
        'username': user.username,
        'email': user.email,
        'sexe': user.sexe,
        'age': user_age,
        'image': user.image

    }



@router.put("/{id}/uploadimage/", response_model=schemas.User_image, status_code=status.HTTP_201_CREATED)
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)  ,current_user: schemas.User = Depends(oauth2.get_current_active_user)):
    user_id=current_user.id
    Filepath=".//static//images//"
    filename=file.filename
    extention=filename.split('.')[1]
    if  (extention.upper() not in ['PNG', 'JPG', 'JPEG','JFIF'] ):

        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                            detail=extention+" is not supported")

    token_name=secrets.token_hex(10)+"."+extention
    generated_name=Filepath+token_name

    file_content=await file.read()
    try:
        with open(generated_name,"wb") as file:
            file.write(file_content)
    except IOError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=generated_name+" file not found")
    file.close()             
    
    db_user = db.query(models.User).filter(models.User.id==user_id).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail="user not found")

    db_user.image=generated_name

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user     



