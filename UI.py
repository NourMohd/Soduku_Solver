import pyglet
from pyglet import shapes
from Logic import Board

class TextWidget:
    def __init__(self, i, j,offset, width, batch):
        self.i = i
        self.j = j
        self.x = offset+i*width
        self.y = offset+j*width
        fontSize = int(width*0.5)
        self.document = pyglet.text.document.UnformattedDocument('0')
        self.document.set_style(0, len(self.document.text), dict(color=(0, 0, 0, 255),font_size=fontSize))

        self.layout = pyglet.text.layout.IncrementalTextLayout(self.document, width, width, batch=batch)
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
        pyglet.gl.glClearColor(1,1,1,1)
        super(Window, self).__init__(self.window_size,self.window_size, caption='Soduko', *args, **kwargs)
        self.batches = list()
        self.textWidgets = list()
        self.text_cursor = self.get_system_mouse_cursor('text')
        self.draw_init()
        self.focus = None
        self.incons = list()
    def draw_init(self):
        Gridbatch = pyglet.graphics.Batch()
        Textbatch = pyglet.graphics.Batch()
        HUDBatch =  pyglet.graphics.Batch()
        self.batches.append(Textbatch)
        self.batches.append(Gridbatch)
        self.batches.append(HUDBatch)
        self.lines = list()
        self.labels = list()
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
                self.textWidgets.append(TextWidget( i, j,game_offset, cell_size, Textbatch))
        self.labels.append(pyglet.text.Label('Domain',
                          font_name='Times New Roman',
                          font_size=26,
                          x=self.HUD_offset+(self.HUD_size//2)+10, y=self.window_size,
                          batch=HUDBatch,
                          anchor_x="center",
                          anchor_y="top",
                          color=(0, 0, 0, 0)))
        self.domain = pyglet.text.Label('1\n2\n3',
                          font_name='Times New Roman',
                          font_size=26,
                          x=self.HUD_offset+(self.HUD_size), y=self.window_size - 50,
                          batch=HUDBatch,
                          anchor_x="center",
                          anchor_y="top",
                          color=(0, 0, 0, 0),multiline=True,width=self.HUD_size)
    def handle_incon(self,pos):
        self.incons = pos
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
                self.textWidgets[k].square.color = self.focus.defaultColor
        self.focus = focus
        k = self.textWidgets.index(self.focus)
        i,j = self.index_to_cart(k)
        active_var = self.Board[i][j]
        print(self.Board.get_incons(active_var))
        if self.focus:
            k = self.textWidgets.index(self.focus)
            i,j = self.index_to_cart(k)
            activeVar = self.Board[i][j]
            self.focus.square.color = self.focus.activeColor
            for var in self.Board.arcs[activeVar]:
                i,j = var.i,var.j
                k = i+j*9
                self.textWidgets[k].square.color = self.focus.highlightColor
    def on_mouse_press(self, x, y, button, modifiers):
        for widget in self.textWidgets:
            if widget.hit_test(x, y):
                self.set_focus(widget)
                break
        else:
            self.set_focus(None)

    def on_text(self, text):
        if self.focus:
            if(text.isnumeric() and text !='0'):
                k = self.textWidgets.index(self.focus)
                i,j = self.index_to_cart(k)
                active_var = self.Board[i][j]
                active_var.set_val(int(text))
                self.focus.document.text = text
                print(self.Board.get_incons(active_var))
    def cart_to_index(self,i,j):      
        return i+j*9
    def index_to_cart(self,k):
        j = (k//9)%9
        i = (k-j*9)%9
        return i,j
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
        for pos in self.incons:
            k = self.cart_to_index(pos[0],pos[1])
            self.textWidgets[k].square.color = self.focus.inconColor
        for batch in self.batches:
            batch.draw()
window = Window()
pyglet.app.run()
