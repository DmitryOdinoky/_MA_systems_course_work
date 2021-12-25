import cherrypy
from cherrypy.process.plugins import Monitor
import os
import random
import simplejson
import sys
import numpy as np

MEDIA_DIR = os.path.join(os.path.abspath("."), u"media")
LOG_DIR = os.path.join(os.path.abspath("."), u"logs")

config = {'/media':
                {'tools.staticdir.on': True,
                 'tools.staticdir.dir': MEDIA_DIR,
                 'tools.encode.text_only': False
                }
        }
    
    


class ControlCenter:
    
    def __init__(self, report_idx=[], report_sensored_prey = [], report_sensored_hunter = [],
                 report_dist_to_hunt = [], report_list_of_mins_prey = []):
        
        self.report_idx = report_idx
        self.report_sensored_prey = report_sensored_prey
        self.report_sensored_hunter = report_sensored_hunter
        self.report_dist_to_hunt = report_dist_to_hunt
        self.report_list_of_mins_prey = report_list_of_mins_prey
        


class Cell:
    def __init__(self, nr=0, table_size=0, already_filled=[]):
        
        self.state = 0
        
        self.nr = nr
        self.x = int(random.uniform(0, table_size) - 1)
        self.y = int(random.uniform(0, table_size) - 1)
        while (self.x, self.y) in already_filled:
            self.x = int(random.uniform(0, table_size))
            self.y = int(random.uniform(0, table_size))

    def move(self, pos):
        if pos:
            self.x, self.y = pos

    def __repr__(self):
        return '<td></td>'


class Hunter(Cell):


    
    def __repr__(self):
        
        return '<td style="background:#36679C">%d</td>' % self.nr
        # return '%dx%d' % (self.x, self.y)

    

class Prey(Cell):
    def __repr__(self):
        return '<td style="background:#B50724">%d</td>' % self.nr
        # return '%dx%d' % (self.x, self.y)


