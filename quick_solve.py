import pygame as pg
from math import hypot
from time import time

'''
A program to visualize how A* pathfinding works

To place the starting node and ending node, left click
To place walls/obstacles, right click
To restart press the r key
To start press the s key
'''
class Node:
    all_nodes = {}
    init_counter = 0
    start_node = None
    end_node = None
    seen_end = False

    def __init__(self, pos):
        self.x, self.y = pos
        self.parent = None
        self.start = False
        self.end = False
        self.hCost = None
        self.gCost = None
        self.fCost = None
        self.seen = False
        self.discovered = False
        self.end_node = []
        self.final = False
        Node.all_nodes[str(pos)] = self
    
    @classmethod
    def exists(cls, pos):
        return cls.all_nodes[str(pos)] if str(pos) in cls.all_nodes else False

    def kill_node(self):
        Node.all_nodes[f"[{self.x}, {self.y}]"] = None

    def set_start(self):
        self.start = True
        self.gCost = 0
        self.hCost = None
        Node.start_node = self

    def set_end(self):
        self.end = True
        self.hCost = 0
        Node.end_node = self
        Node.start_node.hCost = hypot(Node.start_node.x-self.x, Node.start_node.y-self.y)
        Node.start_node.fCost = Node.start_node.gCost + Node.start_node.hCost
        
    def scan(self):

        if not self.discovered and not self.start and not (self.end and Node.seen_end):
            return

        if self.end:
            return self.gen_final_path()
            
        # Change color
        if not self.start and not self.end:
            self.seen = True
 

        '''







        I'm going to turn off diagonal movement for this one cause it looks weird on out.txt lol





        Below (this is the edited part)         |
                                               ...
                                                .
        '''
        # Generate a list of surrounding nodes to update
        check = []
        for x in range(-1,2):
            for y in range(-1,2):
                check.append([self.x+x, self.y+y])
        rem_list = [[-1, -1], [-1, 1], [0,0], [1,1], [1,-1]]
        for i in rem_list:
            check.remove([self.x+i[0], self.y+i[1]])
        #check.remove([self.x,self.y])  
        
        # Update them if they exist
        for node_pos in check:
            node = Node.exists(node_pos)
            if node:
                node.update_cost(self)


    def update_cost(self, parent):

        if self.seen or self.start: 
            return

        if not self.end:
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
            node.final = True

        global running
        running = False


start_node = None
end_node = None
running = True
map = 1
max_x = 0
max_y = 0
map_sizes = {
                    1:[401, 201],
                    2:[18, 18],
                } 
def main():

    for row in range(map_sizes[map][0]):
        for col in range(map_sizes[map][1]):
            Node([row,col])

    # Restart stuff here
    with open(f'mazes\\{map}.txt', 'r') as f:
        x=0
        for line in f:
            y=0
            for char in line:
                if char == '*':
                    Node.all_nodes[f"[{x}, {y}]"].kill_node()
                elif char == 'o':
                    Node.all_nodes[f"[{x}, {y}]"].set_start()
                elif char == 'e':
                    end_node_loc = [x, y]
                y+=1
                global max_y
                max_y = max(max_y, y)
            x+=1
            global max_x
            max_x = max(max_x, x)
        Node.all_nodes[str(end_node_loc)].set_end()
                
def update():
    
    found_nodes = {}
    for node in Node.all_nodes.values():
        if node and node.discovered:
            found_nodes[node.fCost] = node
    if Node.seen_end:
        Node.end_node.scan()
    elif len(found_nodes) == 0:
        Node.start_node.scan()
    else:      
        found_nodes[min(found_nodes)].scan()
        found_nodes[min(found_nodes)].discovered = False

def show():
    s = ''
    with open('out.txt', 'w') as f:
        for x in range(max_x):
            for y in range(max_y):
                if Node.exists([x,y]) and Node.all_nodes[f"[{x}, {y}]"].final:
                    s+='.'
                elif Node.exists([x,y]) and Node.all_nodes[f"[{x}, {y}]"].start:
                    s+='A'
                elif Node.exists([x,y]) and Node.all_nodes[f"[{x}, {y}]"].end:
                    s+='B'
                else:
                    s+='#'
            s+='\n'
        f.write(s)


start = time() 
main()
while running:
    update()
show()
print('Solved in: ' + str(round(time()-start,3)) + ' seconds')