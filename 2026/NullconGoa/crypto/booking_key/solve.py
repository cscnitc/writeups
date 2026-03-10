import socket
import re
import ast
import string

def decrypt(cipher, book):
    charset = set(c for c in string.ascii_letters if c in book)
    out = []
    n = len(book)
    for s in range(n):
        cur = s
        ok = True
        msg = []
        for c in cipher:
            cur = (cur + c) % n
            ch = book[cur]
            if ch not in charset:
                ok = False
                break
            msg.append(ch)
        if ok:
            out.append("".join(msg))
    return out

book = open('book.txt').read()
host = '52.59.124.14'
port = 5102
s = socket.socket()
s.connect((host, port))
buf = b''
def recv_until(tokens):
    global buf
    while True:
        data = s.recv(4096)
        if not data:
            break
        buf += data
        for t in tokens:
            if t in buf:
                return buf
    return buf

recv_until([b'password:'])
while True:
    m = re.search(rb"\[([0-9, ]+)\]", buf)
    if not m:
        break
    arr = m.group(0).decode()
    cipher = ast.literal_eval(arr)
    cand = decrypt(cipher, book)
    ok = False
    for p in cand:
        s.sendall((p + "\n").encode())
        buf = recv_until([b'password:', b'ENO{', b'wrong password', b'correct'])
        if b'ENO{' in buf or b'correct' in buf:
            print(buf.decode())
            ok = True
            break
    if ok:
        break
s.close()