class World(object):
    # '''Constants'''
    N = 25
    N_HUNT = 12
    N_PREY = 5
    RESPAWN_TIME = 5  # iterations
    
    


    def __init__(self):
        super(World, self).__init__()
        self.hunters = []
        self.prey = []
        already_filled = []

        self.iteration_round = 0

        # Used to respawn dead prey
        self.prey_idx = World.N_PREY - 1
        self.respawn_countdowns = []

        print("Spawn", World.N_HUNT, 'hunters')
        print("Spawn", World.N_PREY, 'prey')

        for i in range(World.N_HUNT):
            self.hunters.append(Hunter(i, World.N, already_filled))
            already_filled.append((self.hunters[-1].x, self.hunters[-1].y))

        for i in range(World.N_PREY):
            self.prey.append(Prey(i, World.N, already_filled))
            already_filled.append((self.prey[-1].x, self.prey[-1].y))
            
        self.controlCenter = ControlCenter()

    def reinit(self):
        self.__init__()

    def compile_representation(self):
        # '''Produces a representation of the world as HTML table'''
        table = [[Cell() for k in range(World.N)] for k in range(World.N)]

        for i in self.hunters:
            table[i.x][i.y] = i
        for i in self.prey:
            table[i.x][i.y] = i

        return ''.join(['<tr>'+str(
                    ''.join([str(cell) for cell in row])
                )+'</tr>\n' for row in table])

    def adjacent_cell(self, x, y, direction):
        # '''Returns the adjacent cell from position `(x, y)` in the direction
        #    `direction` if this cell is empty and withhin the map, `None` else.
        #    Direction direction is represented as int, as follows:
        #     0 -> Up
        #     1 -> Right
        #     2 -> Down
        #     3 -> Left
        # '''
        # Up
        if direction == 0:
            new_x = x - 1
            if new_x < 0:
                return None
            else:
                return (new_x, y)
        # Right
        elif direction == 1:
            new_y = y + 1
            if new_y >= World.N:
                return None
            else:
                return (x, new_y)
        # Down
        elif direction == 2:
            new_x = x + 1
            if new_x >= World.N:
                return None
            else:
                return (new_x, y)
        # Left
        elif direction == 3:
            new_y = y - 1
            if new_y < 0:
                return None
            else:
                return (x, new_y)

    def empty_cell(self, pos):
        # '''Checks if the cell is empty'''
        if not pos:
            return False
        for i in self.hunters:
            if (i.x, i.y) == pos:
                return False
        for i in self.prey:
            if (i.x, i.y) == pos:
                return False
        return True

    def prey_trapped(self, p):
        # '''Checks if the prey p is trapped between hunters (or walls)'''
        neighs = [self.adjacent_cell(p.x, p.y, 0),
                    self.adjacent_cell(p.x, p.y, 1),
                    self.adjacent_cell(p.x, p.y, 2),
                    self.adjacent_cell(p.x, p.y, 3)]
        neighs = [x for x in neighs if x]

        for i in self.hunters:
            if (i.x, i.y) in neighs:
                neighs.remove((i.x, i.y))

        if not neighs:
            return True
        return False

    def distance(self, a, b):
        # '''Computes Manhattan distance between 2 cells'''
        
        distance = abs(a.x - b.x) + abs(a.y - b.y)
        
        
        return distance
    
    def use_sensors(self, h):
        
        perception_hunters = [0, 0, 0, 0] # 
        perception_prey = [0, 0, 0, 0] # 
        

        
        # Distance to hunters, within treshold
        
        
        list_of_distances = []
        list_of_mins_prey = []

        
        for j in self.hunters:
            
            
            
    
            # dist_to_hunt = self.distance(h, j)
            # if dist_to_hunt == None or dist_to_hunt == []: dist_to_hunt = 0
            # list_of_distances.append(dist_to_hunt)
            
           
            # dist_list.append(dist_to_hunt)
            
            # if h==j:
            #     continue
            
            
            
            dist = self.distance(h, j)
   
            
            
            if dist <= 12.0 and dist > 0:     
                dist = dist
            else: dist = np.NaN
            
            
            if dist != np.NaN:            
                
                dist = float(dist) + 1

            # Vertical
                if j.x < h.x:
                    perception_hunters[0] += dist
                elif j.x > h.x:
                    perception_hunters[2] += dist
                # Horizontal
                if j.y < h.y:
                    perception_hunters[3] += dist
                elif j.y > h.y:
                    perception_hunters[1] += dist
                    
            

            
            # perception_hunters[4] = 0
            
            # perception_hunters[5] = j.state
            
            list_of_distances.append(dist)
            
            # distances_to_hunt = dist_list
            

        
        
                    
        for j in self.prey:
            
            
            dist = self.distance(h, j)
            
            if dist <= 12.0 and dist > 0:     
                dist = dist
            else: dist = np.NaN
            
            
            if dist != np.NaN:            
                
                dist = float(dist) + 1

            # Vertical
                if j.x < h.x:
                    perception_prey[0] += dist
                elif j.x > h.x:
                    perception_prey[2] += dist
                # Horizontal
                if j.y < h.y:
                    perception_prey[3] += dist
                elif j.y > h.y:
                    perception_prey[1] += dist
                    
            
            
            
            # perception_prey[4] = 0
            
            # perception_prey[5] = j.state
  
        perception_hunters = np.array(perception_hunters)
        perception_prey = np.array(perception_prey)
        distances_to_hunt = np.array(list_of_distances)
        list_of_mins_prey = np.nanmin(perception_prey)        
            
        return perception_hunters, perception_prey, distances_to_hunt, list_of_mins_prey

    def score_directions(self, h):
        scores = [0, 0, 0, 0]
        # Weak rejection force from other hunters
        for j in self.hunters:
            
            if h==j:
                continue
            
            dist = self.distance(h, j)
            
            if dist <= 12.0:
                dist = dist
            else: dist = None
            
            
            if dist != None:            
                
                dist = float(dist) + 1
            

            # Vertical
                if j.x < h.x:
                    scores[2] += 1 / (dist ** 2)
                elif j.x > h.x:
                    scores[0] += 1 / (dist ** 2)
                # Horizontal
                if j.y < h.y:
                    scores[1] += 1 / (dist ** 2)
                elif j.y > h.y:
                    scores[3] += 1 / (dist ** 2)
                    
                
        
        # print(dist)
        
        # Strong attraction force from prey
        for j in self.prey:
            
            
            
            dist = self.distance(h, j)
            
            
            if dist <= 12.0:     
                dist = dist
            else: dist = None
            
            
            
            if dist != None:
                dist = float(dist) + 1
            # Vertical
                if j.x < h.x:
                    scores[0] += 10 / (dist ** 2)
                elif j.x > h.x:
                    scores[2] += 10 / (dist ** 2)
                # Horizontal
                if j.y < h.y:
                    scores[3] += 10 / (dist ** 2)
                elif j.y > h.y:
                    scores[1] += 10 / (dist ** 2)
                        
        return scores


    def respawn_prey(self):
        already_filled = [(k.x, k.y) for k in self.prey+self.hunters]
        self.prey_idx += 1
        self.prey.append(Prey(self.prey_idx, World.N, already_filled))

    def __repr__(self):
        return self.compile_representation()

    def __str__(self):
        return self.__repr__()


world = World()


