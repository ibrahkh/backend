import numpy as np
from keras.models import load_model
import random
import models 
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func,and_ 
from tensorflow.keras.preprocessing import image as image_utils
from tensorflow.keras.applications.imagenet_utils import preprocess_input

model = load_model('.//Classifier.h5')

def recognize(path : str):

    image = image_utils.load_img(path, target_size=(224, 224))
    image = image_utils.img_to_array(image)
    image = image.reshape(1,224,224,3)
    image = preprocess_input(image)
    preds = model.predict(image)
    class_names =['dress',

 'hat',
 'longsleeve',
 'outwear',
 'pants',
 'shirt',
 'shoes',
 'shorts',
 'skirt',
 't-shirt']
 
    pre = class_names[np.argmax(preds)]

    weather = {
        'dress' : 'hot',
        'hat'  : 'cool',
        'longsleeve' : 'cold',
        'outwear' : 'cold',
        'pants': 'cool',
        'shirt': 'cool',
        'shoes': 'cool',
        'shorts': 'hot',
        'skirt' : 'hot',
        't-shirt': 'hot'
       }

    j=weather[pre]
    return (pre,j)


def suggest_outfit (image) :

              (i,j) = recognize (image)

              d= {'longsleeve': ['outwear','pants','shoes'],'t-shirt' :['pants','shoes'],'pants': ['longsleeve','shoes'],'shorts':['t-shirt', 'shoes'],'shoes':['longsleeve','pants'],'dress':['shoes'],'outwear' :['longsleeve','pants','shoes'],'skirt':['longsleeve','shoes']}

              return (d[i])



def whole_outfit (genre : str):
              combinaison = {'MALE' :   [('hat','outwear','longsleeve','pants','shoes'),('t-shirt','pants','shoes'),('hat','t-shirt','shorts','shoes'),('outwear','pants','shoes')]

                             ,'FEMALE' : [('t-shirt','pants','shoes'),('t-shirt','skirt','shoes'),('hat','t-shirt','skirt','shoes'),('longsleeve','pants','shoes'),('outwear','longsleeve','skirt','shoes'),('outwear','pants','shoes'),('dress','shoes'),('dress','shoes','hat')]}
              return (combinaison[genre]) 



def suggest(user_id: int, image_path:str,  db : Session):
    img_exist=db.query(models.Clothes.image).filter(and_(models.Clothes.owner_id==user_id, models.Clothes.image == image_path)).first()
    
    if img_exist==None:
        raise HTTPException(status_code=404, detail="File not found")
    img=img_exist[0]
    weather= db.query(models.Clothes.weather).filter(and_(models.Clothes.owner_id==user_id, models.Clothes.image == image_path)).first()[0]
    option=suggest_outfit(img)
    l=[]
    for to_wear in option:
        result = db.query(models.Clothes).filter(and_(models.Clothes.name==to_wear,models.Clothes.owner_id==user_id)).order_by(func.random()).first()
        if result==None:
            raise HTTPException(status_code=404, detail="you don't have a "+to_wear+ " for a "+weather +" weather")
            
        l.append(result)

    return l




def full_outfit_suggest(user_id:int, user_sexe: str, db: Session):
    j=0
    exist_outfit=False
    l=[]

    if user_sexe.upper() not in ["MALE", "FEMALE"]:
        raise HTTPException(status_code=404,detail="the user gendre is not known")
    while (j<100 and exist_outfit==False):
        choice=whole_outfit(user_sexe.upper())
        i=random.randint(0,len(choice)-1)
        option=choice[i]
        l=[]
        for to_wear in option:
            result = db.query(models.Clothes).filter(and_(models.Clothes.name==to_wear,models.Clothes.owner_id==user_id )).order_by(func.random()).first()
            if result==None:
                j=j+1
                break
            l.append(result)
        if (len(l)==len(option)):
            exist_outfit=True
    if j>=100:
        raise HTTPException(status_code=404, detail="we didn't find an outfit for you, update your wardrobe and try again")

    return l