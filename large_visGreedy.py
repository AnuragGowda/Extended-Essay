import pygame as pg
from math import hypot
from time import sleep, time

import os, psutil
process = psutil.Process(os.getpid())

'''
A program to visualize how A* pathfinding works

To place the starting node and ending node, left click
To place walls/obstacles, right click
To restart press the r key
To start press the s key
'''

class Wall(pg.sprite.Sprite):

    def __init__(self, pos, game):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.size = game.NODE_SIZE
        self.image = game.BLACK_NODE
        self.rect = self.image.get_rect()
        self.x, self.y = pos
        self.rect.x, self.rect.y = [i*game.NODE_SIZE for i in pos]

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
        self.size = game.NODE_SIZE
        self.image = game.WHITE_NODE
        self.rect = self.image.get_rect()
        self.x, self.y = pos
        self.rect.x, self.rect.y = [i*game.NODE_SIZE for i in pos]
        self.parent = None
        self.start = False
        self.end = False
        self.hCost = None
        self.fCost = None
        self.seen = False
        self.discovered = False
        self.end_node = []
        Node.all_nodes[str(pos)] = self
    
    @classmethod
    def exists(cls, pos):
        return cls.all_nodes[str(pos)] if str(pos) in cls.all_nodes else False
    
    def clicked(self, setup=False):
        if pg.mouse.get_pressed()[0] and self.rect.collidepoint(pg.mouse.get_pos()):
            if Node.click_counter == 0:
                self.set_start()
            elif Node.click_counter == 1:
                self.set_end()
            Node.click_counter+=1
        elif pg.mouse.get_pressed()[2] and self.rect.collidepoint(pg.mouse.get_pos()):
            self.kill_node()

    def kill_node(self):
        Wall([self.x, self.y], self.game)
        Node.all_nodes[f"[{self.x}, {self.y}]"] = None
        self.kill()

    def set_start(self):
        self.image = self.game.START_NODE
        self.start = True
        self.hCost = None
        Node.start_node = self
        sleep(.2)

    def set_end(self):
        self.image = self.game.END_NODE
        self.end = True
        self.hCost = 0
        Node.end_node = self
        Node.start_node.hCost = hypot(Node.start_node.x-self.x, Node.start_node.y-self.y)
        Node.start_node.fCost = Node.start_node.hCost
        sleep(.2)
        
    def scan(self):

        if not self.discovered and not self.start and not (self.end and Node.seen_end):
            return

        if self.end:
            return self.gen_final_path()
            
        # Change color
        if not self.start and not self.end:
            self.image = self.game.RED_NODE
            self.seen = True

        # Generate a list of surrounding nodes to update
        check = []
        for x in range(-1,2):
            for y in range(-1,2):
                check.append([self.x+x, self.y+y])
        
        # Uncomment this to disallow traversing diagonally
        rem_list = [[-1, -1], [-1, 1], [1,1], [1,-1]]                     
        for i in rem_list:
            check.remove([self.x+i[0], self.y+i[1]])

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
            self.image = self.game.GREEN_NODE
            self.discovered = True
        else:
            Node.seen_end = True

        if not self.hCost or self.hCost < parent.hCost:
            self.parent = parent
            self.hCost = hypot(self.x-Node.end_node.x, self.y-Node.end_node.y)
        
        self.fCost = self.hCost


    def gen_final_path(self):

        node_list = []
        parent_node = self.parent

        while not parent_node.start:
            node_list.append(parent_node)
            parent_node = parent_node.parent

        for node in node_list:
            node.image = self.game.BLUE_NODE

        #global g
        #g.running = False


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
        self.map = 'map3'#int(input('Choose map (1-5): ')
        
        self.WIDTH, self.HEIGHT = Game.map_sizes[self.map]['size']
        self.NODE_SIZE = Game.map_sizes[self.map]['recommended_node_size']
                
        self.screen = pg.display.set_mode((self.WIDTH*self.NODE_SIZE, self.HEIGHT*self.NODE_SIZE), pg.NOFRAME)
        self.running = True
        self.clock = pg.time.Clock()
        self.WHITE_NODE = pg.transform.scale(pg.image.load('img\\White.png').convert(), (self.NODE_SIZE, self.NODE_SIZE))
        self.BLACK_NODE = pg.transform.scale(pg.image.load('img\\Black.png').convert(), (self.NODE_SIZE, self.NODE_SIZE))
        self.RED_NODE = pg.transform.scale(pg.image.load('img\\Red.png').convert(), (self.NODE_SIZE, self.NODE_SIZE))
        self.GREEN_NODE = pg.transform.scale(pg.image.load('img\\Green.png').convert(), (self.NODE_SIZE, self.NODE_SIZE))
        self.START_NODE = pg.transform.scale(pg.image.load('img\\Start.png').convert(), (self.NODE_SIZE, self.NODE_SIZE))
        self.END_NODE = pg.transform.scale(pg.image.load('img\\End.png').convert(), (self.NODE_SIZE, self.NODE_SIZE))
        self.BLUE_NODE = pg.transform.scale(pg.image.load('img\\Blue.png').convert(), (self.NODE_SIZE, self.NODE_SIZE))

    def new(self):
        
        # Restart stuff here
        self.setup = True
        self.run_vis = True
        self.all_sprites = pg.sprite.Group()
        for row in range(self.WIDTH):
            for col in range(self.HEIGHT):
                Node([row,col], self)
                
        with open(f'mazes\{self.map}.txt', 'r') as f:
            y=0
            for line in f:
                x=0
                for char in line:
                    if char == '*':
                        Node.all_nodes[f"[{x}, {y}]"].kill_node()
                    elif char == 'a':
                        Node.all_nodes[f"[{x}, {y}]"].set_start()
                    elif char == 'b':
                        end_node_loc = [x, y]
                    x+=1
                y+=1
            Node.all_nodes[str(end_node_loc)].set_end()
            
        start = time()
        self.run()
        print(process.memory_info().rss)
        print(time()-start)

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.events()
            if self.run_vis:
                self.update()
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
                    self.new()
                elif event.key == pg.K_s:
                    self.run_vis = True
                    
    def update(self):
        
        found_nodes = {}
        for node in Node.all_nodes.values():
            if node and node.discovered:
                found_nodes[node.fCost] = node
        if Node.seen_end:
            Node.end_node.scan()
            self.run_vis = False
        elif len(found_nodes) == 0:
            Node.start_node.scan()
        else:      
            found_nodes[min(found_nodes)].scan()
            found_nodes[min(found_nodes)].discovered = False
    
    def draw(self):
        self.all_sprites.draw(self.screen)
        pg.display.flip()

           
g = Game()
g.new()
pg.quit()
