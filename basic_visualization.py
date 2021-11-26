import pygame as pg
from math import hypot
import time

'''
A program to visualize how A* pathfinding works
You want to click on the block with the smallest number
until you eventually reach the end block

To place the starting node and ending node, left click
To place walls/obstacles, right click
To restart press the r key
'''

class Wall(pg.sprite.Sprite):

    def __init__(self, pos, game):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.size = 32
        self.image = pg.image.load('img\\Black.png').convert()
        self.rect = self.image.get_rect()
        self.x, self.y = pos
        self.rect.x, self.rect.y = [i*32 for i in pos]

class Node(pg.sprite.Sprite):
    all_nodes = {}
    init_counter = 0
    start_node = None
    end_node = None
    seen_end = False

    def __init__(self, pos, game):
        self.game = game
        self.groups = self.game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.size = 32
        self.image = pg.image.load('img\\White.png').convert()
        self.rect = self.image.get_rect()
        self.x, self.y = pos
        self.rect.x, self.rect.y = [i*32 for i in pos]
        self.parent = None
        self.start = False
        self.end = False
        self.hCost = None
        self.gCost = None
        self.fCost = None
        self.seen = False
        self.discovered = False
        self.end_node = []
        Node.all_nodes[str(pos)] = self
    
    @classmethod
    def exists(cls, pos):
        return cls.all_nodes[str(pos)] if str(pos) in cls.all_nodes else False
    
    def clicked(self, setup=False):
        if pg.mouse.get_pressed()[0] and \
           self.rect.collidepoint(pg.mouse.get_pos()):
            if Node.click_counter == 0:
                self.set_start()
            elif Node.click_counter == 1:
                self.set_end()
            else:
                self.scan()
            Node.click_counter+=1
        elif pg.mouse.get_pressed()[2] and \
             self.rect.collidepoint(pg.mouse.get_pos()):
            self.kill_node()

    def kill_node(self):
        Wall([self.x, self.y], self.game)
        Node.all_nodes[f"[{self.x}, {self.y}]"] = None
        self.kill()

    def set_start(self):
        self.image = pg.image.load('img\\Start.png').convert()
        self.start = True
        self.gCost = 0
        self.hCost = None
        Node.start_node = self
        time.sleep(.2)

    def set_end(self):
        self.image = pg.image.load('img\\End.png').convert()
        self.end = True
        self.hCost = 0
        Node.end_node = self
        Node.start_node.hCost = hypot(Node.start_node.x-self.x, \
                                      Node.start_node.y-self.y)
        Node.start_node.fCost = Node.start_node.gCost + Node.start_node.hCost
        time.sleep(.2)
        
    def scan(self):

        if not self.discovered and not self.start and not\
           (self.end and Node.seen_end):
            return

        if self.end:
            return self.gen_final_path()
            
        # Change color
        if not self.start and not self.end:
            self.image = pg.image.load('img\\Red.png').convert()
            self.seen = True

        # Generate a list of surrounding nodes to update
        check = []
        for x in range(-1,2):
            for y in range(-1,2):
                check.append([self.x+x, self.y+y])
        check.remove([self.x,self.y])  

        # Update them if they exist
        for node_pos in check:
            node = Node.exists(node_pos)
            if node:
                node.update_cost(self)


    def update_cost(self, parent):

        if self.seen or self.start: 
            return

        if not self.end:
            self.image = pg.image.load('img\\Green.png').convert()
            self.discovered = True
        else:
            Node.seen_end = True

        dist = hypot(self.x-parent.x, self.y-parent.y)
        if not self.gCost or self.gCost > parent.gCost + dist:
            self.parent = parent
            self.gCost = self.parent.gCost + dist

        if not self.hCost:
            self.hCost = hypot(self.x-Node.end_node.x, self.y-Node.end_node.y)
        
        self.fCost = self.gCost + self.hCost


    def gen_final_path(self):

        node_list = []
        parent_node = self.parent

        while not parent_node.start:
            node_list.append(parent_node)
            parent_node = parent_node.parent

        for node in node_list:
            node.image = pg.image.load('img\\Blue.png').convert()


class Game:
    start_node = None
    end_node = None
    running = True
    map_sizes = {
                    'map1':{
                        'size': [401, 201],
                        'recommended_node_size': 4,
                        },
                    'map2':{
                        'size':[100,50],
                        'recommended_node_size': 4,
                        },
                    'map3':{
                        'size':[235,53],
                        'recommended_node_size': 4,
                        },
                    2:{
                        'size': [18, 18],
                        'recommended_node_size': 10,
                        },
                    'example':{
                        'size': [10, 5],
                        'recommended_node_size': 10,
                    },
                    'inefficiencyExample':{
                        'size': [20,20],
                        'recommended_node_size': 10,
                    }
                }

    def __init__(self):
        pg.init()
        self.WIDTH = int(input('W: '))
        self.HEIGHT = int(input('H: '))

        # Uncomment the 3 following lines for map generation
        #self.map = 3
        
        #self.WIDTH, self.HEIGHT = Game.map_sizes[self.map]['size']
        self.NODE_SIZE = 10#Game.map_sizes[self.map]['recommended_node_size']

        # You don't need this line for Greedy
        self.disp_costs = True if input('Show g and h costs(y/n)?').lower() == \
                          'y' else False
        self.screen = pg.display.set_mode((self.WIDTH*32, self.HEIGHT*32),\
                                          pg.NOFRAME)
        self.running = True
        self.clock = pg.time.Clock()

    def new(self):
        
        # Restart stuff here
        self.setup = True
        self.all_sprites = pg.sprite.Group()
        for row in range(self.WIDTH):
            for col in range(self.HEIGHT):
                Node([row,col], self)

        # Uncomment for map generation
        '''
        with open(f'mazes\{self.map}.txt', 'r') as f:
            x=0
            for line in f:
                y=0
                for char in line:
                    if char == '*':
                        Node.all_nodes[f"[{y}, {x}]"].kill_node()
                    elif char == 'a':
                        Node.all_nodes[f"[{y}, {x}]"].set_start()
                    elif char == 'b':
                        end_node_loc = [y, y]
                    y+=1
                x+=1
            Node.all_nodes[str(end_node_loc)].set_end()
        '''
        
        self.run()

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.events()
            self.draw()

    def events(self):

        if self.setup:
            Node.click_counter = 0
            self.setup = False
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                key = pg.key.get_pressed()
                if event.key == pg.K_r:
                    g.new()
            
        for node in Node.all_nodes.values():
            if node:
                node.clicked()  
    
    def draw(self):
        self.all_sprites.draw(self.screen)
        for node in Node.all_nodes.values():
            if node and node.discovered:
                # !DELETE all 3 lines below for Greedy 
                if self.disp_costs:
                    self.draw_text(str(int(node.gCost*10)), \
                                   15, (0, 0, 0), node.rect.x+7, node.rect.y+5)
                    self.draw_text(str(int(node.hCost*10)), \
                                   15, (0, 0, 0), node.rect.x+node.size-7, \
                                   node.rect.y+5)
                self.draw_text(str(int(node.fCost*10)), \
                               20, (0, 0, 0), node.rect.x+node.size/2, \
                               node.rect.y+node.size/2) 
        pg.display.flip()

    def draw_text(self, text, size, color , x, y, font_name = ''):
        font = pg.font.Font(pg.font.match_font(font_name), size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)
            
g = Game()
g.new()
pg.quit()
