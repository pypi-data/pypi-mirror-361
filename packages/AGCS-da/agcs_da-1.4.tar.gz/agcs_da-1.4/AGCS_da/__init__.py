__author__ = 'development2'
__version__ = '1.4'
__email__ = 'agcs-development@yandex.ru'
import os
import sys
from tkinter import *
from tkinter.scrolledtext import ScrolledText
import ctypes

def run_as_admin():
    script = sys.executable
    params = ' '.join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", script, params, None, 1)

# Проверка, запущен ли уже с правами администратора
if not ctypes.windll.shell32.IsUserAnAdmin():
    # Запрос прав администратора
    run_as_admin()
    sys.exit()  # Остановить текущий скрипт, если он перезапускается с правами

def translator (cod, libr):
    cod_2 = []
    for i_1 in cod:
        i_1 = i_1.split(' ')
        b = ''
        for i_2 in i_1:
            if i_2 in libr:
                b += str(libr[i_2])
            else:
                b += str(i_2)
        cod_2 += [b]
    return cod_2
#'Наш аналог в коде':'Функция обозначающая из пайтон'
def AGCS (library = {}):
    global lib
    lib = library
    window = Tk()
    window.title("Карманная среда разработки")
    width= window.winfo_screenwidth() 
    height= window.winfo_screenheight()
    window.geometry("%dx%d" % (width, height))
    global txt
    txt = ScrolledText(window, width=width, height=35)
    txt.pack(fill=BOTH)
    def clicked():
        global lib
        global txt
        a = txt.get('1.0', 'end-1c')
        cod = translator(a.split('\n'), lib)
        try:
            os.remove('Runer.py')
        except:
            pass
        try:
            os.remove('1.cmd')
        except:
            pass
        file = open('Runer.py', 'a', encoding='UTF-8')
        for i in cod:
            file.write(f"{i}\n")
        file.write("input()")
        file.close()
        os.system('Runer.py')
    def open_():
        open__ = Tk ()
        txt_2 = Entry(open__,width=70)
        txt_2.grid(column=0, row=0)
        def open___ ():
            global txt
            file = open(fr"{str(txt_2.get())}", 'r', encoding='UTF-8')
            content = file.read()
            file.close()
            txt.delete('1.0', 'end')
            txt.insert('1.0', content)
            open__.destroy()
        def SAVE_AS ():
            global txt
            try:
                os.remove(fr"{str(txt_2.get())}")
            except:
                  pass
            f = open(file=fr"{str(txt_2.get())}", mode='x', encoding='UTF-8')
            f.write(txt.get('1.0', 'end-1c'))
            f.close()
            open__.destroy()
        Button(open__, text="OPEN", command=open___).grid(column=0, row=1)
        Button(open__, text="SAVE AS", command=SAVE_AS).grid(column=0, row=2)
        open__.mainloop()
    
    Button(window, text="____RUN____", width=100, height=1, command=clicked).pack(fill=BOTH)
    Button(window, text="____OPEN / SAVE AS____", width=100, height=1, command=open_).pack(fill=BOTH)
    window.mainloop()
AGCS()