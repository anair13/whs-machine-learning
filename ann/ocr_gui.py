import pickle
version = 3
try: # python 3
    from tkinter import *
    from ocr import *
except ImportError: # python 2
    version = 2
    from Tkinter import *
    from PIL import Image
    from img_to_txt import *

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

class DrawingBoard:
    
    def __init__(self, master, network):

        self.master = master
        self.square = 50
        self.radius = 15
        self.network = network
        self.up = False
        
        # self.image = Image.new("RGB", (1200, 900), (255, 255, 255))
        # self.draw = ImageDraw.Draw(image1)
        
        self.menubar = Menu(self.master)
        self.menubar.add_command(label="Exit", command=self.master.quit)
        self.master.config(menu=self.menubar)
    
        self.canvas = Canvas(self.master, bg = "white", width = 1200, height = 900)
        self.canvas.bind("<Motion>", self.motion)
        self.canvas.bind("<ButtonPress-1>", self.click)
        self.canvas.bind("<ButtonRelease-1>", self.release)
        self.master.bind("<Configure>", self.resize)
        self.canvas.pack(side=LEFT)
    
    def resize(self, event):
        old_square = self.square
        self.square = min(self.canvas.winfo_width(), self.canvas.winfo_height()) / 10
        if self.square == 0:
            self.square = 50
        self.update()
    
    def click(self, event):
        self.up = True
        self.draw_circle(event)
        self.update()
    
    def motion(self, event):
        if self.up:
            self.draw_circle(event)
        self.update()
    
    def draw_circle(self, event):
        self.canvas.create_oval(event.x - self.radius, event.y - self.radius, 
                                event.x + self.radius, event.y + self.radius,
                                fill="black")
    
    def release(self, event):
        self.up = False
        
    def update(self):
        self.canvas.update_idletasks()

if __name__ == "__main__":
    root = Tk()
    n = load_network('ocr_save')
    app = PixelBoard(root, n)
    root.mainloop()
