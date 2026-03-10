import socket
import ast
import os
import base64
alphabet = b'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/='
idx = {c:i for i,c in enumerate(alphabet)}
def to_blocks(msg_bytes):
    # base64-encode and pad to 16-byte blocks (just like chall.py)
    enc = base64.b64encode(msg_bytes)
    padlen = 16 - (len(enc) % 16)
    enc += b'=' * padlen
    blocks = []
    for i in range(0, len(enc), 16):
        blk = enc[i:i+16]
        blocks.append([idx[c] for c in blk])
    return blocks
def recv_line(sock):
    buf = b''
    while not buf.endswith(b'\n'):
        data = sock.recv(1)
        if not data:
            break
        buf += data
    return buf.decode().rstrip('\n')
def parse_list(line):
    # server output might include a prompt. If so, strip it.
    if 'enter your message' in line:
        line = line.split(':',1)[1].strip()
    return ast.literal_eval(line)
def solve_mod_linear(X, y, p):
    # X: list of rows (each row is list of n coefficients), y: list of length m outputs.
    # Solves for unknown vector of length n in Z_p by Gaussian elimination on the augmented matrix.
    m = len(X); n = len(X[0])
    A = [row[:] + [yy] for row, yy in zip([r[:] for r in X], y)]
    row = 0
    for col in range(n):
        pivot = None
        for r in range(row, m):
            if A[r][col] % p:
                pivot = r; break
        if pivot is None:
            continue
        A[row], A[pivot] = A[pivot], A[row]
        inv = pow(A[row][col], -1, p)
        A[row] = [(v * inv) % p for v in A[row]]
        for r in range(m):
            if r == row: continue
            factor = A[r][col] % p
            if factor == 0: continue
            A[r] = [(a - factor*b) % p for a,b in zip(A[r], A[row])]
        row += 1
        if row == m: break
    sol = [0]*n
    for r in range(m-1, -1, -1):
        lead = None
        for c in range(n):
            if A[r][c] % p == 1:
                lead = c; break
            elif A[r][c] % p != 0:
                break
        if lead is None: continue
        sol[lead] = A[r][-1] % p
    return sol
def invert_matrix_mod(mat, p):
    # mat is n x n. returns inverse modulo p using augmented matrix elimination.
    n = len(mat)
    aug = [ (mat[i][:] + [int(i==j) for j in range(n)]) for i in range(n) ]
    row = 0
    for col in range(n):
        pivot = None
        for r in range(row, n):
            if aug[r][col] % p:
                pivot = r; break
        if pivot is None:
            continue
        aug[row], aug[pivot] = aug[pivot], aug[row]
        inv = pow(aug[row][col], -1, p)
        aug[row] = [(v * inv) % p for v in aug[row]]
        for r in range(n):
            if r == row: continue
            factor = aug[r][col] % p
            if factor == 0: continue
            aug[r] = [(a - factor*b) % p for a,b in zip(aug[r], aug[row])]
        row += 1
    inv_mat = [row[n:] for row in aug]
    return inv_mat
def crt_pair(a5, a13):
    # combine residues modulo 5 and 13 into residue modulo 65
    # x = a5 * 13 * inv(13 mod 5) + a13 * 5 * inv(5 mod 13) (mod 65)
    # inv(13 mod 5) = inv(3 mod 5) = 2
    # inv(5 mod 13) = 8
    return (a5 * 13 * 2 + a13 * 5 * 8) % 65
HOST='52.59.124.14'
PORT=5101
sock = socket.create_connection((HOST, PORT))
first = recv_line(sock)
flag_cipher = parse_list(first)
samples_X = []
samples_y = [[] for _ in range(16)]
def send_msg(mbytes):
    hx = mbytes.hex()
    sock.sendall((hx+'\n').encode())
    line = recv_line(sock)
    if not line:
        raise SystemExit('no resp')
    return parse_list(line)
# collect chosen-encryption samples (random messages)
for _ in range(60):
    m = os.urandom(12)   # 12 bytes => base64 length 16 => one block; using random data is fine
    blocks = to_blocks(m)
    cipher = send_msg(m)
    for blk, start in zip(blocks, range(0,len(cipher),16)):
        rowvec = blk + [1]  # 16 coefficients + 1 for the constant 'b' term
        samples_X.append(rowvec)
        for j in range(16):
            samples_y[j].append(cipher[start+j])
sock.sendall(b'exit\n')
# Reconstruct A (rows) and b by solving for each output coordinate.
A = [[0]*16 for _ in range(16)]
b = [0]*16
X5 = [[v%5 for v in row] for row in samples_X]
X13 = [[v%13 for v in row] for row in samples_X]
for j in range(16):
    ycol = samples_y[j]
    sol5 = solve_mod_linear(X5, [yy%5 for yy in ycol], 5)
    sol13 = solve_mod_linear(X13, [yy%13 for yy in ycol], 13)
    sol = [crt_pair(a5,a13) for a5,a13 in zip(sol5, sol13)]
    for c in range(16):
        A[j][c] = sol[c] % 65
    b[j] = sol[16] % 65
# Invert A modulo 5 and modulo 13, then combine inverses by applying each to the
# corresponding residue and CRTing the results back (we invert separately then use them to
# solve for x, which is easier than trying to combine one big matrix inverse directly).
A5_inv = invert_matrix_mod([[a%5 for a in row] for row in A], 5)
A13_inv = invert_matrix_mod([[a%13 for a in row] for row in A], 13)
def solve_block(y_vec):
    y = [(v - b_i) % 65 for v,b_i in zip(y_vec,b)]
    y5 = [v%5 for v in y]
    y13 = [v%13 for v in y]
    x5 = [sum(A5_inv[r][c]*y5[c] for c in range(16)) % 5 for r in range(16)]
    x13 = [sum(A13_inv[r][c]*y13[c] for c in range(16)) % 13 for r in range(16)]
    return [crt_pair(a5,a13) for a5,a13 in zip(x5,x13)]
flag_blocks = [flag_cipher[i:i+16] for i in range(0,len(flag_cipher),16)]
plain_blocks = []
for blk in flag_blocks:
    plain_blocks.extend(solve_block(blk))
plain_bytes = bytes(alphabet[i] for i in plain_blocks)
# remove padding introduced by encryption (trailing '=')
plain_bytes = plain_bytes.rstrip(b'=')
# ensure valid base64 length
if len(plain_bytes)%4:
    plain_bytes += b'=' * (4 - len(plain_bytes)%4)
flag = base64.b64decode(plain_bytes)
print(flag)
