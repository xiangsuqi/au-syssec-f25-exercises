import string
import secrets
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


class PPMImage:
    """Wrapper around a image in the PPM format.

    Format specification: http://netpbm.sourceforge.net/doc/ppm.html
    """

    def __init__(self, width, height, data, comments=None):
        """Construct an image from given dimension and raw data, and optionally comments."""
        self.width = width
        self.height = height
        if len(data) < width * height * 3:
            raise ValueError(
                "expected at least {width * height * 3} bytes, got {len(data)} bytes"
            )
        self.data = bytearray(data)
        if comments is None:
            self.comments = []
        else:
            self.comments = comments[:]

    def copy(self):
        """Make a copy of this object."""
        return PPMImage(self.width, self.height, self.data[:], self.comments[:])

    def __eq__(self, other):
        """Check if two objects are equal.

        NB: This is invoked whenever the `==` operator is used.
        """
        eq = True
        eq &= self.width == other.width
        eq &= self.height == other.height
        eq &= self.data == other.data
        eq &= self.comments == other.comments
        return eq

    def __repr__(self):
        """Make a human-readable description of the image."""
        return f"<PPMImage: width={self.width}, height={self.height}, comments={self.comments}, data_size={len(self.data)}>"

    def encrypt(self, key, mode):
        """Use AES to encrypt the image data in-place.

        The self.data is replaced with the ciphertext.  Additional data is
        stored in comment fields:
        - 'X-mode: <mode of operation used>
        - 'X-iv: <iv if CBC mode is used>
        - 'X-nonce: <nonce if CTR or GCM mode is used>
        - 'X-tag: <authentication tag if GCM mode is used>

        Parameters
        ----------
        key : bytes-like object of size 16
              key to be used for encryption
        mode : string, one of 'ecb', 'cbc', 'ctr', 'gcm'
              mode of operation
        """
        if mode.lower() == "ecb":
            # 1. create an AES object in ECB mode
            aes = AES.new(key, AES.MODE_ECB)
            # 2. pad the plaintext to a multiple of 16 bytes
            padded_plaintext = pad(self.data, 16)
            # 3. encrypt the padded plaintext
            ciphertext = aes.encrypt(padded_plaintext)
            # replace the image data with the ciphertext
            self.data = bytearray(ciphertext)
            # add a comment that we use ECB mode
            self.comments.append(b"X-mode: ecb")
        elif mode.lower() == "cbc":
            # --------- add your code here --------
            # raise NotImplementedError(f'mode of operation {mode} not implemented')
            iv = get_random_bytes(16)
            aes = AES.new(key, AES.MODE_CBC, iv)
            padded_plaintext = pad(self.data, 16)
            ciphertext = aes.encrypt(padded_plaintext)
            # ----- end add your code here --------
            # replace the image data with the ciphertext
            self.data = bytearray(ciphertext)
            # add a comment that we use CBC mode
            self.comments.append(b"X-mode: cbc")
            # store the IV in a comment
            self.comments.append(f"X-iv: {iv.hex()}".encode())
        elif mode.lower() == "ctr":
            # --------- add your code here --------
            # raise NotImplementedError(f'mode of operation {mode} not implemented')
            nonce = get_random_bytes(8)
            aes = AES.new(key, AES.MODE_CTR, nonce=nonce)
            ciphertext = aes.encrypt(self.data)
            # ----- end add your code here --------
            # replace the image data with the ciphertext
            self.data = bytearray(ciphertext)
            # add a comment that we use CTR mode
            self.comments.append(b"X-mode: ctr")
            # store the nonce in a comment
            self.comments.append(f"X-nonce: {nonce.hex()}".encode())
        elif mode.lower() == "gcm":
            # --------- add your code here --------
            # raise NotImplementedError(f"mode of operation {mode} not implemented")
            nonce = secrets.token_bytes(8)
            aes = AES.new(key, AES.MODE_GCM, nonce=nonce)
            ciphertext = aes.encrypt(self.data)
            tag = aes.digest()
            # ----- end add your code here --------
            # replace the image data with the ciphertext
            self.data = bytearray(ciphertext)
            # add a comment that we use GCM mode
            self.comments.append(b"X-mode: gcm")
            # store the authentication tag in a comment
            self.comments.append(f"X-tag: {tag.hex()}".encode())
            # store the nonce in a comment
            self.comments.append(f"X-nonce: {nonce.hex()}".encode())
        else:
            raise NotImplementedError(f"unknown mode of operation {mode}")

    def decrypt(self, key):
        """Use AES to decrypt the encrypted image data in-place.

        Required additional data is read from the comments:
        - 'X-mode: <mode of operation used>
        - 'X-iv: <iv if CBC mode is used>
        - 'X-nonce: <nonce if CTR or GCM mode is used>
        - 'X-tag: <authentication tag if GCM mode is used>

        Then self.data is replaced with the plaintext.

        Parameters
        ----------
        key : bytes-like object of size 16
              key to be used for encryption
        """

        # Some helper functions you can ignore

        def find_property_in_comments(name):
            """Find the comment starting with 'X-name:'."""
            comment = next(
                (c for c in self.comments if c.startswith(f"X-{name}:".encode())), None
            )
            if comment is None:
                raise ValueError(f"not comment starting with 'X-{name}:' found")
            return comment.decode().removeprefix(f"X-{name}:").strip()

        def cleanup_comments():
            """Remove all the special comments we used to store additional data in."""
            prefixes = [b"X-mode", b"X-iv", b"X-nonce", b"X-tag"]
            self.comments = list(
                filter(
                    lambda c: not any(c.startswith(prefix) for prefix in prefixes),
                    self.comments,
                )
            )

        # Read the mode of operation from the comments
        mode = find_property_in_comments("mode")

        if mode.lower() == "ecb":
            # 1. create an AES object in ECB mode
            aes = AES.new(key, AES.MODE_ECB)
            # 2. decrypt the ciphertext
            padded_plaintext = aes.decrypt(self.data)
            # 3. remove the padding to obtain the original plaintext
            plaintext = unpad(padded_plaintext, 16)
            # replace the image data with the plaintext
            self.data = bytearray(plaintext)
            # remove the comments where we stored the additional data
            cleanup_comments()
        elif mode.lower() == "cbc":
            # Read the used IV from the comments
            iv = bytes.fromhex(find_property_in_comments("iv"))
            # --------- add your code here --------
            # raise NotImplementedError(f'mode of operation {mode} not implemented')
            aes = AES.new(key, AES.MODE_CBC, iv)
            padded_plaintext = aes.decrypt(self.data)
            plaintext = unpad(padded_plaintext, 16)
            # ----- end add your code here --------
            # replace the image data with the plaintext
            self.data = bytearray(plaintext)
            # remove the comments where we stored the additional data
            cleanup_comments()
        elif mode.lower() == "ctr":
            # Read the used nonce from the comments
            nonce = bytes.fromhex(find_property_in_comments("nonce"))
            # --------- add your code here --------
            # raise NotImplementedError(f'mode of operation {mode} not implemented')
            aes = AES.new(key, AES.MODE_CTR, nonce=nonce)
            plaintext = aes.decrypt(self.data)
            # ----- end add your code here --------
            # replace the image data with the plaintext
            self.data = bytearray(plaintext)
            # remove the comments where we stored the additional data
            cleanup_comments()
        elif mode.lower() == "gcm":
            # Read the used nonce from the comments
            nonce = bytes.fromhex(find_property_in_comments("nonce"))
            # Read the authentication tag from the comments
            tag = bytes.fromhex(find_property_in_comments("tag"))
            # --------- add your code here --------
            # raise NotImplementedError(f"mode of operation {mode} not implemented")
            aes = AES.new(key, AES.MODE_GCM, nonce=nonce)
            plaintext = aes.decrypt_and_verify(self.data, tag)
            # ----- end add your code here --------
            # replace the image data with the plaintext
            self.data = bytearray(plaintext)
            # remove the comments where we stored the additional data
            cleanup_comments()
        else:
            raise NotImplementedError(f"unknown mode of operation {mode}")

    @property
    def size(self):
        """Size in pixels."""
        return self.width * self.height

    @staticmethod
    def load_from_file(file):
        """Load a PPM file from a file object.

        The implementation can be ignored for the exercise.

        Example
        -------
        with open('image.ppm', 'rb') as f:          # open the image in binary mode (with option 'b')
            image = PPMImage.load_from_file(f)
        """
        whitespace = string.whitespace.encode()
        digits = string.digits.encode()

        comments = []

        def consume_comment(f):
            if (c := f.read(1)) != b"#":
                raise ValueError(f"expected b'#', got {c} instead")
            comment = b""
            while (c := f.read(1)) != b"\n":
                if c == b"":
                    raise ValueError("unexpected end of file")
                comment += c
            comments.append(comment)

        def consume_whitespace(f):
            while (c := f.peek(1)[:1]) != b"":
                if c == b"#":
                    consume_comment(f)
                elif c in whitespace:
                    f.read(1)
                else:
                    return
            raise ValueError("unexpected end of file")

        def read_until_whitespace(f):
            token = b""
            while (c := f.peek(1)[:1]) != b"":
                if c == b"#":
                    consume_comment(f)
                elif c not in whitespace:
                    token += f.read(1)
                else:
                    return token
            raise ValueError("unexpected end of file")

        def is_number(token):
            return all(x in digits for x in token)

        def read_number(f):
            token = read_until_whitespace(f)
            if not is_number(token):
                raise ValueError(f"expected number, got {token} instead")
            return int(token)

        # read magic number
        magic_number = file.read(2)
        if len(magic_number) < 2:
            raise ValueError("unexpected end of file")
        if magic_number != b"P6":
            raise ValueError("unknown file type")

        # read width of image
        consume_whitespace(file)
        width = read_number(file)

        # read height of image
        consume_whitespace(file)
        height = read_number(file)

        # read maximum value of pixels
        consume_whitespace(file)
        max_value = read_number(file)
        if max_value >= 256:
            raise ValueError("only one-byte values are supported")

        while (c := file.peek(1)[:1]) == b"#":
            consume_comment()

        c = file.read(1)
        if not c in whitespace:
            raise ValueError(f"expected single whitespace, got {c} instead")

        size = width * height * 3
        data = file.read()  # just read all available data
        if (l := len(data)) < size:
            raise ValueError(f"expected at least {size} bytes, got only {l} bytes")

        return PPMImage(width, height, data, comments=comments)

    def write_to_file(self, file):
        """Write this object to a PPM file.

        The implementation can be ignored for the exercise.

        Example
        -------
        with open('image.ppm', 'wb') as f:          # open the image writable in binary mode (with options 'w' and 'b')
            image.write_to_file(f)
        """
        file.write(b"P6\n")
        for comment in self.comments:
            file.write(b"#" + comment + b"\n")
        header = f"{self.width} {self.height}\n255\n"
        file.write(header.encode())
        file.write(self.data)


