import cv2
import os

image_folder = os.path.join("static", "images", "walls")

img = cv2.imread(os.path.join(image_folder, "s1.JPG"), 0)

# cv2.imshow('image', cv2.resize(img, (504, 672)))
# cv2.waitKey(0)
# cv2.destroyAllWindows()


img_eq = cv2.equalizeHist(img)

# cv2.imshow('image_eq', cv2.resize(img_eq, (504, 672)))
# cv2.waitKey(0)
# cv2.destroyAllWindows()

clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
img_clahe = clahe.apply(img)

# cv2.imshow('image_clahe', cv2.resize(img_clahe, (504, 672)))
# cv2.waitKey(0)
# cv2.destroyAllWindows()

img_edges = cv2.Canny(img_eq, 100, 200)

cv2.imshow('image_edges', cv2.resize(img_edges, (504, 672)))
cv2.waitKey(0)
cv2.destroyAllWindows()
