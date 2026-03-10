---
title: "NullCon Goa CTF 2026 - TLS"
pubDatetime: 2026-03-09T12:00:00+00:00
author: "astroanax"
---

The code in chall.py is small, the server gives out an rsa modulus and a ciphertext that encodes an AES CBC message followed by an RSA encrypted AES key. The key is constructed as 8 zero bytes followed by eight random bytes. That detail means the real secret portion of the key is only 64 bits.

My first thought was a straight CBC padding oracle. If the remote service will accept modified IVs and reveal padding validity I can recover the plaintext byte by byte. Locally the CBC padding oracle worked fine.  I then tried the same approach against the remote service by flipping the IV bytes and the preceding ciphertext blocks and looking at the responses.

Sometimes the server returned invalid padding, other times errors idk why. In chall.py there is an early check after RSA decryption that errors if the recovered integer representing the AES key is larger than 1 left shifted 128. That check kills many modified ciphertexts before AES is even attempted. In other words the RSA key check prevents a reliable padding oracle over the network.

The RSA decryption logic performs CRT exponent recombination and then checks whether the resulting integer fits within 128 bits. If the RSA decrypted integer is small enough the code proceeds to AES decryption and I might get a padding error. If it is larger the server fails . So the server leaks a single bit about whether the RSA decrypted value is at most 2 to the 128 or not.

Because RSA is multiplicative, if c is an RSA ciphertext for m and I get c prime equal to c* s to the e mod n and c prime decrypts to m * s mod n. Since the actual AES key integer m is small compared with n, for small enough s the value m * s is just the normal integer product. By choosing s so that m * s crosses the 2 to the 128 boundary versus staying below it I can test inequalities and gradually narrow down m with a binary search on 64 bit unknown by using multiplicative blinding with different s values and checking the server predicate for each trial.

The solver reads the modulus and ciphertext, parses the length IV and AES ciphertext, and extracts the RSA encrypted key. It then carries out a binary search where each step picks a candidate multiplier derived from the current interval and sends the altered RSA ciphertext. The server answer tells whether the product is below or above the 2 to the 128 threshold and I use that information to shrink the interval.

The exact outputs are below, the server printed the modulus and the ciphertext in the initial banner. 

2583445339238263550349768203407696376053079972542385056538679156304692123031166277683374662188329475477729821797523953913899038010744457519768280829891585965983988279013383046962307878351115277608085121816315962249534057347103089147386003267203014718077891726591288954622007382700914589353184482171655652224359993032133876246889627870628108543647779735620037767644441696731326022046691637098052708485569
00000020f45eff9ea04a554899c75dae7ab5a608bdb7661c05b40b854beeaf6c153042c599e73a014b461925c08aa43296217c95011f249582c3ea4b8e7e3e638f8838c578c37054eda45ab5a5e6826807da28c0fbb1c89caf0806689b8b379869df7ac9e6b43de52dd174ac6c6c0c3893920556024fe51d7dc63e40ff5286c729a48880f3f984ff206cc03e1b964b543e4042f5f8194be9126945cedbe013e33e78f4f86fc67f635d31c792f315d724da8543d45b5225c8846386fe410013013dbbd6b151538df080681ca6bc975d1d3c47946f04d562cc11f707a2

The server sometimes responded with invalid padding and sometimes with a weird error that indicates the RSA key check failed. After switching to the multiplicative search approach I ran the binary search and the script then worked -

iter 0 low 9223372036854775808 high 18446744073709551615
iter 10 low 11078855083331420160 high 11087862282586161151
iter 20 low 11084827630493499392 high 11084836426586521599
iter 30 low 11084828077170098176 high 11084828085760032767
iter 40 low 11084828078478721024 high 11084828078487109631
iter 50 low 11084828078485078016 high 11084828078485086207
iter 60 low 11084828078485081344 high 11084828078485081351
queries 64
interval 11084828078485081349 11084828078485081349
key 000000000000000099d538684e610d05
pt_raw b'ENO{Y4y_a_f4ctor1ng_0rac13}\x05\x05\x05\x05\x05'
msg b'ENO{Y4y_a_f4ctor1ng_0rac13}'

The recovered key shown here has the upper 64 bits as 0s. The plaintext included PKCS#7 padding in the log and the final unpadded message is the flag -

ENO{Y4y_a_f4ctor1ng_0rac13}

code [here](./solve.py)

satisfyibg
