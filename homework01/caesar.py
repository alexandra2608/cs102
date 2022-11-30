def encrypt_caesar(plaintext: str, shift: int = 3) -> str:
    """
    Encrypts plaintext using a Caesar cipher.
    >>> encrypt_caesar("PYTHON")
    'SBWKRQ'
    >>> encrypt_caesar("python")
    'sbwkrq'
    >>> encrypt_caesar("Python3.6")
    'Sbwkrq3.6'
    >>> encrypt_caesar("")
    ''
    """
    ciphertext = ""

    for i in range(len(plaintext)):
        char = plaintext[i]
        if char.isupper():
            ciphertext += chr((ord(char) + shift - ord("A")) % 26 + ord("A"))
        elif char.islower():
            ciphertext += chr((ord(char) + shift - ord("a")) % 26 + ord("a"))
        else:
            ciphertext += plaintext[i]
    return ciphertext


def decrypt_caesar(ciphertext: str, shift: int = 3) -> str:
    """
    Decrypts a ciphertext using a Caesar cipher.
    >>> decrypt_caesar("SBWKRQ")
    'PYTHON'
    >>> decrypt_caesar("sbwkrq")
    'python'
    >>> decrypt_caesar("Sbwkrq3.6")
    'Python3.6'
    >>> decrypt_caesar("")
    ''
    """
    plaintext = ""
    for i in range(len(ciphertext)):
        char = ciphertext[i]
        if char.isupper():
            plaintext += chr((ord(char) - shift - ord("A")) % 26 + ord("A"))
        elif char.islower():
            plaintext += chr((ord(char) - shift - ord("a")) % 26 + ord("a"))
        else:
            plaintext += ciphertext[i]
    return plaintext
