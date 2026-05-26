# import qrcode as qr

# img = qr.make('https://www.linkedin.com/in/jainam259/')
# img.save('Jainam_Linkdin.png')

import qrcode
from PIL import Image

qr = qrcode.QRCode(version=1,
                   error_correction = qrcode.constants.ERROR_CORRECT_H,
                   box_size=10, border=4,)

qr.add_data('https://www.linkedin.com/in/jainam259/')
qr.make(fit=True)

img = qr.make_image(fill_color='black',back_color='white')
img.save('Jainam_linkdin.png')
print("QR Code Generate Successfully...")