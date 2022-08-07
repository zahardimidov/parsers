from tkinter import filedialog as fd
from tkinter import messagebox
from customtkinter import *
import threading
from parser import Parser


class App():
    def __init__(self, width, height):
        set_appearance_mode("light")  # Modes: system (default), light, dark
        set_default_color_theme("green")  # Themes: blue (default), dark-blue, green

        window = CTk()  # create CTk window like you do with the Tk window
        window.title('Parser')
        window.geometry(f"{width}x{height}")
        window.resizable(False, False)

        self.window=window
        self.home_page=CTkFrame(window, width=width, height=height, fg_color='white')

        CTkButton(master=self.home_page, text="Start", command=self.start_parse).place(relx=0.5, rely=0.1, anchor=CENTER)

        self.home_page.pack()

        self.load_page=CTkFrame(window, width=400, height=500, fg_color='white')
        self.load_label=CTkLabel(master=self.load_page, width=200, text="Loading...")
        self.load_label.place(relx=0.5, rely=0.35, anchor=CENTER)
        self.progressbar = CTkProgressBar(master=self.load_page)
        self.progressbar.place(relx=0.5, rely=0.45, anchor=CENTER)
        self.progressbar.set(0)

    def start_parse(self):
        path=fd.askdirectory(title="Save folder")
        if not path:return
        else: path+="/result.xlsx"

        parser=Parser(path, self.set_bar)

        try:
            file=open(path, 'w',  encoding='utf-8-sig', newline='')
            file.close()
        except: 
            self.error("Perhaps the save file is open in another program or you entered incorrect path!")
            return

        x=threading.Thread(target=parser.main)
        x.start()

        self.home_page.pack_forget()
        self.load_page.pack()

    def set_bar(self, text, value):
        self.progressbar.set(value/100,1)
        self.load_label["text"]=f"{text} {value}%"
    def error(self, text):
        messagebox.showwarning("Error", text)

if __name__=='__main__':
    application = App(400,500)
    application.window.mainloop()
