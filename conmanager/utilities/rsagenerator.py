from Crypto.PublicKey import RSA
import socket
hFile = open("testkeys.txt", "w")
#hFile.write("[testkeys]\n")
i = 0
while i < 100:
    i += 1
    RSAKey = RSA.generate(1024)
    key_public = RSAKey.publickey()
    key_public_ = key_public.exportKey()
    key_private = RSAKey
    key_private_ = key_private.exportKey()
    #print(key_public_)
    #print(key_private_)
    hFile.write("{}\n{}\n\n".format(str(key_public_)[2:-1], str(key_private_)[2:-1]))    
    print(i)
    
hFile.close()