def test():
    """Simple test of correctness."""
    with open("dk.ppm", "rb") as f:
        original_image = PPMImage.load_from_file(f)

    key = secrets.token_bytes(16)
    for mode in ["ecb", "cbc", "ctr", "gcm"]:
        image = original_image.copy()
        image.encrypt(key, mode)
        assert (
            original_image != image
        ), f"encrypting with {mode} mode should change the image"
        image.decrypt(key)
        assert (
            original_image == image
        ), f"encrypting and decrypting with {mode} mode should yield the original image"


def exercise_3():
    with open("dk.ppm", "rb") as f:
        image_dk = PPMImage.load_from_file(f)
    with open("se.ppm", "rb") as f:
        image_se = PPMImage.load_from_file(f)

    assert len(image_dk.data) == len(image_se.data)
    encrypted_image = image_dk.copy()
    key = secrets.token_bytes(16)
    encrypted_image.encrypt(key, "ctr")

    def xor(xs, ys):
        """Compute the bit-wise xor of two byte-like objects."""
        return bytes(x ^ y for x, y in zip(xs, ys))

    diff = xor(image_dk.data, image_se.data)

    encrypted_image.data = bytearray(xor(encrypted_image.data, diff))

    encrypted_image.decrypt(key)
    with open("ex3_result.ppm", "wb") as f:
        encrypted_image.write_to_file(f)
    
def exercise_5():
    with open("security.ppm", "rb") as f:
        image = PPMImage.load_from_file(f)

    key = secrets.token_bytes(16)
    image.encrypt(key, 'gcm')

    image.height = 245

    image.decrypt(key)
    with open("ex5_result.ppm", "wb") as f:
        image.write_to_file(f)

if __name__ == "__main__":
    # The following is executed if you run `python3 ppmcrypt.py`.
    test()
    # exercise_3()
    # exercise_5()
