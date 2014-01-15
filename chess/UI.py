from Tkinter import * # change to "tkinter" if using python3
from PIL import ImageTk, Image
# the module imported below contains the computer Brain
from AI import *
import cProfile

class Board:
    
    pieces = {0: 0, 2:'Q', -5: 'b', 6:'P', -1:'k', 5:'B', -4:'n', -2:'q', -6:'p', -3:'r', 3:'R', 4:'N', 1:'K'}
    Tpieces = {0: 0, 'Q': 2, 'b': -5, 'P': 6, 'k': -1, 'B': 5, 'n': -4, 'q': -2, 'p': -6, 'r': -3, 'R': 3, 'N': 4, 'K': 1}
    position = Position([3, 4, 5, 2, 1, 5, 4, 3, 6, 6, 6, 6, 6, 6, 6, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -6, -6, -6, -6, -6, -6, -6, -6, -3, -4, -5, -2, -1, -5, -4, -3], -1,
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 2, 2, 3, 2, 2, 3, 2, 2, 1, 1, 1, 4, 4, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 4, 4, 1, 1, 1, 2, 2, 3, 2, 2, 3, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            True, True, False, True, True, False)
        # pieces: ['p','b','n','r','q','k',0,'K','Q','R','N','B','P']
        # values: [-6, -5, -4, -3, -2, -1, 0, 1,  2,  3,  4,  5,  6]
    human = -1 # side that human is playing on (white = -1)
    moves = generate_moves(position)

    def __init__(self, master):
        self.master = master
        self.brain = Brain()
        
        self.menubar = Menu(self.master)
        self.menubar.add_command(label="Exit", command=self.master.quit)
        self.master.config(menu=self.menubar)
        
        self.analysis_display = StringVar()
        Label(master, width = 30, textvariable=self.analysis_display, font=("Helvetica", 12)).pack(side=LEFT, fill=Y)
        self.analysis_display.set("Analysis")

        self.move_list_text = Text(self.master, width = 30)
        self.move_list_text.pack(side=LEFT, fill=Y)
        self.move_list_text.insert(INSERT, "#   white      black     \n")
        self.move_list_text.insert(INSERT, "1   ")
        self.num_move = 1

        self.canvas = Canvas(self.master, bg="white", width=400, height=400)
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<ButtonRelease-1>", self.drop)
        self.canvas.pack(side=LEFT)
        
        self.canvas_heat = Canvas(self.master, bg="white", width=400, height=400)
        self.canvas_heat.pack(side=LEFT)
        
        self.square = 50
        self.selected = None
        
        self.ims = {} # load images
        keys = [-5, -4, -2, -6, -3, -1, 5, 4, 2, 6, 3, 1]
        for i,s in zip(keys, ['wb', 'wn', 'wq', 'wp', 'wr', 'wk', 'bb', 'bn', 'bq', 'bp', 'br', 'bk']): 
            im = Image.open("res/300/" + s + ".png")
            im = im.resize((self.square, self.square), Image.ANTIALIAS)
            self.ims[i] = ImageTk.PhotoImage(im)
        
        self.update_with_board()
        self.update_with_heatmap()
        
        self.master.bind("<Configure>", self.resize)
    
    def update_with_board(self):
        if not self.position:
            print("game is over")
            self.canvas.update_idletasks()
            return
        self.canvas.delete(ALL)
        for i in range(8):
            for j in range(8):
                color = "gray" if (i+j) % 2 else "white"
                self.canvas.create_rectangle(self.square * i, self.square * j, self.square * (i+1), self.square * (j+1), fill=color)
                if self.position.board[8 * j + i] in self.ims.keys():
                    self.canvas.create_image(self.square * i + self.square/2,
                    self.square * j + self.square/2, image = self.ims[self.position.board[8 * j + i]])
        self.canvas.update_idletasks()
    
    def update_with_heatmap(self):
        if not self.position:
            print("game is over")
            self.canvas.update_idletasks()
            return
        self.canvas_heat.delete(ALL)
        for i in range(8):
            for j in range(8):
                color = "gray" if (i+j) % 2 else "white"
                self.canvas_heat.create_rectangle(self.square * i, self.square * j, self.square * (i+1), self.square * (j+1), fill=color)
                self.canvas_heat.create_text(self.square * i + self.square/2,
                    self.square * j + self.square/2, text = str(self.position.white_heat_map[8 * j + i]) + "|" + str(self.position.black_heat_map[8 * j + i]))
        self.canvas_heat.update_idletasks()
    
    def click(self, event):
        self.selected = event.y / self.square * 8 + event.x / self.square
        
    def drop(self, event):
        e = event.y / self.square * 8 + event.x / self.square
        move = (self.selected, e, 0)
        if self.position.board[self.selected] == -6:
            if event.y / self.square * 8 == 0:
                move = (self.selected, e, 2)
            elif e - self.selected == -16:
                move = (self.selected, e, 4)
            elif self.human == -1 and self.position.white_en_passant:
                if self.selected == self.position.white_en_passant[0] and e == self.selected - 7:
                    move = (self.selected, e, 3)
                elif self.selected == self.position.white_en_passant[1] and e == self.selected - 9:
                    move = (self.selected, e, 3)
            elif self.human == 1 and self.position.black_en_passant:
                if self.selected == self.position.black_en_passant[0] and e == self.selected + 9:
                    move = (self.selected, e, 3)
                elif self.selected == self.position.black_en_passant[1] and e == self.selected + 7:
                    move = (self.selected, e, 3)
        elif self.position.board[self.selected] == 6:
            if event.y / self.square * 8 == 7:
                move = (self.selected, e, 2)
            elif e - self.selected == 16:
                move = (self.selected, e, 5)
        elif abs(self.position.board[self.selected]) == 1:
            if e - self.selected == 2:
                move = (self.selected, e, 1)
            elif self.selected - e == 2:
                move = (self.selected, e, 1)
                
        if self.selected:
            if self.position.side != self.human:
                print("not your turn!")
                return
            if move not in self.moves:
                print("invalid move")
                return
            valid_move = make_move(deepcopy(self.position), *move)
            if not valid_move:
                print("invalid move")
                return
            self.position = valid_move
            self.move_list_text.insert(INSERT, move_to_string(move) + " " * (11 - len(move_to_string(move))))
            
            self.update_with_board()
            self.update_with_heatmap()
            
            print(move)

            ai_move = self.brain.get_move(self.position)
            self.position = make_move(self.position, *ai_move)
            self.move_list_text.insert(INSERT, move_to_string(ai_move) + " " * (11 - len(move_to_string(ai_move))))
            
        self.update_with_board()
        self.update_with_heatmap()
        
        self.num_move = self.num_move + 1
        self.move_list_text.insert(INSERT, "\n" + str(self.num_move) + " " * (4 - len(str(self.num_move))))
        
        self.moves = generate_moves(self.position)
        
        if not any(make_move(deepcopy(self.position), *move) for move in self.moves):
            if self.position.side < 0 and position.black_heat_map[self.position.board.index(-1)] or self.position.side > 0 and self.position.white_heat_map[self.position.board.index(1)]:
                print "Checkmate!"
            else:
                print "Stalemate!"
            
        
    def resize(self, event):
        old_square = self.square
        self.square = min(self.canvas.winfo_width(), self.canvas.winfo_height())/8
        if self.square == 0:
            self.square = 50
        
        if old_square != self.square:
            self.ims = {} # reload images
            keys = [-5, -4, -2, -6, -3, -1, 5, 4, 2, 6, 3, 1]
            for i,s in zip(keys, ['wb', 'wn', 'wq', 'wp', 'wr', 'wk', 'bb', 'bn', 'bq', 'bp', 'br', 'bk']): 
                im = Image.open("res/300/" + s + ".png")
                im = im.resize((self.square, self.square), Image.ANTIALIAS)
                self.ims[i] = ImageTk.PhotoImage(im)
        
        self.update_with_board()
        self.update_with_heatmap()

if __name__ == "__main__":
    root = Tk()
    app = Board(root)
    root.mainloop()
