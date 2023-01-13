import numpy as np

from keras.models import load_model

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

        'dress' :'hot' ,

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