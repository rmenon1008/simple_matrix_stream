import cv2
import numpy as np

def center_crop(image, aspect_ratio):
    height, width = image.shape[:2]
    image_aspect_ratio = width / height
    if image_aspect_ratio > aspect_ratio:
        # Crop width
        new_width = int(height * aspect_ratio)
        left = (width - new_width) // 2
        right = width - new_width - left
        return image[:, left:-right]
    elif image_aspect_ratio < aspect_ratio:
        # Crop height
        new_height = int(width / aspect_ratio)
        top = (height - new_height) // 2
        bottom = height - new_height - top
        return image[top:-bottom, :]
    else:
        return image

def crop_percentages(image, crop):
    height, width = image.shape[:2]
    x1, y1, x2, y2 = crop
    return image[int(y1 / 100 * height) : int(y2 / 100 * height),
                 int(x1 / 100 * width) : int(x2 / 100 * width)]

def adjust_saturation(img, factor):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    s = np.clip(s * factor, 0, 255).astype(np.uint8)
    hsv = cv2.merge([h, s, v])
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def adjust_temperature(img, factor):
    b, g, r = cv2.split(img)
    r = np.clip(r + factor*255, 0, 255).astype(np.uint8)
    b = np.clip(b - factor*255, 0, 255).astype(np.uint8)
    img = cv2.merge([b, g, r])
    return img

def image_adjustment(image, whitepoint=[255, 255, 255], blackpoint=[0, 0, 0], saturation=1.0, temperature=0.0):
    # Apply whitepoint and blackpoint
    image = image.astype(np.float32)
    whitepoint = np.array(whitepoint, dtype=np.float32)
    blackpoint = np.array(blackpoint, dtype=np.float32)
    image = (image - blackpoint) / (whitepoint - blackpoint)
    image = np.clip(image, 0, 1)
    image = (image * 255).astype(np.uint8)

    # Apply saturation and temperature
    image = adjust_saturation(image, saturation)
    image = adjust_temperature(image, temperature)

    return image