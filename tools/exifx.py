import PIL.Image
from PIL.ExifTags import TAGS
import pandas as pd
import sys

urls=[]
img = PIL.Image.open('img2.jpg')
exif_data = img._getexif()
print(type(exif_data))
i = 0
for k in exif_data:
    try:
        #print(TAGS[k], exif_data[k])
        urls.append(TAGS[k] + ": "  + str(exif_data[k]))
        i = i + 1
        print(i)

    except Exception as e:
        print(e)

urls=pd.Series(urls)
urls.to_csv("exif.csv")
