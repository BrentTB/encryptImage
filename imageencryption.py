import numpy as np
from PIL import Image
import random

red = [255,0,0]
green = [0,255,0]
blue = [0,0,255]
white = [255,255,255]
black = [0,0,0]

path = 'ImageEncryption/'

baseUse = 3 # make it that it can change how many pixels are used, the smaller, the closer to the origional but less text can be held


def decimalToTern(decimal, length):
    numTer = str(np.base_repr(decimal,base=3))
    while (len(numTer) < length):
        numTer = '0'+numTer
    return numTer

def ternToDecimal(tern):
    numTer=0
    for num in map(int, tern):
         numTer = 3 * numTer + num
    return numTer

def decryptPoly(ciphertext, key):

    index=0
    newStr = ''
    for letter in ciphertext:
        num = ternToDecimal(letter)
        shift = key[index]
        if num - shift <0:
            num= num - shift + 243
            newStr += chr(num)
        else:
            num= num - shift
            newStr += chr(num)
        index = (index+1)%len(key)

    return newStr

def encryptPoly(plaintext, key):

    index=0
    newStr = []
    for letter in plaintext:
        shift = key[index]
        if ord(letter) + shift >243:
            num= ord(letter) + shift - 243
            newStr.append(decimalToTern(num,5))
        else:
            num= ord(letter) + shift
            newStr.append(decimalToTern(num,5))
        index = (index+1)%len(key)

    return newStr

def encryptImage(image_name, text, newName):

    keys = []
    ternary=[]

    for i in range(8):
        num = random.randint(0,26)
        keys.append(i*10+num)
        ternary.append(decimalToTern(num,3))

    im = Image.open(image_name)
    width, height = im.size
    pixelTmp = np.asarray(im).copy()

    if len(text) > width*height/2 - 5:
        print('The text is too large. Please plit it into multiple pieces or choose a smaller text')

    ciphertext = encryptPoly(text,keys)
    index = 0

    inMiddle=False
    done=False
    for y in range(height):
        for x in range(width):

            # 255 is divisible by 3, so if it is 255, it would break when adding 1 or 2
            pixelTmp[y,x][0] = 254 if  pixelTmp[y,x][0]==255 else pixelTmp[y,x][0]
            pixelTmp[y,x][1] = 254 if  pixelTmp[y,x][1]==255 else pixelTmp[y,x][1]
            pixelTmp[y,x][2] = 254 if  pixelTmp[y,x][2]==255 else pixelTmp[y,x][2]

            # adding keys to the image
            if (y==0 and x<8):

                pixelTmp[y,x][0] = pixelTmp[y,x][0] - pixelTmp[y,x][0]%3 + (ord(ternary[x][0])-ord('0'))
                pixelTmp[y,x][1] = pixelTmp[y,x][1] - pixelTmp[y,x][1]%3 + (ord(ternary[x][1])-ord('0'))
                pixelTmp[y,x][2] = pixelTmp[y,x][2] - pixelTmp[y,x][2]%3 + (ord(ternary[x][2])-ord('0'))

                continue
                
            
            if done and not inMiddle:
                # randomise all 3 pixels

                pixelTmp[y,x][0]-=pixelTmp[y,x][0]%3-random.randint(0,2)
                pixelTmp[y,x][1]-=pixelTmp[y,x][1]%3-random.randint(0,2)
                pixelTmp[y,x][2]-=pixelTmp[y,x][2]%3-random.randint(0,2)

                continue

            # not done yet 
            if not inMiddle:
                if (index == len(ciphertext)-1):
                    pixelTmp[y,x][0]-=pixelTmp[y,x][0]%3-2 # -> showing its the end of the word
                    done = True
                    print(f'place it stopped: (y,x) = ({y},{x})')
                else:
                    pixelTmp[y,x][0]-=pixelTmp[y,x][0]%3 - random.randint(0,1)

                pixelTmp[y,x][1]-=pixelTmp[y,x][1]%3 - (ord(ciphertext[index][0])-ord('0'))
                pixelTmp[y,x][2]-=pixelTmp[y,x][2]%3 - (ord(ciphertext[index][1])-ord('0'))

            else:

                pixelTmp[y,x][0]-=pixelTmp[y,x][0]%3 - (ord(ciphertext[index][2])-ord('0'))
                pixelTmp[y,x][1]-=pixelTmp[y,x][1]%3 - (ord(ciphertext[index][3])-ord('0'))
                pixelTmp[y,x][2]-=pixelTmp[y,x][2]%3 - (ord(ciphertext[index][4])-ord('0'))

                index+=1

            inMiddle = not inMiddle

    output_image = Image.fromarray(np.uint8(pixelTmp))
    output_image.save(newName)

def decryptImage(image_name):

    im = Image.open(image_name)
    width, height = im.size
    pixelTmp = np.asarray(im).copy()

    keys=[]
    for x in range(8):
        tern = str(pixelTmp[0,x][0]%3)+str(pixelTmp[0,x][1]%3)+str(pixelTmp[0,x][2]%3)
        num = ternToDecimal(tern)
        keys.append(num+x*10)

    inMiddle=False
    done=False

    ciphertext=[]    
    index = 0

    for y in range(height):
        if done:
            break
        for x in range(width):
            if done and not inMiddle:
                break

            # We have already delt with the keys
            if (y==0 and x<8):
                continue

            if not inMiddle:
                # This is the last letter
                if (pixelTmp[y,x][0]%3==2):
                    done=True
                
                txt = str(pixelTmp[y,x][1]%3)+str(pixelTmp[y,x][2]%3)
                ciphertext.append(txt)
            else:

                txt = str(pixelTmp[y,x][0]%3)+str(pixelTmp[y,x][1]%3)+str(pixelTmp[y,x][2]%3)
                ciphertext[index]+=txt
                index+=1

            inMiddle = not inMiddle

    return decryptPoly(ciphertext,keys)



if __name__ == '__main__':

    with open(path+'Harry_Potter_1.txt', 'r') as file:
    # Read in the contents of the file
        text = file.read()
    image_name='earth.jpg'


    # text='Hi'
    # image_name = 'gradient.png'


    newName = ('encrypt-'+image_name).replace('.jpg','.png') # jpg's dont work, so I convert everything to png
    encryptImage(path+image_name, text, path+newName)

    print(decryptImage(path+newName)[:200]) # print the first 200 charaters of the text



    # digit 1:
    # 0 -> randomly chosen. This could carry more info
    # 1 -> 
    # 2 -> this pixel is the end of message

    # first 8 pixels, 4 pixels per key, and each key has 4 numbers for each pixel

