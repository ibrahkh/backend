from fastapi import FastAPI
import models
from database import SessionLocal, engine
from fastapi.staticfiles import StaticFiles


from routers import user, Login, wardrobe, event, categories



models.Base.metadata.create_all(bind=engine)

app=FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(user.router)
app.include_router(Login.router)
app.include_router(wardrobe.router)
app.include_router(event.router)
app.include_router(categories.router)







