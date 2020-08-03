import pygame as pg
from math import hypot
from time import sleep 

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
        self.image = pg.image.load('img\\Start.png').convert()
        self.start = True
        self.gCost = 0
        self.hCost = None
        Node.start_node = self
        sleep(.2)

    def set_end(self):
        self.image = pg.image.load('img\\End.png').convert()
        self.end = True
        self.hCost = 0
        Node.end_node = self
        Node.start_node.hCost = hypot(Node.start_node.x-self.x, Node.start_node.y-self.y)
        Node.start_node.fCost = Node.start_node.gCost + Node.start_node.hCost
        sleep(.2)
        
    def scan(self):

        if not self.discovered and not self.start and not (self.end and Node.seen_end):
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

    def __init__(self):
        pg.init()
        self.WIDTH = int(input('W: '))
        self.HEIGHT = int(input('H: '))
        self.SPEED = int(input('Speed (1-10): '))
        self.disp_costs = False#True if input('Show costs(y/n)?').lower() == 'y' else False
        self.screen = pg.display.set_mode((self.WIDTH*32, self.HEIGHT*32))
        self.running = True
        self.clock = pg.time.Clock()

    def new(self):
        
        # Restart stuff here
        self.setup = True
        self.run_vis = False
        self.all_sprites = pg.sprite.Group()
        for row in range(self.WIDTH):
            for col in range(self.HEIGHT):
                Node([row,col], self)

        self.run()

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
                    
        for node in Node.all_nodes.values():
            if node:
                node.clicked()  
                    
    def update(self):
        
        found_nodes = {}
        for node in Node.all_nodes.values():
            if node and node.discovered:
                found_nodes[node.fCost] = node
        if len(found_nodes) == 0:
            Node.start_node.scan()
        elif Node.seen_end:
            Node.end_node.scan()
            self.run_vis = False
        else:      
            found_nodes[min(found_nodes)].scan()
            found_nodes[min(found_nodes)].discovered = False
        sleep(1-self.SPEED/10)
    
    def draw(self):
        self.all_sprites.draw(self.screen)
        for node in Node.all_nodes.values():
            if node and (node.discovered or node.seen):
                if self.disp_costs:
                    self.draw_text(str(int(node.gCost*10)), 15, (0, 0, 0), node.rect.x+7, node.rect.y+5)
                    self.draw_text(str(int(node.hCost*10)), 15, (0, 0, 0), node.rect.x+node.size-7, node.rect.y+5)
                    self.draw_text(str(int(node.fCost*10)), 20, (0, 0, 0), node.rect.x+node.size/2, node.rect.y+node.size/2) 
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
