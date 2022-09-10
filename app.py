import telebot
import cv2
import numpy
from fer import FER
import validators
import requests
import urllib.request as ur
import os


bot=telebot.TeleBot(API_KEY)


@bot.message_handler(commands=['working'])
def greet(message):
    bot.reply_to(message,'send a photo, or url [your_image url]\nWe will start processing and send you result as image and all emoji relateds')


@bot.message_handler(commands=['start'])
def greet(message):
    bot.reply_to(message,'Welcome to F-Moji')


def getmessage(message):
    request=message.text.split()
    if(len(request)<2 or request[0].lower() not in 'url'):
        return False
    else:
        return True


def download_image(url, file_name):
    try:
        full_path='come/'+str(file_name)+'.jpg'
        ur.urlretrieve(url, full_path)
        return True
    except  Exception as e:
        print(e)
        return False


def fer(imgname):
    try:
        imgname=str(imgname)+'.jpg'
        faceCascade=cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        font=cv2.FONT_HERSHEY_SIMPLEX
        cam=cv2.VideoCapture(0)
        cam.set(3, 640)
        cam.set(4, 480)
        minW=0.1*cam.get(3)
        minH=0.1*cam.get(4)
        img=cv2.imread("come/"+imgname)
        gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        faces=faceCascade.detectMultiScale(gray, scaleFactor = 1.2, minNeighbors = 5, minSize = (int(minW), int(minH)),)
        ferr=FER(mtcnn=True)
        r=ferr.detect_emotions(img)
        pi=len(r)
        name= ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        emolist=["meow"]
        vallist=[0]
        query='len='+str(pi)
        for pii in range(0,pi):
            rol=r[pii]
            rrrr=0
            rrra='none'
            for pki in name:
                ap=rol["emotions"][pki]                
                if(ap>rrrr):
                    rrrr=ap
                    rrra=pki
            emolist.append(rrra)
            vallist.append(int(rrrr*100))
            query=query+'&emo'+str(pii+1)+'='+rrra+'&per'+str(pii+1)+'='+str(int(rrrr*100))
        pika=0
        for(x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
            pika=pika+1
            id=emolist[pika]
            justper=vallist[pika]
            cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
            cv2.putText(img, str(str(justper)+"%"), (x+5,y+h-5), font, 1, (255,255,0), 1)
        cv2.imwrite("store/"+imgname,img)
        #os.system('clear')   #for linux
        os.system('CLS')      #for windows
        return query
    except  Exception as e:
        print(e)
        return False


@bot.message_handler(func=getmessage)
def sm(message):
    try:
        request=message.text.split()
        if(validators.url(request[1])==True):
            image_formats = ("image/png", "image/jpeg", "image/jpg")
            r=requests.head(request[1])
            if r.headers["content-type"] in image_formats:
                bot.send_message(message.chat.id,'URL Working, Process Started')
                if(download_image(request[1], message.chat.id)==True):
                    bot.send_message(message.chat.id,'Image Recived by URL, scanning image,')
                    rfer=fer(message.chat.id)
                    if(rfer!=False):
                        imgname=str(message.chat.id)+".jpg"
                        bot.send_message(message.chat.id,'Done, Sending image and deleting from our side and then emoji results. 😁')
                        bot.send_photo(message.chat.id,photo=open("store/"+imgname, 'rb'))
                        os.remove("come/"+imgname)
                        os.remove("store/"+imgname)
                        link='http://localhost/fmoji?'+rfer
                        f=ur.urlopen(link)
                        emoji=f.read()
                        bot.send_message(message.chat.id,emoji)
                    else:
                        bot.send_message(message.chat.id,'Failed, Maybe not able to detect face or emotion.')
                else:
                    bot.send_message(message.chat.id,'Retrive Image Failed')
            else:
                bot.send_message(message.chat.id,'URL may not contain image or not a valid format, we accept PNG, JPEG & JPG.')
        else:
            bot.send_message(message.chat.id,'Not a Valid URL')
    except  Exception as e:
        bot.send_message(message.chat.id,'Unexpectted Error Occur, Try again or after sometime.')


@bot.message_handler(content_types=['photo'])
def photo(message):
    print('message.photo =', message.photo)
    fileID = message.photo[-1].file_id
    print('fileID =', fileID)
    file_info = bot.get_file(fileID)
    print('file.file_path =', file_info.file_path)
    downloaded_file = bot.download_file(file_info.file_path)
    with open("image.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)
bot.polling()
