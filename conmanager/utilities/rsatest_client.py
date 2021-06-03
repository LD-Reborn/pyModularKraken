from Crypto.PublicKey import RSA
import socket

def importKey(sKey):
	sKey = bytes(sKey[2:-2], "utf-8").replace(b'\\n', b'\n')
	return RSA.importKey(sKey)


hFile = open("testkeys.txt")
hPub = importKey(hFile.readline())

sData = b'Lol WTF'
sData = hPub.encrypt(sData, 'K')[0]

print(sData)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#.setblocking(0)

try:
    s.connect(("", 20012))
except socket.error as msg:
    print('connect failed. Error Code : {}'.format(msg))
    exit()



s.send(sData)
