from Crypto.PublicKey import RSA
import hashlib
oSHA = hashlib.sha256()
hPrivKey = RSA.generate(1024)
hPubKey = hPrivKey.publickey()
sTestMsg = b"This is a testmsg"
oSHA.update(sTestMsg)
sTestHash = oSHA.digest()
print("Hash: {}".format(sTestHash))
sSignature = hPrivKey.decrypt(sTestHash)
print("Signature: {}".format(sSignature))
sReencryptedHash = hPubKey.encrypt(1024, sTestHash)
print("ReencryptedHash: {}".format(sReencryptedHash))
