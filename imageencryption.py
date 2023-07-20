import numpy as np
from PIL import Image
import random

# folders to store text and images
txtPath = 'ImageEncryption/Text/'
imgPath = 'ImageEncryption/Images/'

def main():
    image_name='earth.jpg'
    newName = imgPath+('encrypt-'+image_name).replace('.jpg','.png') # jpg's dont work, so I convert everything to png
    image_name = imgPath+image_name

    type = 'd'

    if type == 'e':

        # Encrypt the text of the first Harry Potter novel
        with open(txtPath+'Harry_Potter_1.txt', 'r') as file:
            text = file.read()
        encryptImage(image_name, text, newName)

    else:
        print(decryptImage(newName)[:2000]) # print the first 2000 charaters of the text

# convert a char into its equivalent integer 
def charToInt(char):
    return ord(char)-ord('0')

# convert a (int) decimal number into a (string) ternion number
def decimalToTern(decimal, length):
    numTer = str(np.base_repr(decimal,base=3))
    while (len(numTer) < length):
        numTer = '0'+numTer
    return numTer

# convert a (string) ternion number into a (int) decimal number
def ternToDecimal(tern):
    numTer=0
    for num in map(int, tern):
         numTer = 3 * numTer + num
    return numTer

# encrypt a text using a polyalphabetic cipher with a key
def encryptPoly(plaintext, key):
    textIndex=0
    newStr = []

    # shift each letter in the ciphertext by the equivalent char in the key
    for letter in plaintext:
        shift = key[textIndex]
        if ord(letter) + shift >243:
            num= ord(letter) + shift - 243
            newStr.append(decimalToTern(num,5))
        else:
            num= ord(letter) + shift
            newStr.append(decimalToTern(num,5))

        # when the full key has been used, repeat
        textIndex = (textIndex+1)%len(key)
    return newStr

# decrypt a polyalphabetic cipher using a key
def decryptPoly(ciphertext, key):
    textIndex=0
    newStr = ''

    # shift each letter in the ciphertext by the equivalent char in the key
    for letter in ciphertext:
        num = ternToDecimal(letter)
        shift = key[textIndex]

        # overflow characters if needed
        if num - shift <0:
            num= num - shift + 243
            newStr += chr(num)
        else:
            num= num - shift
            newStr += chr(num)
        
        # when the full key has been used, repeat
        textIndex = (textIndex+1)%len(key)
    return newStr

# encrypt text into an image and save the new image
def encryptImage(image_name, text, newName):

    keys, ternary = [], []

    # generate a random key that will be used to encrypot the text for extra security. 
    for i in range(8):
        num = random.randint(0,26)
        keys.append(i*10+num)
        ternary.append(decimalToTern(num,3))

    im = Image.open(image_name)
    width, height = im.size
    pixelTmp = np.asarray(im).copy()

    # make sure the image can hold the entire text
    if len(text) > width*height/2 - 7:
        print('The text is too large. Please split it into multiple pieces or choose a smaller text')

    # encrypt the text with a polyalphabetic cipher
    ciphertext = encryptPoly(text,keys)
    
    # inMiddle stores whether it is on the first or second pixel of the gorup of 2
    textIndex, inMiddle, doneWithText = 0, False, False

    # go through every pixel in the image
    for y in range(height):
        for x in range(width):

            # round 255 into 254 to avoid overflow issues
            for i in range(3):
                pixelTmp[y,x][i] = 254 if pixelTmp[y,x][i]==255 else pixelTmp[y,x][i]

            # the first 8 pixels store the key used on the text
            if (y==0 and x<8):
                for i in range(3):
                    pixelTmp[y,x][i] += charToInt(ternary[x][i]) - pixelTmp[y,x][i]%3
                continue
            
            # if the full message has been used, randomise the number added to the rest of the pixels
            if doneWithText and not inMiddle:
                for i in range(3):
                    pixelTmp[y,x][i] += random.randint(0,2) - pixelTmp[y,x][i]%3
                continue

            # if the text has not been fully used and this pixel is the first in a group of 2
            if not inMiddle:
                # if this is the last character of text, store a special value (2)
                if (textIndex == len(ciphertext)-1):
                    pixelTmp[y,x][0] += 2 - pixelTmp[y,x][0]%3 # -> showing its the end of the word
                    doneWithText = True
                    print(f'place it stopped: (y,x) = ({y},{x})')
                else:
                    # choose a random value for the pixel (0 or 1)
                    pixelTmp[y,x][0] += random.randint(0,1) - pixelTmp[y,x][0]%3

                for i in range(1,3):
                    pixelTmp[y,x][i] += charToInt(ciphertext[textIndex][i-1]) - pixelTmp[y,x][i]%3

            # if the text has not been fully used and this pixel is the second in a group of 2
            else:
                for i in range(3):
                    pixelTmp[y,x][i] += charToInt(ciphertext[textIndex][i+2]) - pixelTmp[y,x][i]%3

                textIndex+=1

            inMiddle = not inMiddle

    # save the new image
    output_image = Image.fromarray(np.uint8(pixelTmp))
    output_image.save(newName)

# decrypt the image into its original text
def decryptImage(image_name):

    im = Image.open(image_name)
    width, height = im.size
    pixelTmp = np.asarray(im).copy()

    # find the key from the first 8 pixels
    keys = []
    for x in range(8):
        tern = str(pixelTmp[0,x][0]%3)+str(pixelTmp[0,x][1]%3)+str(pixelTmp[0,x][2]%3)
        num = ternToDecimal(tern)
        keys.append(num+x*10)

    textIndex, inMiddle, doneWithText, ciphertext= 0, False, False, []

    # go through every pixel until the entire text has been found
    for y in range(height):
        if doneWithText:
            break
        for x in range(width):
            if doneWithText and not inMiddle:
                break

            # ignore the first 8 pixels
            if (y==0 and x<8):
                continue

            # if this pixel is the first in a group of 2
            if not inMiddle:
                # check if this is the last text pixel
                if (pixelTmp[y,x][0]%3==2):
                    doneWithText=True
                
                txt = str(pixelTmp[y,x][1]%3)+str(pixelTmp[y,x][2]%3)
                ciphertext.append(txt)
            else:

                txt = str(pixelTmp[y,x][0]%3)+str(pixelTmp[y,x][1]%3)+str(pixelTmp[y,x][2]%3)
                ciphertext[textIndex]+=txt
                textIndex+=1

            inMiddle = not inMiddle

    # return the text (saved as ternions) afer decrypting with the key
    return decryptPoly(ciphertext,keys)

if __name__ == '__main__':
    main()