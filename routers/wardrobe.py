from fastapi import APIRouter,HTTPException,status,Depends
from fastapi import File, UploadFile
from typing import List
import secrets
import schemas, models, oauth2
from sqlalchemy.orm import Session
from database import get_db
import os 
from .classification import recognize, suggest_outfit
from sqlalchemy import func,and_


router = APIRouter(prefix="/clothes", tags=["clothes"])



def get_clothes(db: Session, clothes_id: int, user_id : int):
    return db.query(models.Clothes).filter(and_(models.Clothes.owner_id==user_id , models.Clothes.id == clothes_id)).first()

def get_clothes_list(db: Session, user_id : int , skip: int = 0, limit: int = 100):
    return db.query(models.Clothes).filter(models.Clothes.owner_id==user_id).offset(skip).limit(limit).all()

def delete_clothes(db: Session, clothes_id: int, user_id:int):
    imagePath=db.query(models.Clothes.image).filter(models.Clothes.id == clothes_id).scalar()
    os.remove(imagePath)
    db_clothes = db.query(models.Clothes).filter(models.Clothes.id == clothes_id).delete()
    db.commit()
    return print(db_clothes)


def get_category(db: Session, name : str):
    if name in ['hat','dress', 'shirt', 't-shirt', 'longsleeve']:
        return 1
    if name in ['pants','shorts', 'skirt']:
        return 2
    if name in ['shoes']:
        return 3
    if name in ['outwear']:
        return 4




@router.post("/uploadimage/", response_model=schemas.Clothes, status_code=status.HTTP_201_CREATED)
async def create_upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)  ,current_user: schemas.User = Depends(oauth2.get_current_active_user)):
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
    except IOError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=generated_name+" file not found")
    file.close()             
    
    (clothes_name,clothes_weather)=recognize(generated_name)

    category=get_category(db,clothes_name)

    db_clothes = models.Clothes(image=generated_name, owner_id=user_id, name=clothes_name, weather=clothes_weather, category_id=category)
    db.add(db_clothes)
    db.commit()
    db.refresh(db_clothes)
    return db_clothes     




@router.get("/", response_model=List[schemas.Clothes] , status_code=status.HTTP_200_OK)
def read_clothes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),current_user: schemas.User = Depends(oauth2.get_current_active_user)):
    clothes = get_clothes_list(db, user_id=current_user.id, skip=skip, limit=limit)
    return clothes


@router.get("/category", response_model=List[schemas.Clothes] , status_code=status.HTTP_200_OK)
def read_clothes_category(category_id : int,skip: int = 0, limit: int = 100, db: Session = Depends(get_db),current_user: schemas.User = Depends(oauth2.get_current_active_user)):
    clothes = db.query(models.Clothes).filter(and_(models.Clothes.owner_id==current_user.id, models.Clothes.category_id==category_id)).offset(skip).limit(limit).all()
    return clothes


@router.get("/{clothes_id}", response_model=schemas.Clothes, status_code=status.HTTP_200_OK)
def read_clothes(clothes_id: int, db: Session = Depends(get_db),current_user: schemas.User = Depends(oauth2.get_current_active_user)):
    db_clothes = get_clothes(db, clothes_id=clothes_id, user_id=current_user.id)
    if db_clothes is None:
        raise HTTPException(status_code=404, detail="File not found")
    return db_clothes



@router.delete("/{clothes_id}",status_code=status.HTTP_202_ACCEPTED)
def deleted_clothes(clothes_id: int, db: Session = Depends(get_db),current_user: schemas.User = Depends(oauth2.get_current_active_user)):
    db_clothes = get_clothes(db=db, clothes_id=clothes_id, user_id=current_user.id)
    if db_clothes is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    return delete_clothes(db=db, clothes_id=clothes_id, user_id=current_user.id)




@router.get("/outfit/", response_model=List[schemas.Clothes], status_code=status.HTTP_202_ACCEPTED)
def outfit_suggested(clothes_id: int, db: Session = Depends(get_db),current_user: schemas.User = Depends(oauth2.get_current_active_user)):
    img=db.query(models.Clothes.image).filter(and_(models.Clothes.owner_id==current_user.id , models.Clothes.id == clothes_id)).first()[0]
    weather= db.query(models.Clothes.weather).filter(and_(models.Clothes.owner_id==current_user.id , models.Clothes.id == clothes_id)).first()[0]
    option=suggest_outfit(img)
    l=[]
    for to_wear in option:
        result = db.query(models.Clothes).filter(and_(models.Clothes.name==to_wear,models.Clothes.owner_id==current_user.id )).order_by(func.random()).first()
        if result==None:
            result=models.Clothes(name="you don't have a "+to_wear+ " for a "+weather +" weather" , owner_id=current_user.id )
        l.append(result)

    return l