def iterate():
    print("ITERATION:", world.iteration_round)
    # print(LOG_DIR)
    # sys.exit()
    
    # print("ITERATION:", world.controlCenter.reports[-1])

    # Check if prey dies
    for i in world.prey:
        if world.prey_trapped(i):
            world.prey.remove(i)
            world.respawn_countdowns.append(World.RESPAWN_TIME)
            
        
    prey_list = []
    # Prey movement
    for i in world.prey:
        alternatives = [world.adjacent_cell(i.x, i.y, d) for d in range(4)]
        alternatives = [a for a in alternatives if a and world.empty_cell(a)]
        prey_list.append(alternatives)

        if not alternatives:
            # Stay
            continue

        new_pos = random.choice(alternatives)
        i.move(new_pos)
    
    

    
    # Hunters movement
    world.controlCenter.report_sensored_prey = []
    world.controlCenter.report_sensored_hunter = []
    world.controlCenter.report_dist_to_hunt = []
    world.controlCenter.report_list_of_mins_prey = []
    
    for i in world.hunters:
        
        # world.controlCenter.report_idx.append(world.iteration_round)
        # print(i.nr)
        
        # sys.exit()
        
        moves = True
        scores = world.score_directions(i)
        perc_hunters, perc_prey, distances_to_hunt, list_of_mins_prey = world.use_sensors(i)
        
        # print(type(distances_to_hunt))
        # np.savetxt(LOG_DIR + '/' +  f'iter_{world.iteration_round}.csv',  perc_hunters, fmt='%10.1f', delimiter=",")
        
        # sys.exit()
        # print(perc)
        
        
        world.controlCenter.report_sensored_prey.append(np.array(perc_prey))
        world.controlCenter.report_sensored_hunter.append(np.array(perc_hunters))
        # print(np.shape(distances_to_hunt))
        world.controlCenter.report_dist_to_hunt.append(np.array(distances_to_hunt))
        world.controlCenter.report_list_of_mins_prey.append(np.array(list_of_mins_prey))
        # world.controlCenter.report_dist_to_hunt = world.controlCenter.report_dist_to_hunt
           
        
        direction = scores.index(max(scores))
        new_pos = world.adjacent_cell(i.x, i.y, direction)
        while (not new_pos or not world.empty_cell(new_pos)) and sum(scores) != 0:
            # If the best direction is blocked, just keep current position
            if not world.empty_cell(new_pos):
                moves = False
                break
            # Take the next biggest
            scores[direction] = 0
            direction = scores.index(max(scores))
            new_pos = world.adjacent_cell(i.x, i.y, direction)
        if moves and sum(scores) != 0:
            # Not completly blocked
            i.move(new_pos)
            
        # print(np.expand_dims(distances_to_hunt, axis = 1))
        # print(np.shape(distances_to_hunt)) 
            
    out_prey = np.array(world.controlCenter.report_sensored_prey)       
    out_hunter = np.array(world.controlCenter.report_sensored_hunter) 
    out_dist_to_hunt = np.array(world.controlCenter.report_dist_to_hunt)
    
    out_list_of_mins_prey = np.array(world.controlCenter.report_list_of_mins_prey)
    out_list_of_mins_prey[out_list_of_mins_prey == 0.0] = np.NaN
    
    # print(np.min(out_dist_to_hunt))
    
    # print(out_dist_to_hunt)
    # print(np.shape(np.squeeze(world.controlCenter.report_dist_to_hunt))) 
    
    np.savetxt(LOG_DIR + '/' +  f'last_iter_prey.csv', out_prey, fmt='%10.1f', delimiter=",")
    np.savetxt(LOG_DIR + '/' +  f'last_iter_hunter.csv', out_hunter, fmt='%10.1f', delimiter=",")
    np.savetxt(LOG_DIR + '/' +  f'last_iter_dist_to_hunt.csv', out_dist_to_hunt, fmt='%10.1f', delimiter=",")
    np.savetxt(LOG_DIR + '/' +  f'last_iter_out_list_of_mins_prey.csv', out_list_of_mins_prey, fmt='%10.1f', delimiter=",")
    
    
    
    # Rounds count
    world.iteration_round += 1
    # Handle respawning
    for i in range(len(world.respawn_countdowns)):
        world.respawn_countdowns[i] -= 1
        if world.respawn_countdowns[i] <= 0:
            world.respawn_prey()
    world.respawn_countdowns = [a for a in world.respawn_countdowns if a > 0]


class HuntingGameApp(object):
    @cherrypy.expose
    def index(self):
        return open(os.path.join(MEDIA_DIR, u'index.html'))

    @cherrypy.expose
    def update(self):
        prey_list = [[a.nr, a.x, a.y] for a in world.prey]
        hunt_list = [[a.nr, a.x, a.y] for a in world.hunters]
        table = [prey_list, hunt_list]
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return simplejson.dumps(dict(repr=table)).encode("utf-8")

    @cherrypy.expose
    def set(self, hunters, prey):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        if not hunters and not prey:
            return simplejson.dumps(dict(success='Fill both fields')).encode("utf-8")

        if hunters.isdigit() and prey.isdigit():
            if int(hunters) + int(prey) > World.N**2:
                return simplejson.dumps(dict(success='Too many')).encode("utf-8")
            World.N_HUNT = int(hunters)
            World.N_PREY = int(prey)
            world.reinit()
        else:
            return simplejson.dumps(dict(success='Invalid input'))
        return simplejson.dumps(dict(success='Done')).encode("utf-8")


Monitor(cherrypy.engine, iterate, frequency=1).subscribe()

# Hack for Heroku
from cherrypy.process import servers
def fake_wait_for_occupied_port(host, port): return
servers.wait_for_occupied_port = fake_wait_for_occupied_port
# ---------------

cherrypy.config.update({'server.socket_host': '0.0.0.0',})
cherrypy.config.update({'server.socket_port': int(os.environ.get('PORT', '4040')),})
cherrypy.tree.mount(HuntingGameApp(), '/', config=config)
cherrypy.engine.start()