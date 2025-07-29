try:
    import cv2
except ModuleNotFoundError:
    pass


def read_img_to_rgb(img_path):
    try:
        cv2
    except NameError:
        print(
            "OpenCV is not installed. If you want to use this function, please install via pip `pip install opencv-python`"
        )
    fig = cv2.imread(img_path, cv2.IMREAD_LOAD_GDAL)
    bgr_ = cv2.split(fig)
    trans_fig = cv2.merge(bgr_[::-1]) if len(bgr_) == 3 else cv2.merge(bgr_[:3][::-1] + bgr_[-1])
    return trans_fig
