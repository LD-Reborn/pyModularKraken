from Crypto.PublicKey import RSA
import socket
import time

def importKey(sKey):
	sKey = bytes(sKey[2:-2], "utf-8").replace(b'\\n', b'\n')
	return RSA.importKey(sKey)

hFile = open("testkeys.txt")
hPub = importKey(hFile.readline())
hPriv = importKey(hFile.readline())

clients = []

HOST = ''
PORT = 20012

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setblocking(0)

try:
	s.bind((HOST, PORT))
except socket.error as msg:
	print('Bind failed. Error Code : {}'.format(msg))
	exit()

s.listen(10)

while True:
        try:
                conn, addr = s.accept()
                conn.setblocking(0)
                print("newcon:")
                print(conn)
                clients.append((conn, addr))
        except:
                pass
        if len(clients):
                for client in clients:
                        sRecv = b''
                        bHas = True
                        while bHas:
                                try:
                                        sTemp = client[0].recv(128)
                                        sRecv = sRecv + hPriv.decrypt(sTemp)
                                except:
                                        break
                        if len(sRecv):
                                print(client[0])
                                print(client[1])
                                print(sRecv)
                                print("")
