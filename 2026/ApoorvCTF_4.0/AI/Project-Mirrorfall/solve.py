#!/usr/bin/env python3

import subprocess
import os

def get_commit_sha():
    repo_url = "https://github.com/iamcryptoki/snowden-archive"
    repo_dir = "snowden-archive"
    target_file = "documents/2013/20130905-theguardian__bullrun.pdf"

    if not os.path.exists(repo_dir):
        subprocess.run(["git", "clone", repo_url], check=True)

    result = subprocess.run(
        ["git", "log", "--oneline", "--", target_file],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    first_line = result.stdout.strip().splitlines()[0]
    full_sha = first_line.split()[0]
    short_sha = full_sha[:7]
    print(f"[*] Full commit SHA : {full_sha}")
    print(f"[*] Variable X      : {short_sha}")
    return short_sha


def get_eci_codeword():
    # From row A.2 Remarks column of the BULLRUN classification guide PDF:
    # APERIODIC, AMBULANT, AUNTIE, PAINTEDEAGLE, PAWLEYS, PITCHFORD,
    # PENDLETON, PICARESQUE, PIEDMONT
    # Second ECI (8-letter codeword) → AMBULANT → normalise to lowercase
    codeword = "ambulant"
    print(f"[*] ECI codeword    : {codeword}")
    return codeword


def get_embedding_value(codeword: str) -> float:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embedding = model.encode(codeword)
    value = round(float(embedding[0]), 4)
    print(f"[*] embedding[0]    : {value}")
    return value


if __name__ == "__main__":
    x = get_commit_sha()
    codeword = get_eci_codeword()
    y = get_embedding_value(codeword)
    flag = f"apoorvctf{{{x}_{y}}}"
    print(f"\n[+] FLAG: {flag}")