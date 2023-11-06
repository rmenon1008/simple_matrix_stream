import cv2

class Matrix:
    def __init__(self):
        pass

    def set_pixels(self, pixels):
        cv2.namedWindow("Matrix Emulator", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Matrix Emulator", 750, 375)
        cv2.imshow("Matrix Emulator", pixels)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            exit(0)

    def reset(self):
        pass