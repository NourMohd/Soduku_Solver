import pyglet
from pyglet import shapes
from Logic import Board

class TextWidget:
    def __init__(self, i, j,offset, width, batch,foregroundBatch):
        self.i = i
        self.j = j
        self.x = offset+i*width
        self.y = offset+j*width
        fontSize = int(width*0.5)
        self.document = pyglet.text.document.UnformattedDocument('0')
        self.document.set_style(0, len(self.document.text), dict(color=(0, 0, 0, 255),font_size=fontSize))

        self.layout = pyglet.text.layout.IncrementalTextLayout(self.document, width, width, batch=foregroundBatch)
        # Calculate the center of the square
        center_x = self.x + width / 2
        center_y = self.y - width / 2
        # Calculate the center of the text
        text_width = self.layout.content_width
        text_height = self.layout.content_height
        # Position the layout so the text is centered
        self.layout.position = center_x - text_width / 2, center_y + text_height / 2, 0
        self.defaultColor = (200, 200, 225)
        self.activeColor = (255, 255, 255)
        self.highlightColor = (200, 255, 200)
        self.inconColor = (255, 200, 200)
        self.square = pyglet.shapes.Rectangle(self.x, self.y, width, width,self.defaultColor , batch)
        self.document.text = ''

    def hit_test(self, x, y):
        return (0 < x - self.x < self.layout.width and
                0 < y - self.y < self.layout.height)
class Button:
    def __init__(self,x,y,text,width,height, batch,callback= None):
        self.x = x
        self.y = y
        fontSize = int(height*0.3)
        self.document = pyglet.text.document.UnformattedDocument(text)
        self.document.set_style(0, len(self.document.text), dict(color=(255, 255, 255, 255),font_size=fontSize))

        self.layout = pyglet.text.layout.TextLayout(self.document, width, height, batch=batch)
        # Calculate the center of the square
        center_x = self.x + width / 2
        center_y = self.y - height / 2
        # Calculate the center of the text
        text_width = self.layout.content_width
        text_height = self.layout.content_height
        # Position the layout so the text is centered
        self.layout.position = center_x - text_width / 2, center_y + text_height / 2, 0
        self.defaultColor = (50, 50, 50)
        self.hoverColor = (150, 150, 150)
        self.rect = pyglet.shapes.Rectangle(self.x, self.y, width, height,self.defaultColor , batch)
        #self.rect = pyglet.shapes.Ellipse(center_x, center_y, width, height, color=self.defaultColor , batch=batch)
        self.callback = callback
    def hit_test(self, x, y):
        return (0 < x - self.x < self.layout.width and
                0 < y - self.y < self.layout.height)

