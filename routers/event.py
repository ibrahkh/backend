from fastapi import APIRouter,HTTPException,status,Depends
from typing import List
import schemas, models, oauth2
from sqlalchemy.orm import Session
from database import get_db
from sqlalchemy import and_
from datetime import date

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/add_event/", response_model=schemas.Events,  status_code=status.HTTP_201_CREATED)
async def create_event(event : schemas.Events_create ,db: Session = Depends(get_db)  ,current_user: schemas.User = Depends(oauth2.get_current_active_user)):
    db_Events = models.Events(name=event.name, date=event.date, owner_id=current_user.id)
    db.add(db_Events)
    db.commit()
    db.refresh(db_Events)
    return db_Events  


@router.get("/", response_model=List[schemas.Events], status_code=status.HTTP_200_OK)
def read_evnt(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_active_user)):
    event=db.query(models.Events).filter(models.Events.owner_id==current_user.id).offset(skip).limit(limit).all()
    return event


@router.put("/{event_id}", response_model=schemas.Events ,status_code=status.HTTP_202_ACCEPTED)
def update_event(event_date: date,event: schemas.Events, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_active_user)):
    db_event = db.query(models.Events).filter(and_(models.Events.owner_id==current_user.id, models.Events.date==event_date )).first()

    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    
    if (event.name):
        db_event.name = event.name
    
    if (event.date):
        db_event.date = event.date

    db.commit()
    db.refresh(db_event)

    return db_event


@router.delete("/{event_id}",status_code=status.HTTP_202_ACCEPTED)
def delete_event(event_date: date, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_active_user)):
    db_event = db.query(models.Events).filter(and_(models.Events.owner_id==current_user.id, models.Events.date==event_date )).first()
    if db_event is None:
        raise HTTPException(status_code=404, detail="User not found")
    deleted_event = db.query(models.Events).filter(and_(models.Events.owner_id==current_user.id, models.Events.date==event_date )).delete()
    db.commit()
    return deleted_event
