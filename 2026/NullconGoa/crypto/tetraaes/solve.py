import re
import socket
from itertools import product
from chall import encrypt

HOST='52.59.124.14'
PORT=5103
PROMPT=b"message to encrypt:"
CHUNK=8

def recv_until_prompts(sock, expected, timeout=60):
    sock.settimeout(timeout)
    data=b''
    prompts=0
    while prompts<expected:
        chunk=sock.recv(4096)
        if not chunk:
            break
        data+=chunk
        prompts+=chunk.count(PROMPT)
    return data

def parse_ciphers(blob):
    return [bytes.fromhex(x.decode()) for x in re.findall(rb"cipher\.hex\(\) = '([0-9a-f]+)'", blob)]

with socket.create_connection((HOST, PORT), timeout=60) as s:
    banner=recv_until_prompts(s,1,timeout=60)
    ciphers=parse_ciphers(banner)
    if not ciphers:
        raise SystemExit('no banner cipher')
    c_key=ciphers[0]

    key_candidates=[]
    for pos in range(16):
        found=None
        start=0
        while found is None and start<128:
            msgs=[]
            for x in range(start, min(128, start+CHUNK)):
                a=x
                b=x^0x8c
                m=bytearray(16); m[pos]=a
                m2=bytearray(16); m2[pos]=b
                msgs.append(bytes(m))
                msgs.append(bytes(m2))
            s.sendall(b"\n".join(m.hex().encode() for m in msgs)+b"\n")
            resp=recv_until_prompts(s,len(msgs),timeout=60)
            ciph=parse_ciphers(resp)
            if len(ciph)!=len(msgs):
                raise SystemExit('cipher mismatch')
            for i in range(0,len(msgs),2):
                if ciph[i]==ciph[i+1]:
                    found=msgs[i][pos]
                    break
            start+=CHUNK
        if found is None:
            raise SystemExit('no collision')
        if pos==0:
            cand1=found^42
            cand2=cand1^0x8c
        else:
            cand1=found
            cand2=found^0x8c
        key_candidates.append((cand1,cand2))

    key=None
    for bits in product([0,1], repeat=16):
        k=bytes(key_candidates[i][bits[i]] for i in range(16))
        if encrypt(k,k)==c_key:
            key=k
            break
    if key is None:
        raise SystemExit('no key after brute force')

    s.sendall(b"end\n")
    buf=b''
    while b'key in hex' not in buf:
        chunk=s.recv(4096)
        if not chunk:
            break
        buf+=chunk
    s.sendall(key.hex().encode()+b"\n")
    final=s.recv(4096)
    print(final.decode(errors='ignore'))
