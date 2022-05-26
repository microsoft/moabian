import numpy as np
import cv2

cam = cv2.VideoCapture(0)

w = 384
h = 288
d = 32

x = int((w / 2 - d / 2))
y = int((h / 2 - d / 2))

x += -12
y += 4

cam.set(cv2.CAP_PROP_FRAME_WIDTH, w)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
cam.set(cv2.CAP_PROP_FPS, 30)

cam.set(cv2.CAP_PROP_BRIGHTNESS, 60)
cam.set(cv2.CAP_PROP_CONTRAST, 100)

_, img = cam.read()
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

cropped = hsv[y : y + d, x : x + d]
cv2.imwrite("/tmp/cropped.jpg", cropped, [cv2.IMWRITE_JPEG_QUALITY, 90])
cv2.imwrite("/tmp/img.jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 90])
cv2.imwrite("/tmp/hsv.jpg", hsv, [cv2.IMWRITE_JPEG_QUALITY, 90])

# m = np.array(cropped)