class HUD:
    def __init__(self,HUD_offset, HUD_size, game_offset,game_size, batch) -> None:
        self.offset = HUD_offset
        self.size = HUD_size
        self.game_offset = game_offset
        self.game_size = game_size
        window_size = HUD_offset+HUD_size
        self.unsatColor = (255, 200, 200,255)
        self.defaultColor = (255, 200, 200,0)
        self.lockedColor = (200, 200, 200,255)
        self.labels = list()
        self.labels.append(pyglet.text.Label('Domain',
                          font_name='Times New Roman',
                          font_size=26,
                          x=self.offset+(self.size//2)+10, y=window_size*0.95,
                          batch=batch,
                          anchor_x="center",
                          anchor_y="top",
                          color=(0, 0, 0, 255)))
        self.title = pyglet.text.Label('SODUKU',
                          font_name='Times New Roman',
                          font_size=50,
                          x=window_size//2, y=window_size*0.95,
                          batch=batch,
                          anchor_x="center",
                          anchor_y="top",
                          color=(0, 0, 0, 255))
        self.domain = pyglet.text.Label('',
                          font_name='Times New Roman',
                          font_size=26,
                          x=self.offset+(self.size), y=window_size * 0.9,
                          batch=batch,
                          anchor_x="center",
                          anchor_y="top",
                          color=(0, 0, 0, 255),multiline=True,width=self.size)
        self.buttons = list()
        self.buttons.append(Button(25,window_size*0.1,"Lock",150,100,batch,lambda x: x.lock_grid()))
        self.buttons.append(Button(25,window_size*0.6,"Gen",150,100,batch,lambda x: x.gen_board()))
        self.buttons.append(Button(25,window_size*0.75,"Solve",150,100,batch,lambda x: x.solve_board()))
        self.buttons.append(Button(25,window_size*0.25,"Clear",150,100,batch,lambda x: x.clear_board()))

    def update_domain(self,var):
        if(len(var.domain)==0):
            self.domain.text = "∅"
            return
        rep = str(var.domain).replace(', ','\n')[1:-1]
        self.domain.text = rep

        
    def getUnsatWidget(self,i, j,offset, width, batch):
        x = offset+i*width
        y = offset+j*width
        return pyglet.shapes.Rectangle(x, y, width, width,self.defaultColor , batch)

class Window(pyglet.window.Window):
    window_size = 1000
    game_size = 600
    game_offset = (window_size-game_size)//2
    cell_size = game_size // 9
    game_size = cell_size*9
    HUD_offset = game_offset+game_size
    HUD_size = window_size-HUD_offset
    def __init__(self, *args, **kwargs):
        self.Board = Board(self.handle_incon)
        self.HUD = None
        pyglet.gl.glClearColor(1,1,1,1)
        super(Window, self).__init__(self.window_size,self.window_size, caption='Soduko', *args, **kwargs)
        self.batches = list()
        self.textWidgets = list()
        self.unsatWidgets = list()
        self.text_cursor = self.get_system_mouse_cursor('text')
        self.draw_init()
        self.focus = None
    def draw_board(self):
        for k,widget in enumerate(self.textWidgets):
            i,j = self.index_to_cart(k)
            val = self.Board[i][j].val
            if val:
                widget.document.text = str(val)
            else:
                widget.document.text = ''
    def draw_init(self):
        Gridbatch = pyglet.graphics.Batch()
        Textbatch = pyglet.graphics.Batch()
        HUDBatch =  pyglet.graphics.Batch()
        foregroundBatch = pyglet.graphics.Batch()
        self.batches.append(Textbatch)
        self.batches.append(HUDBatch)
        self.batches.append(foregroundBatch)
        self.batches.append(Gridbatch)   
        self.HUD = HUD(self.HUD_offset,self.HUD_size,self.game_offset,self.game_size,HUDBatch)
        self.labels = self.HUD.labels
        self.lines = list()
        game_offset = self.game_offset
        game_size = self.game_size
        cell_size = self.cell_size
        self.lines.append(shapes.Line(game_offset,  game_offset, game_offset+game_size, game_offset, 2, color = (0, 0, 0), batch = Gridbatch))
        self.lines.append(shapes.Line(game_offset, game_offset,  game_offset, game_offset+game_size, 2, color = (0, 0, 0), batch = Gridbatch))
        self.lines.append(shapes.Line(game_offset,  game_offset+9*cell_size, game_offset+game_size, game_offset+9*cell_size, 2, color = (0, 0, 0), batch = Gridbatch))
        self.lines.append(shapes.Line(game_offset+9*cell_size, game_offset,  game_offset+9*cell_size, game_offset+game_size, 2, color = (0, 0, 0), batch = Gridbatch))
        for i in range(1,9):
                for j in range(1,9):
                    # Draw thicker lines for the 3x3 squares
                    if i % 3 == 0 and i > 0:
                        self.lines.append(shapes.Line(game_offset,  game_offset+i*cell_size, game_offset+game_size, game_offset+i*cell_size, 2, color = (0, 0, 0), batch = Gridbatch))
                    else:
                        self.lines.append(shapes.Line(game_offset,  game_offset+i*cell_size, game_offset+game_size, game_offset+i*cell_size, 1, color = (50, 50, 50), batch = Gridbatch))
                    if j % 3 == 0 and j > 0:
                        self.lines.append(shapes.Line(game_offset+j*cell_size, game_offset,  game_offset+j*cell_size, game_offset+game_size, 2, color = (0, 0, 0), batch = Gridbatch))
                    else:
                        self.lines.append(shapes.Line(game_offset+j*cell_size, game_offset,  game_offset+j*cell_size, game_offset+game_size, 1, color = (50, 50, 50), batch = Gridbatch))
        for i in range(9):
            for j in range(9):
                self.textWidgets.append(TextWidget( i, j,game_offset, cell_size, Textbatch,foregroundBatch))
                self.unsatWidgets.append(self.HUD.getUnsatWidget(i, j,game_offset, cell_size, HUDBatch))
        
    def handle_incon(self,unsats):
        for widget in self.unsatWidgets:
            if (widget.color ==self.HUD.unsatColor):
                widget.color = self.HUD.defaultColor
        for var in unsats:
            if not var.readOnly:
                k = self.cart_to_index(var.i,var.j)
                self.unsatWidgets[k].color = self.HUD.unsatColor
    def set_focus(self, focus):
        if focus is self.focus:
            return
        if self.focus:
            self.focus.square.color = self.focus.defaultColor
            k = self.textWidgets.index(self.focus)
            i,j = self.index_to_cart(k)
            activeVar = self.Board[i][j]
            for var in self.Board.arcs[activeVar]:
                i,j = var.i,var.j
                k = self.cart_to_index(i,j)
                self.textWidgets[k].square.color = self.textWidgets[k].defaultColor
        self.focus = focus
        if self.focus:
            k = self.textWidgets.index(self.focus)
            i,j = self.index_to_cart(k)
            activeVar = self.Board[i][j]
            self.HUD.update_domain(activeVar)
            self.focus.square.color = self.textWidgets[k].activeColor
            for var in self.Board.arcs[activeVar]:
                i,j = var.i,var.j
                k = i+j*9
                self.textWidgets[k].square.color = self.textWidgets[k].highlightColor
    def on_mouse_press(self, x, y, button, modifiers):
        for widget in self.HUD.buttons:
            if widget.hit_test(x,y):
                widget.callback(self)
                return
        for widget in self.textWidgets:
            if widget.hit_test(x, y):
                self.set_focus(widget)
                break
            else:
                self.set_focus(None)
    def on_mouse_motion(self, x, y, dx, dy):
        for widget in self.HUD.buttons:
            widget.rect.color = widget.defaultColor
            if widget.hit_test(x, y):
                widget.rect.color = widget.hoverColor
                break
    def on_text(self, text):
        if self.focus:
            if(text.isnumeric() and text !='0'):
                k = self.textWidgets.index(self.focus)
                i,j = self.index_to_cart(k)
                active_var = self.Board[i][j]
                active_var.set_val(int(text))
                self.focus.document.text = str(active_var.val)
                self.Board.force_consistency()
                self.HUD.update_domain(active_var)
    def cart_to_index(self,i,j):      
        return i+j*9
    def index_to_cart(self,k):
        j = (k//9)%9
        i = (k-j*9)%9
        return i,j
    def gen_board(self):
        board = self.Board.generate_sudoku()
        self.Board = board
        self.draw_board()
    def solve_board(self):
        board = self.Board.solve()
        self.Board = board
        self.draw_board()
    def clear_board(self):
        self.Board.clear()
        self.draw_board()
    def lock_grid(self):
        if self.focus in self.textWidgets:
                k = self.textWidgets.index(self.focus)
                i,j = self.index_to_cart(k)
                active_var = self.Board[i][j]
                active_var.update_lock(not active_var.readOnly)
                if(active_var.readOnly):
                    self.unsatWidgets[k].color = self.HUD.lockedColor
                else:
                    self.unsatWidgets[k].color = self.HUD.defaultColor
                self.HUD.update_domain(self.Board[i][j])
    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.TAB:
            if modifiers & pyglet.window.key.MOD_SHIFT:
                direction = -1
            else:
                direction = 1

            if self.focus in self.textWidgets:
                i = self.textWidgets.index(self.focus)
            else:
                i = 0
                direction = 0

            self.set_focus(self.textWidgets[(i + direction) % len(self.textWidgets)])
        elif symbol == pyglet.window.key.BACKSPACE:
            if self.focus in self.textWidgets:
                k = self.textWidgets.index(self.focus)
                i,j = self.index_to_cart(k)
                self.focus.document.text = ''
                self.Board.reset_var(i,j)
                self.HUD.update_domain(self.Board[i][j])
        elif symbol == pyglet.window.key.CAPSLOCK:
            self.lock_grid()
        elif symbol == pyglet.window.key.ESCAPE:
            pyglet.app.exit()
        elif symbol == pyglet.window.key.UP or symbol == pyglet.window.key.W:
            if self.focus in self.textWidgets:
                k = self.textWidgets.index(self.focus)
                i,j = self.index_to_cart(k)
                self.set_focus(self.textWidgets[((i+1)%9 + j*9)])
        elif symbol == pyglet.window.key.DOWN or symbol == pyglet.window.key.S:
            if self.focus in self.textWidgets:
                k = self.textWidgets.index(self.focus)
                i,j = self.index_to_cart(k)
                self.set_focus(self.textWidgets[(j*9+(i-1)%9)])
        elif symbol == pyglet.window.key.RIGHT or symbol == pyglet.window.key.D:
            if self.focus in self.textWidgets:
                i = self.textWidgets.index(self.focus)
                self.set_focus(self.textWidgets[(i + 9) % len(self.textWidgets)])
        elif symbol == pyglet.window.key.LEFT or symbol == pyglet.window.key.A:
            if self.focus in self.textWidgets:
                i = self.textWidgets.index(self.focus)
                self.set_focus(self.textWidgets[(i - 9) % len(self.textWidgets)])
    def on_draw(self):
        pyglet.gl.glClearColor(1, 1, 1, 1)
        self.clear()
        for batch in self.batches:
            batch.draw()
window = Window()
pyglet.app.run()
