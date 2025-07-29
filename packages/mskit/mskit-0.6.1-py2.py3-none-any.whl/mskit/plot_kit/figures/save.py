import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_pdf import PdfPages


def save_pdf(path):
    with PdfPages(path) as pdf:
        pdf.savefig()


def to_array(figure=None):
    if figure is None:
        figure = plt.gcf()
    canvas = FigureCanvasAgg(figure)
    canvas.draw()
    image_array = np.array(canvas.renderer.buffer_rgba())
    return image_array
