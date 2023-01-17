#Maximilian Dobrei, Carleton University 101103400
#Last modified: August 2nd 2022
#a script that defines functions useful for encrypting & decrypting messages, as well as creating and verifying digital signatures
#UTILIZES RSA AS IMPLEMENTED IN THE PYCRYPTODOME LIBRARY 


from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

def generate_key():
    priv_key = RSA.generate(2048)

    return priv_key
    
#EXPECTS A VARIABLE OF TYPE Crypto.PublicKey.RSA.RsaKey -- ie KEY HAS ALREADY BEEN IMPORTED AND TURNED INTO AN RSA KEY OBJECT
#DOES NOT WORK IF GIVEN A KEY IN PEM FORMAT
#ENCRYPTS USING THE PUBLIC KEY OF RECEIVER
def encrypt_msg(public_key, message):
    cipher = PKCS1_OAEP.new(public_key)
    return cipher.encrypt(message)

#EXPECTS A VARIABLE OF TYPE Crypto.PublicKey.RSA.RsaKey -- ie KEY HAS ALREADY BEEN IMPORTED AND TURNED INTO AN RSA KEY OBJECT
#DOES NOT WORK IF GIVEN A KEY IN PEM FORMAT
#DECRYPTS USING THE PRIVATE KEY OF RECEIVER
def decrypt_msg(private_key, ciphertext):
    cipher = PKCS1_OAEP.new(private_key)
    try:
        message = cipher.decrypt(ciphertext)
        return message
    except:
        return b"FAILED"


#EXPECTS A VARIABLE OF TYPE Crypto.PublicKey.RSA.RsaKey -- ie KEY HAS ALREADY BEEN IMPORTED AND TURNED INTO AN RSA KEY OBJECT
#DOES NOT WORK IF GIVEN A KEY IN PEM FORMAT
#CREATES A DIGITAL SIGNATURE USING THE SENDERS PRIVATE KEY
def sign_msg(private_key, message):
    hash = SHA256.new(message)
    return pkcs1_15.new(private_key).sign(hash)

#EXPECTS A VARIABLE OF TYPE Crypto.PublicKey.RSA.RsaKey -- ie KEY HAS ALREADY BEEN IMPORTED AND TURNED INTO AN RSA KEY OBJECT
#DOES NOT WORK IF GIVEN A KEY IN PEM FORMAT
#VERIFIES A DIGITAL SIGNATURE USING THE SENDERS PUBLIC KEY
def verify_msg(public_key, ciphertext, signature):
    hash = SHA256.new(ciphertext)
    try:
        pkcs1_15.new(public_key).verify(hash, signature)
        return True
    except(ValueError, TypeError):
        return False
