import pickle
from ocr import *
from tkinter import *

class PixelBoard:
    
    def __init__(self, master, network):
        self.master = master
        self.square = 50
        self.network = network
        
        self.state = [0] * 100
        
        self.menubar = Menu(self.master)
        self.menubar.add_command(label="Exit", command=self.master.quit)
        self.master.config(menu=self.menubar)
    
        self.canvas = Canvas(self.master, bg = "white", width = 500, height = 500)
        self.canvas.bind("<Button-1>", self.click)
        self.master.bind("<Configure>", self.resize)
        self.canvas.pack(side=LEFT)
    
    def resize(self, event):
        old_square = self.square
        self.square = min(self.canvas.winfo_width(), self.canvas.winfo_height()) / 10
        if self.square == 0:
            self.square = 50
        self.update()
    
    def click(self, event):
        y = int(event.y // self.square) 
        x = int(event.x // self.square)
        self.state[10 * y + x] = 1 - self.state[10 * y + x]
        print(get_char(self.network, self.state))
        self.update()
        
    def update(self):
        s = self.square
        for i in range(10):
            for j in range(10):
                if self.state[10 * j + i]:
                    self.canvas.create_rectangle(s * i, s * j, s * (i+1), s * (j+1), fill = "gray")
                else:
                    self.canvas.create_rectangle(s * i, s * j, s * (i+1), s * (j+1), fill = "white")
        self.canvas.update_idletasks()
        
if __name__ == "__main__":
    root = Tk()
    n = load_network('ocr_save')
    app = PixelBoard(root, n)
    root.mainloop()
