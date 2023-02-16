import tkinter
from tkinter import filedialog as fd

import matplotlib.pyplot as plt
# plt.rcParams['text.usetex'] = True
from matplotlib import rc
rc('font',**{'family':'serif'})
# rc('text.latex',preamble="\\usepackage[utf8]{inputenc}")
# rc('text.latex',preamble="\\usepackage[russian]{babel}")

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import numpy as np

# Создание основного окна.
root = tkinter.Tk()
# Заголовок основного окна.
root.wm_title("Измеритель толщины")

cap0 = tkinter.Label(text="Выбор файлов с спектрами")
cap0.grid(row=0, column=0)
cap3 = tkinter.Label(text="Спектры:")
cap3.grid(row=0, column=1)
choose_spec_frame = tkinter.Frame(root)
cap1 = tkinter.Label(choose_spec_frame, text="Спектр от подложки:")
cap1.grid(row=0, column=0)
cap2 = tkinter.Label(choose_spec_frame, text="Спектр от плёнки:")
cap2.grid(row=2, column=0)
norm_spec = tkinter.IntVar()
norm_spec_but = tkinter.Checkbutton(choose_spec_frame, text="Нормировать спектры на полную интенсивность",
                                    onvalue=1,offvalue=0, variable=norm_spec)
norm_spec_but.grid(row=5,column=0)


def choose_si_spec():
    si_name = fd.askopenfilename()
    global data_si
    global norm_data_si
    global norm_si
    data_si = np.loadtxt(si_name)
    norm_data_si = data_si.copy()
    norm_si = 0.0
    d_lambda = data_si[1, 0] - data_si[0, 0]
    for v in data_si[:, 1]:
        norm_si += d_lambda * v
    norm_data_si[:, 1] = norm_data_si[:, 1] / norm_si
    choose_spec_si_but.config(text=si_name)


def choose_o_spec():
    o_name = fd.askopenfilename()
    global data_o
    global norm_data_o
    global norm_o
    data_o = np.loadtxt(o_name)
    norm_data_o = data_o.copy()
    norm_o = 0.0
    d_lambda = data_o[1, 0] - data_o[0, 0]
    for v in data_o[:, 1]:
        norm_o += d_lambda * v
    norm_data_o[:, 1] = norm_data_o[:, 1] / norm_o
    choose_spec_o_but.config(text=o_name)


def plot_spectrum():
    ax.clear()
    if norm_spec.get():
        ax.plot(data_si[:,0],data_si[:,1]/norm_si,c='r',label='подложка')
        ax.plot(data_o[:,0],data_o[:,1]/norm_o,c='b',label='плёнка')
    else:
        ax.plot(data_si[:, 0], data_si[:, 1], c='r', label='подложка')
        ax.plot(data_o[:, 0], data_o[:, 1], c='b', label='плёнка')
    ax.set_xlabel("длина волны, нм")
    ax.grid()
    ax.legend()
    spec_canvas.draw()


choose_spec_si_but = tkinter.Button(choose_spec_frame, text='...', command=choose_si_spec)
choose_spec_si_but.grid(row=1, column=0)
choose_spec_o_but = tkinter.Button(choose_spec_frame, text='...', command=choose_o_spec)
choose_spec_o_but.grid(row=3, column=0)
plot_spectrum_but = tkinter.Button(choose_spec_frame, text="Построить спектры.", command=plot_spectrum)
plot_spectrum_but.grid(row=4, column=0)
choose_spec_frame.grid(row=1, column=0,sticky='n')

# Отрисовка графика средствами matplotlib
fig = Figure(figsize=(5, 4), dpi=80)
ax = fig.add_subplot(111)
ax.scatter([0.0],[0.0],c='r', label='подложка')
ax.scatter([0.0],[0.0],c='b', label='плёнка')
ax.set_xlabel("длина волны, нм")
ax.grid()
ax.legend()
# Отрисовка графика средствами matplotlib
fig_calc = Figure(figsize=(5, 4), dpi=80)
ax_calc = fig_calc.add_subplot(111)
ax_calc.scatter([0.0],[0.0],c='r', label='теория')
ax_calc.scatter([0.0],[0.0],c='b', label='эксперимент')
ax_calc.set_xlabel("обратная длина волны, нм^(-1)")
ax_calc.grid()
ax_calc.legend()

# Элемент с графиком
spec_canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
spec_canvas.draw()
spec_canvas.get_tk_widget().grid(row=1, column=1)
calc_canvas = FigureCanvasTkAgg(fig_calc,master=root)
calc_canvas.draw()
calc_canvas.get_tk_widget().grid(row=3, column=1)


def plot_calc():
    n = float(n_field.get())
    nr = float(nr_field.get())
    h = float(h_field.get())*10**(-9)
    min_idx = int(len(data_o[:, 0]) * 0.08)
    ll_idx = min_idx
    lr_idx = -min_idx
    ll = data_o[ll_idx,0]
    rl = data_o[lr_idx,0]
    # ll = 400
    # rl = 700
    N = 1000
    r1 = (-1 + n) / (1 + n)
    r2 = (-n + nr) / (n + nr)
    k0_l = 2 * np.pi / rl / 1e-9;
    k0_r = 2 * np.pi / ll / 1e-9;
    K = np.linspace(k0_l, k0_r, N, endpoint=True)
    R = K.copy()
    for i, k in enumerate(K):
        rc = (r1 + r2 * np.exp(-2.0 * 1j * k * n * h)) / ((1.0 + r1 * r2 * np.exp(-2.0 * 1j * k * n * h)))
        r = abs(rc)
        R[i] = r
    L = (2 * np.pi / K) * 10 ** 9
    ax_calc.clear()
    ax_calc.plot(1/L,R,c='r', label='теория')
    ax_calc.plot(1/data_o[ll_idx:lr_idx,0],data_o[ll_idx:lr_idx,1]/data_si[ll_idx:lr_idx,1],c='b',label="эксперимент")
    ax_calc.set_xlabel("обратная длина волны, нм^(-1)")
    ax_calc.grid()
    ax_calc.legend()
    calc_canvas.draw()

# Расчёт коэффициента отражения
calc_frame = tkinter.Frame(root)
calc_label = tkinter.Label(root,text="Параметры расчёта")
calc_label.grid(row=2,column=0)
nr_label = tkinter.Label(calc_frame,text="К-т преломления подложки n_r:")
nr_label.grid(row=1,column=0)
nr_field = tkinter.Entry(calc_frame)
nr_field.grid(row=2,column=0)
n_label = tkinter.Label(calc_frame,text="К-т преломления плёнки n:")
n_label.grid(row=3,column=0)
n_field = tkinter.Entry(calc_frame)
n_field.grid(row=4,column=0)
h_label = tkinter.Label(calc_frame,text="Толщина плёнки h (нм):")
h_label.grid(row=5,column=0)
h_field = tkinter.Entry(calc_frame)
h_field.grid(row=6,column=0)
calc_but = tkinter.Button(calc_frame,text="Построить",command=plot_calc)
calc_but.grid(row=7,column=0)
calc_frame.grid(row=3,column=0,sticky='n')
calc_frame_label = tkinter.Label(root,text="Коэффициенты отражения")
calc_frame_label.grid(row=2,column=1)

def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

button = tkinter.Button(master=root, text="Quit", command=_quit)
button.grid(row=7, column=0)

tkinter.mainloop()
# If you put root.destroy() here, it will cause an error if the window is
# closed with the window manager.