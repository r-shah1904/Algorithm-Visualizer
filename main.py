import pygame
import math 
from queue import PriorityQueue

# Setting display 
WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Visualizer")

# Setting up the colour codes
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
WHITE = (255,255,255)
BLACK = (0,0,0)
PURPLE = (128,0,128)
ORANGE = (255,165,0)
GREY = (128,128,128)
TURQUOISE = (64, 224, 208)

class Spot:
    # Setting up the properties of the grid nodes
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row*width
        self.y = col*width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    #gives the position of the node
    def get_pos(self):
        return self.row, self.col
    
    # Methof to determine if a node is visited (logic: if it is red then it is visited)
    def is_closed(self):
        return self.color == RED
    
    def is_open(self):
        return self.color == GREEN
    
    def is_barrier(self):
        return self.color == BLACK
    
    def is_start(self):
        return self.color == ORANGE
    
    def is_end(self):
        return self.color == TURQUOISE
    
    def reset(self):
        self.color = WHITE

    # Method to change the color upon interaction
    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color,(self.x, self.y, self.width, self.width))

    def update_negihbors(self, grid):
        self.neighbors = []
        # Checking the row that we are at is less than total row - 1 so that we can determine if we can move down
        # DOWN
        if self.row < self.total_rows - 1 and not grid[self.row+1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        #UP 
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        #RIGHT
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        #LEFT
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

    # __lt__ represents less than which compares the self node and some other node
    def __lt__(self, other):
        return False

def h(p1, p2): # for the h score using the Mahatan Distance **
    x1,y1  = p1
    x2,y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

def algorithm(draw, grid, start, end):
    count = 0 # keeps track of when we put it
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {} # Parent tracking
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos()) # Hueristic distance from the start to the end so that we can make an estimate of the distance between the start and end node
    
    open_set_hash = {start} # we make this beacuse the priority queue cannot tell us if there is something in the queue or not 

    while not open_set.empty():
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: # to quit during simulation
                pygame.quit()
            
        current = open_set.get()[2] # as we only want the node from the open set
        # if two nodes have the same f score then we look at the count and anything that was inserted first that is what we take
        # we are going to loop through all the items in the open set and pickup the ones with the smallest f score

        open_set_hash.remove(current) 

        if current == end: # if we end up at the end node
            reconstruct_path(came_from, end, draw)
            start.make_start()
            end.make_end()
            return True
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1 
                    open_set.put((f_score, count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open() # as we have put it in open set
        draw()
        if current != start:
            current.make_closed()

    return False

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows) # creating a new node
            grid[i].append(spot) # appends the node in th ith row
    return grid

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0,i*gap), (width, i*gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j*gap,0), (j*gap, width))

def draw(win, grid, rows, width):
    win.fill(WHITE) # fills the entire screen with one colour
    for row in grid:
        for spot in row:
            spot.draw(win)
            
    draw_grid(win, rows, width)
    pygame.display.update()

def get_click_pos(pos, rows, width):
    gap = width // rows
    y, x = pos
    row = y // gap
    col = x // gap
    return row, col

def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)
    start = None
    end = None

    run = True
    started = False

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if started: # to prevent the user from pressing anything else when the algo is running
                continue
            if pygame.mouse.get_pressed()[0]: #left mouse btn pressed
                pos = pygame.mouse.get_pos()
                row, col = get_click_pos(pos, ROWS, width)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()
                elif not end and spot != start:
                    end = spot
                    end.make_end()
                elif spot != end and spot != start:
                    spot.make_barrier()
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_click_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                if spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_negihbors(grid)
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)
    pygame.quit()

main(WIN, WIDTH)

        
