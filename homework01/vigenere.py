def encrypt_vigenere(plaintext: str, keyword: str) -> str:
    """
    Encrypts plaintext using a Vigenere cipher.
    >>> encrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> encrypt_vigenere("python", "a")
    'python'
    >>> encrypt_vigenere("ATTACKATDAWN", "LEMON")
    'LXFOPVEFRNHR'
    """
    ciphertext = ""
    for pos, letter in enumerate(plaintext):
        if letter.isupper():
            ciphertext += chr(ord("A") + (ord(letter) + (ord(keyword[pos % len(keyword)]) - 2 * ord("A"))) % 26)
        elif letter.islower():
            ciphertext += chr(ord("a") + (ord(letter) + (ord(keyword[pos % len(keyword)]) - 2 * ord("a"))) % 26)
        else:
            ciphertext += letter
    return ciphertext


def decrypt_vigenere(ciphertext: str, keyword: str) -> str:
    """
    Decrypts a ciphertext using a Vigenere cipher.
    >>> decrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> decrypt_vigenere("python", "a")
    'python'
    >>> decrypt_vigenere("LXFOPVEFRNHR", "LEMON")
    'ATTACKATDAWN'
    """
    plaintext = ""
    for pos, letter in enumerate(ciphertext):
        if letter.isupper():
            plaintext += chr(ord("A") + (ord(letter) - ord(keyword[pos % len(keyword)])) % 26)
        elif letter.islower():
            plaintext += chr(ord("a") + (ord(letter) - ord(keyword[pos % len(keyword)])) % 26)
        else:
            plaintext += letter
    return plaintext
