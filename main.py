import os
from tkinter import Tk, filedialog, Button, Toplevel, Frame, Scale, W, Entry, HORIZONTAL, NSEW

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def open_file_dialog():
    filepath = filedialog.askopenfilename(
        title='Выберите cube_file.txt',
        filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
    )
    if filepath:
        app_directory = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.basename(filepath)
        path = os.path.join(app_directory, filename)
        load_main_window(path)


def read_cube(filename):
    object = []
    with open(filename, 'r') as f:
        for s in f:
            s += ' 1'
            object.append(s.split())
        object = np.array(object).astype(float)
    return object


def create_slider(window, handler, row, column, start=0, to=100, label=None):
    slider = Scale(window, from_=start, to=to, resolution=1, length=250, orient=HORIZONTAL,
                        label=label, command=handler)
    slider.grid(row=row, column=column, sticky=W)
    return slider

def create_entry(window, row, column):
    entry = Entry(window)
    entry.grid(row=row, column=column, sticky=W)
    return entry

def on_k1_changed(value):
    global k1
    if value == '':
        return
    k1 = float(value)
    update()

def on_Znear_changed(value):
    global Znear
    if value == '':
        return
    Znear = float(value)
    update()

def on_Zfar_changed(value):
    global Zfar
    if value == '':
        return
    Zfar = float(value)
    update()

def on_dx_changed(value):
    global dx
    if value == '':
        return
    dx = float(value)
    update()

def on_dy_changed(value):
    global dy
    if value == '':
        return
    dy = float(value)
    update()

def on_camera_rotation_x_changed(value):
    global Cam
    if value == '':
        return
    Cam[0, 0] = float(value)
    update()

def on_camera_rotation_y_changed(value):
    global Cam
    if value == '':
        return
    Cam[1, 1] = float(value)
    update()

def on_rotation_changed(value):
    global P
    if value == '':
        return
    angle = np.radians(float(value))
    P[0, 0] = np.cos(angle)
    P[0, 1] = -np.sin(angle)
    P[1, 0] = np.sin(angle)
    P[1, 1] = np.cos(angle)
    update()

def load_main_window(filepath):
    global object, ax, canvas, Zfar_entry, Znear_entry, dx_entry, dy_entry, k1_entry, rotation_entry, \
        cam_x_rotation_entry, cam_y_rotation_entry
    main_window = Toplevel(window)
    main_window.title("Имитатор фотокамеры с искажениями")
    main_window.geometry("960x600")
    object = read_cube(filepath)

    frame = Frame(main_window)
    frame.grid(row=0, column=0, columnspan=6)

    fig, ax = plt.subplots()
    fig.set_size_inches(5, 3)
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=0, columnspan=3, sticky=NSEW)

    create_slider(main_window, on_Zfar_changed, 1, 0, start=-100, to=100, label='Zfar')
    Zfar_entry = Entry(main_window)
    Zfar_entry.grid(row=1, column=1, sticky=W)

    create_slider(main_window, on_Znear_changed, 2, 0, start=-100, to=100, label='Znear')
    Znear_entry = Entry(main_window)
    Znear_entry.grid(row=2, column=1, sticky=W)

    create_slider(main_window, on_dx_changed, 3, 0, start=-10, to=10, label='dx')
    dx_entry = Entry(main_window)
    dx_entry.grid(row=3, column=1, sticky=W)

    create_slider(main_window, on_dy_changed, 4, 0, start=-10, to=10, label='dy')
    dy_entry = Entry(main_window)
    dy_entry.grid(row=4, column=1, sticky=W)

    create_slider(main_window, on_k1_changed, 1, 3, start=-10, to=10, label='k1')
    k1_entry = Entry(main_window)
    k1_entry.grid(row=1, column=4, sticky=W)

    create_slider(main_window, on_rotation_changed, 2, 3, start=-180, to=180, label='Rotation xy')
    rotation_entry = Entry(main_window)
    rotation_entry.grid(row=2, column=4, sticky=W)

    create_slider(main_window, on_camera_rotation_x_changed, 3, 3, start=-10, to=10, label='Camera X rotation')
    cam_x_rotation_entry = Entry(main_window)
    cam_x_rotation_entry.grid(row=3, column=4, sticky=W)

    create_slider(main_window, on_camera_rotation_y_changed, 4, 3, start=-10, to=10, label='Camera Y rotation')
    cam_y_rotation_entry = Entry(main_window)
    cam_y_rotation_entry.grid(row=4, column=4, sticky=W)

    apply_btn = Button(main_window, text="Apply", width=10, command=update_values)
    apply_btn.grid(row=5, column=3, sticky=W)

    update()

def update():
    global object, ax, canvas, Zfar, Znear, dx, dy, P, Cam, K1
    Zrange = Zfar - Znear
    if Zrange == 0:
        return
    P[0, 2] = dx
    P[1, 2] = dy
    P[2, 2] = -Zfar / Zrange
    P[2, 3] = Znear * Zfar / Zrange
    ax.clear()
    dots = []
    for i in range(object.shape[0]):
        f = Cam @ P @ object[i, :]
        dots.append(f / f[2])
    dots = np.array(dots)
    dots_center = np.array([0.1, 0.1])
    K2 = 0.0
    r = (dots[:, :2] - dots_center) ** 2
    f1 = (r).sum(axis=1)
    f2 = (r ** 2).sum(axis=1)
    mask = np.expand_dims(K1 * f1 + K2 * f2, axis=-1)
    dots_new = (dots[:, :2]) + (dots[:, :2] - dots_center) * mask
    ax.plot(dots_new[:, 0], dots_new[:, 1], '-D')
    ax.set_aspect('equal')
    canvas.draw()

def update_values():
    global Zfar_entry, Znear_entry, dx_entry, dy_entry, k1_entry, rotation_entry, cam_x_rotation_entry, cam_y_rotation_entry
    on_Zfar_changed(Zfar_entry.get())
    on_Zfar_changed(Znear_entry.get())
    on_Zfar_changed(dx_entry.get())
    on_Zfar_changed(dy_entry.get())
    on_Zfar_changed(k1_entry.get())
    on_Zfar_changed(rotation_entry.get())
    on_Zfar_changed(cam_y_rotation_entry.get())
    on_Zfar_changed(cam_x_rotation_entry.get())

window = Tk()
window.title("Имитатор фотокамеры с искажениями")
window.geometry("500x250")

button = Button(window, text="Выбрать файл", command=open_file_dialog)
button.pack()

Znear = -3
Zfar = -10
dx = -0.2
dy = -0.5
P = np.array([[1, 0, dx, 0],
            [0, 1, dy, 0],
            [0, 0, -Zfar / (Zfar - Znear), Znear * Zfar / (Zfar - Znear)],
            [0, 0, 1, 0]])

Cam = np.array([[1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0]])

k1 = 1
object = None
ax = None
canvas = None
(Zfar_entry, Znear_entry, dx_entry, dy_entry,
 k1_entry, rotation_entry, cam_x_rotation_entry, cam_y_rotation_entry) = None, None, None, None, None, None, None, None

window.mainloop()
