import socket
from Crypto.Cipher import AES
from Crypto.Util.number import bytes_to_long,long_to_bytes

HOST='52.59.124.14'
PORT=5104
B=1<<128
E=65537

def recv_prompt(s):
    data=b''
    while b'input cipher (hex): ' not in data:
        chunk=s.recv(4096)
        if not chunk:
            break
        data+=chunk
    return data.decode(errors='replace')

s=socket.create_connection((HOST,PORT))
init=recv_prompt(s)
lines=[l for l in init.strip().split('\n') if l]
mod=int(lines[0])
cipher_hex=lines[1]
C=bytes.fromhex(cipher_hex)
L=int.from_bytes(C[:4],'big')
iv=C[4:20]
enc_msg=C[20:20+L]
enc_key=C[20+L:]
c0=bytes_to_long(enc_key)

def oracle(enc_key_int):
    enc_key_bytes=long_to_bytes(enc_key_int)
    payload=L.to_bytes(4,'big')+iv+enc_msg+enc_key_bytes
    s.sendall(payload.hex().encode()+b'\n')
    out=recv_prompt(s)
    return 'invalid padding' in out

low=0
high=(1<<64)-1
for _ in range(70):
    if low>=high:
        break
    mid=(low+high)//2
    if mid==0:
        mid=1
    s_val=B//mid
    if s_val==0:
        s_val=1
    c_prime=(c0*pow(s_val,E,mod))%mod
    ok=oracle(c_prime)
    if ok:
        U=(B-1)//s_val
        if U < high:
            high=U
    else:
        Lb=(B + s_val -1)//s_val
        if Lb > low:
            low=Lb

m=low
key=m.to_bytes(16,'big')
cipher=AES.new(key,AES.MODE_CBC, iv=iv)
pt=cipher.decrypt(enc_msg)
pad=pt[-1]
if 1<=pad<=16 and pt[-pad:]==bytes([pad])*pad:
    msg=pt[:-pad]
else:
    msg=pt
print(msg.decode(errors='replace'))
