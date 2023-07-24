A program to encrypt text into images

An image can hold the number of text characters equal to half its number of pixels

Each RGB value is rounded down to the nearest multiple of 3, and then its value increases.
This allows a pair of 2 pixels to hold 3^6 possible combinations [6 ternary units]. The first 5 units of the pixels have a value, while the last records if the current pixel is the end of the text or not. Once the text is done, the rest of the pixels have random values added to them.

Moreover, the first 8 pixels are used to record a random key which is used in the decryption process, to increase security

The encryption is not very noticeable in standard images, but it can be seen in the gradient photo, and thus the photo must be chosen carefully in order for no abnormalities to be noticed. 

TODO: Implement Binary encoding, such that the change in each pixel's value will be less, at the cost of the picture being able to hold fewer words. The code should automatically use binary unless the text size is large, in which case ternary should be utilized
