from Crypto.PublicKey import RSA
bitlength = 4096
#hFile = open("testkeys_{}.txt".format(bitlength), "w")
#hFile.write("[testkeys]\n")
i = 0
while i < 10:
    i += 1
    hPriv = open("{}_{}.priv".format(i, bitlength), "w")
    hPub = open("{}_{}.pub".format(i, bitlength), "w")
    RSAKey = RSA.generate(bitlength)
    key_public = RSAKey.publickey()
    key_public_ = key_public.exportKey()
    key_private = RSAKey
    key_private_ = key_private.exportKey()
    #print(key_public_)
    #print(key_private_)
    hPriv.write(str(key_private_)[2:-1])
    hPriv.close()
    hPub.write(str(key_private_)[2:-1])
    hPub.close()
    #hFile.write("{}\n{}\n\n".format(str(key_public_)[2:-1], str(key_private_)[2:-1]))    
    print(i)
    
#hFile.close()
