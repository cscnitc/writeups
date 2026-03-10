import json
from sympy import integer_nthroot
from Crypto.Util.number import long_to_bytes
entries = []
with open('intercepts.txt') as f:
    for line in f:
        line = line.strip()
        if line.startswith('{'):
            entries.append(json.loads(line))
def crt(items):
    N = 1
    for c, n in items:
        N *= n
    result = 0
    for c, n in items:
        m = N // n
        inv = pow(m, -1, n)
        result = (result + c * inv * m) % N
    return result, N
e5_entries = [(i, obj) for i, obj in enumerate(entries) if int(obj['e']) == 5]
items = [(int(obj['c']), int(obj['n'])) for _, obj in e5_entries[:5]]
C, N = crt(items)
root, exact = integer_nthroot(C, 5)
fake_key = long_to_bytes(root).decode()
runes = 'smuQJxedb40gWZiLl6MkjRy8SPpva1THO9cKIznDw2CB_UXEh7YAVroq53GfFtN'
memo = 'FcrrcF{x20nodPqn4xn3FHRX1o4bk5BVVNDSe}'
def vigenere_decrypt(ciphertext, key, alphabet):
    result = []
    key_idx = 0
    key_filtered = ''.join(c for c in key if c in alphabet)
    for c in ciphertext:
        if c in alphabet:
            c_pos = alphabet.index(c)
            k_pos = alphabet.index(key_filtered[key_idx % len(key_filtered)])
            p_pos = (c_pos - k_pos) % len(alphabet)
            result.append(alphabet[p_pos])
            key_idx += 1
        else:
            result.append(c)
    return ''.join(result)
flag = vigenere_decrypt(memo, fake_key, runes)
print(flag)
