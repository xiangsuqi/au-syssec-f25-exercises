from ppmcrypt import PPMImage
from Crypto.Random import get_random_bytes


image = PPMImage.load_from_file(open('tux.ppm', 'rb'))

key = get_random_bytes(16)

# # ECB
# image.encrypt(key, 'ecb')
# image.data[42] = 0x42
# image.write_to_file(open('image_encrypted_ecb_42.ppm', 'wb'))

# # CBC
# image.encrypt(key, 'cbc')
# image.write_to_file(open('image_encrypted_cbc.ppm', 'wb'))

# # CTR
# image.encrypt(key, 'ctr')
# image.write_to_file(open('image_encrypted_ctr.ppm', 'wb'))

# GCM
image.encrypt(key, 'gcm')
image.write_to_file(open('image_encrypted_gcm.ppm', 'wb'))


image.decrypt(key)
# image.write_to_file(open('image_decrypted_gcm.ppm', 'wb'))
