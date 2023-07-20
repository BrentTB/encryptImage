A program to encrypt text into images

An image can hold the amount of text characters equal to half its number of pixels

Each RGB value is rounded down to the nearest multiple of 3, and then its value is increased.
This allows a pair of 2 pixels to hold 3^6 possible combinations [6 ternary units]. The first 5 units of the pixels to hold a value, while the last records if the current pixels is the end of the text or not. Once the text is done, the rest of the pixels have random values added to them.

Moreover, the first 8 pixels are used to record a random key which is used in the decryption process, to increase security

The encryption is not very noticable in normal images, but it can be seen in the gradient photo, and thus the photo must be chosen carefully in order for no abnormalities to be noticed. 