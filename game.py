"""
Copyright (C) 2013 Charlie Li 
Student at Carleton University

Everyone is permitted to copy and distribute verbatim copies
of this license document.
"""
from __future__ import division
import math
import sys
import os
import pygame
import time
import random
import operator

def load_sound(filename):
    """Load a sound with the given filename from the sounds directory"""
    return pygame.mixer.Sound(os.path.join('sounds', filename))

def draw_centered(surface1, surface2, position):
    """Draw surface1 onto surface2 with center at position"""
    rect = surface1.get_rect()
    rect = rect.move(position[0]-rect.width//2, position[1]-rect.height//2)
    surface2.blit(surface1, rect)

def blit_centered(surface1, surface2):
    """Blit surface2, centered, onto surface1"""
    rect = surface2.get_rect()
    rect = rect.move((surface1.get_width()-rect.width)//2,
                     (surface1.get_height()-rect.height)//2)
    surface1.blit(surface2, rect)

def load_font(filename,size):
    """Loads the necessary fonts for me"""
    return pygame.font.Font(os.path.join('fonts', filename), size)

def distance(a, b):
    """Return the distance between two points a and b"""
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def random_image():
    """Selects a random image to display as number"""
    image = random.choice(['paper1.png','paper2.png','paper3.png','paper4.png'])
    return image

def renderfont(string,font,aa,color):
    """Will render a font for myself"""
    return font.render(string,aa,color)

def power_set(a):
    """Compute the set of all subsets of a (set = list here)"""
    if len(a) == 0: return [ [] ]
    ss = power_set(a[1:])
    ss_with_a0 = [ [a[0]] + x for x in ss ]
    return ss + ss_with_a0    

def subset_sum(a, t):
    """Finds all subsets that can be the sum of t"""
    return [ x for x in power_set(a) if sum(x) == t ]

def remove_from_list(a,b):
    """Remove elemnts of one list out of other (sums that have been completed)"""
    for i in a:
        if i in b:
            b.remove(i)
    return b     

def load_image(filename):
    """Load an image with the given filename from the images directory"""
    image = pygame.image.load(os.path.join('images', filename))
    image_rect = image.get_rect()
    return image,image_rect

def load_image_convert(filename,alpha):
    """Load an image with the given filename from the images directory and converts it"""
    image = pygame.image.load(os.path.join('images', filename))
    if alpha:
        return image.convert_alpha()
    else:
        return image.convert(),image.get_rect()

class Paper(object):
    """Paper object that display a number on them"""
    def __init__(self,number,position,font,image,colour,grid_position):
        self.t_f = False
        self.remove = False
        self.kill = False
        self.grid_position = grid_position
        self.number = number
        self.colour = colour
        self.position = position
        self.font = font
        self.numbersurface = renderfont(str(self.number),self.font,True,self.colour)
        self.image,self.image_rect = load_image(image)
        self.image = self.image.convert_alpha()
        self.filename = image
        self.opacity = 0
        blit_centered(self.image, self.numbersurface)

    def display_paper(self,target):
        """Displays or removes the paper images with magic involved, inspired by
        http://www.nerdparadise.com/tech/python/pygame/blitopacity/"""
        if self.remove:
            if self.opacity > 0:
                self.opacity -= 17
            x = self.position[0]
            y = self.position[1]
            temp = pygame.Surface((self.image.get_width(), self.image.get_height())).convert()
            temp.blit(target, (-x, -y))
            temp.blit(self.image, (0, 0))
            temp.set_alpha(self.opacity)        
            target.blit(temp, self.position)
            if self.opacity == 0:
                self.kill = True
        else:
            if self.opacity < 256:
                self.opacity += 17
            x = self.position[0]
            y = self.position[1]
            temp = pygame.Surface((self.image.get_width(), self.image.get_height())).convert()
            temp.blit(target, (-x, -y))
            temp.blit(self.image, (0, 0))
            temp.set_alpha(self.opacity)        
            target.blit(temp, self.position)

    def clicked(self):
        """Checks if the image selected in clicked or not"""
        self.t_f = not self.t_f
        if self.t_f:
            self.image = load_image_convert('c'+self.filename,True)
        else:
            self.image = load_image_convert(self.filename,True)
        blit_centered(self.image, self.numbersurface)
        return self.t_f

class HighScores(object):
    """An object to set HighScores"""
    def __init__(self,score,name):
        self.score = score
        self.name = name
        self.highscores = {}
        self.isBest = False
        
    def readhighscore(self):
        """Reads the highscore into dictionary and take the key with the highest value"""
        with open("highscores.txt","a+") as scores:
            for line in scores:
                key,value = line.split()
                if int(value) > self.highscores.get(key, -1):
                    self.highscores[key] = int(value)
        return self.highscores

    def writehighscores(self):
        """Writes to the highscore file"""
        format = "%s %d\n" % (self.name,self.score)
        f = open('highscores.txt','a')
        f.write(format)
    
    def checkbest(self):
        """Checks if the associated name has a higher score"""
        if self.score > max(self.readhighscore().iteritems(),key=operator.itemgetter(1))[1]:
            return True
        else:
            return False

class Game(object):
    """The thing-a-ma-jiggy that makes this game work"""
    START_SCREEN, PLAYING, ENDROUND,INSTRUCTION,SELECT_LEVEL,HIGHSCORE = range(6)
    
    BLUE = (74,169,242)
    BLACK = (49,79,79)
    GREEN = (63,213,78)
    RED = (192,57,57)
    WHITE = (255,254,249)
    ORANGE = (255,128,0)
    COLOUR_ARRAY = [RED,BLUE,GREEN,BLACK]
    FIELD_COLOUR_ARRAY = [RED,BLUE,GREEN]

    def __init__(self):
        """Initialize a new game"""
        pygame.mixer.init()
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()
        
        #Below we start the game off by the most basic settings
        self.state = Game.START_SCREEN
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Charliesum Additionmania')

        #Below is where I loaded the images needed for the game
        self.bg_front,self.bg_front_rect = load_image_convert('front.jpg',False)
        self.bg_game,self.bg_game_rect= load_image_convert('game.jpg',False)
        self.bg_end,self.bg_end_rect= load_image_convert('end.jpg',False)
        self.bg_dif,self.bg_dif_rect= load_image_convert('diffscreen.jpg',False)
        self.bg_score,self.bg_score_rect= load_image_convert('scorescreen.jpg',False)
        self.bg_instruct,self.bg_instruct_rect = load_image_convert('instruc.jpg',False)
        self.png_sign,self.png_sign_rect = load_image('sign.png')
        self.png_light,self.png_light_rect= load_image('light_sm.png')
        self.png_sign = self.png_sign.convert_alpha()
        self.png_light = self.png_light.convert_alpha()

        #Beblow is the Button images
        self.btnPlay = load_image_convert('pbutton.png',True)
        self.btnPlayo = load_image_convert('pbutton_orange.png',True)
        self.btnEasy = load_image_convert('btneasy.png',True)
        self.btnEasy_hover = load_image_convert('btneasyhover.png',True)
        self.btnNormal = load_image_convert('btnnormal.png',True)
        self.btnNormal_hover = load_image_convert('btnnormalhover.png',True)
        self.btnHard = load_image_convert('btnhard.png',True)
        self.btnHard_hover = load_image_convert('btnhardhover.png',True)
        self.btnScore = load_image_convert('btnhighs.png',True)
        self.btnScoreHover = load_image_convert('btnhighshover.png',True)
        self.btnBack = load_image_convert('btnback.png',True)
        self.btnBackHover = load_image_convert('btnbackhover.png',True)
        self.btnTime = load_image_convert('timeatk.png',True)
        self.btnTimeHover = load_image_convert('timeatkhover.png',True)
        self.btnIntro = load_image_convert('btnintro.png',True)
        self.btnIntroHover = load_image_convert('btnintrohover.png',True)
        self.btnS_on = load_image_convert('sndon.png',True)
        self.btnS = self.btnS_on
        self.btnS_off = load_image_convert('sndoff.png',True)
        self.difficulty_buttons = [self.btnEasy,self.btnEasy_hover,self.btnNormal,self.btnNormal_hover,\
            self.btnHard,self.btnHard_hover]

        #Below we load the sound clips
        self.volume = 0.3
        self.s_intro = load_sound('intro.wav')
        self.s_selectlvl = load_sound('intermediatescreen.wav')
        self.s_mainloop = load_sound('drumloop.wav')
        self.s_nextdiff = load_sound('get_ready.wav')
        self.s_k1 = load_sound('key1.wav')
        self.s_k2 = load_sound('key2.wav')
        self.s_k3 = load_sound('key3.wav')
        self.s_k4 = load_sound('key4.wav')
        self.click = load_sound('click.wav')
        self.s_wrong = load_sound('buzz.wav')
        self.click.set_volume(.3)
        self.s_key_list = [self.s_k1,self.s_k1,self.s_k2,self.s_k2,self.s_k3,self.s_k3,self.s_k4,self.s_k4]
        self.s_intro.set_volume(self.volume)
        self.s_intro.play(-1, 0, 1000)
        self.player_clicks = 0
        self.sound_off = False

        #Below is the game difficulty and extra settings
        self.amt_of_nums = 21 #how many papers on deck max 63
        self.max_number = 10 #highest num value on paper
        self.min_numbers = 1 #lowest num
        self.difficulty = 0 #
        self.big_black = 7
        self.the_sum = 0 #the target sum
        self.the_current_sum = 0 #the sum currently added.
        self.time_limit = 9
        self.angle = 0
        self.opacity = 0
        self.highest_combo = 0

        #Below is the number array generators to provide numbers and sums
        self.m_pos = (0,0)
        self.red_nums = [] # red array
        self.blue_nums = [] # blue array
        self.green_nums = [] # green array
        self.list_of_colors = [self.red_nums,self.blue_nums,self.green_nums]
        self.colour_of_sum = 0
        self.game_msg = '' # end round message

        #Below is the score settings and font helpers
        self.score = 0
        self.selected_colour_index = 0
        self.numbers_clicked = []
        self.num_objects_clicked = []
        self.gamefont = load_font("VarsityPlaybook-DEMO.ttf",75)
        self.gamefont_sm = load_font("VarsityPlaybook-DEMO.ttf",30)
        self.liveshelper = renderfont("Mistakes :",self.gamefont_sm,True,Game.WHITE)
        self.score_board = renderfont(str(self.score),self.gamefont,True,(238,41,41))
        self.lives = ['','a','b','c']
        self.lives_index = 0
        self.livesfont = load_font("tally.ttf",40)
        self.lives_board = renderfont(self.lives[0],self.livesfont, True,Game.WHITE)
        self.numfont = load_font("VarsityPlaybook-DEMO.ttf",35)
        self.numberfont = renderfont(str(self.the_sum),self.numfont,True,Game.BLACK)
        self.sum_clicked = renderfont(str(sum(self.numbers_clicked)),self.numfont,True,Game.BLACK)
        self.game_msgfont  = load_font("round.ttf",50)
        self.msg_render = renderfont(self.game_msg,self.game_msgfont,True,Game.ORANGE)
        self.name = ''
        self.name_text = renderfont(self.name,self.numfont,True,Game.RED)
        self.highscores = HighScores(0,0)
        self.score_list = self.highscores.readhighscore()
        self.score_list = dict(sorted(self.score_list.iteritems(),None,key=operator.itemgetter(1),reverse=True)[:8])
        self.last_gamestate = ''
        self.remove_msg = False
        self.time_attack = False
        self.round_time = 0
        self.time_elapsed = 0
        self.start = 0
        self.full_bar_width = 450

        #Below is the Grid options and settings
        self.margin = 5
        self.g_width = 62
        self.g_height = 50
        self.grid = []
        self.my_grid_list = []
        self.column = 11
        self.row = 10
        self.bad_positions = [[1,0],[1,1],[1,2],[2,0],[2,1],[2,2],[9,9],[9,10],[9,11]]
        self.generate_grid()
        self.numbers = []

        self.FPS = 30
        Game.REFRESH = pygame.USEREVENT+1
        pygame.time.set_timer(Game.REFRESH, 1000//self.FPS)

    def run(self):
        """Loop forever processing events"""
        running = True
        while running:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.m_pos = pygame.mouse.get_pos()
                if self.state == Game.PLAYING:
                    self.get_clicked(self.m_pos)                  
            elif event.type == Game.REFRESH:
                if self.state == Game.START_SCREEN:
                    self.draw_startscreen()
                elif self.state == Game.PLAYING:
                    self.draw()
                elif self.state == Game.ENDROUND:
                    self.draw_endscreen()
                elif self.state == Game.SELECT_LEVEL:
                    self.draw_select_levelscreen()
                elif self.state == Game.HIGHSCORE:
                    self.draw_highscore_screen()
                elif self.state == Game.INSTRUCTION:
                    self.draw_instruction_screen()
            elif event.type == pygame.KEYDOWN:
                if self.state == Game.SELECT_LEVEL:
                    pressed = pygame.key.get_pressed()
                    self.set_name(pressed)

            else:
                pass # an event type we don't handle 

    def game_over(self):
        """Clears everything from the board and sets highscores"""
        self.highscores.score = self.score
        try:
            self.highscores.writehighscores()
        except:
            print "Something went wrong saving your score."
        self.score_list = self.highscores.readhighscore() 
        self.column = 11
        self.row = 10
        self.big_black = 7
        self.numbers = []
        self.lives_index = 0
        self.the_current_sum = 0
        self.num_objects_clicked = []
        self.numbers_clicked = []
        self.amt_of_nums = 21
        self.max_number = 10
        self.min_numbers = 1
        self.m_pos = (0,0)
        self.difficulty = 0
        self.all_nums = []
        self.my_grid_list = []
        self.split_num_colors()
        self.generate_grid()
        self.lives_board = renderfont(self.lives[self.lives_index],\
                self.livesfont, True,Game.WHITE)
        self.s_mainloop.stop()
        self.s_intro.set_volume(self.volume)
        self.s_intro.play(-1, 0, 1000)

    def next_difficulty(self):
        """Increments the difficulty"""
        self.column = 11
        self.row = 10
        self.all_nums = self.generate_numarray()
        self.split_num_colors()
        self.generate_grid()
        if self.amt_of_nums < 66:
            self.amt_of_nums += 3 # How many papers on deck max 66
        self.max_number += 5 # Highest num value on paper
        if self.big_black != 16:
            self.big_black += 1 # Max should be 16
        self.opacity = 0
        self.game_msg = "Get Ready For Next Round"
        self.msg_render = renderfont(self.game_msg,self.game_msgfont,True,Game.ORANGE)
        self.player_clicks = 0
        self.s_nextdiff.set_volume(self.volume)
        self.s_nextdiff.play()

    def set_difficulty(self):
        if self.difficulty == 2:
            self.big_black = 11
            self.lives_index = 1
            self.amt_of_nums = 36
            self.max_number = 16
            self.min_numbers = 1
            self.m_pos = (0,0)
            self.lives_board = renderfont(self.lives[0],\
                    self.livesfont, True,Game.WHITE)
        elif self.difficulty == 4:
            self.big_black = 16
            self.lives_index = 3
            self.amt_of_nums = 51
            self.max_number = 26
            self.min_numbers = 1        
            self.lives_board = renderfont("Don't",\
                    self.livesfont, True,Game.WHITE)
        self.m_pos = (0,0)   
        self.all_nums = self.generate_numarray()
        self.split_num_colors()
        self.display_sum()
        self.opacity = 0

    def set_colour(self):
        """Sets the colour of for the next sum, check to see what colour is on the board"""
        empty_list_indexes = [i for i,j in enumerate(self.list_of_colors) if not j]
        if len(empty_list_indexes) > 0:
            all_indexes = range(0,3)
            if len(empty_list_indexes) == 3:
                self.next_difficulty()
            else:
                self.selected_colour_index = random.choice([x for x in all_indexes if x not in empty_list_indexes])
        else:
            self.selected_colour_index = random.randint(0,3)
        self.colour_of_sum = Game.COLOUR_ARRAY[self.selected_colour_index]

    def remove_nums_from_field(self):
        """Removes numbers from the field"""
        for i in self.num_objects_clicked:
            i.remove = True
            if i.colour != Game.BLACK:
                colour_index = Game.FIELD_COLOUR_ARRAY.index(i.colour)
            self.list_of_colors[colour_index].remove(i.number)
            self.all_nums.remove(i.number)
        self.next_sum()

    def display_sum(self):
        """Displays the sum on the board, also selects it's colour"""
        self.set_colour()
        if self.colour_of_sum == Game.BLACK:
            self.spliced_all_nums = self.all_nums[:self.big_black] # For performance reasons
            self.the_sum = self.generate_sum(self.spliced_all_nums)
        else:
            self.the_sum = self.generate_sum(self.list_of_colors[self.selected_colour_index])
        self.sum_board = renderfont(str(self.the_sum),self.gamefont,True,self.colour_of_sum)

    def split_num_colors(self):
        """Splits the number array into coloured chunks"""
        split_even = self.amt_of_nums//3
        colour_array=[self.all_nums[x:x+split_even] for x in xrange(0,len(self.all_nums),split_even)]
        c_index = 0
        for i in colour_array:
            for j in i:
                new_paper = self.make_numbers(j,Game.FIELD_COLOUR_ARRAY[c_index])
                self.numbers.append(new_paper)
            self.list_of_colors[c_index] = i[:]
            c_index += 1

    def make_numbers(self,num,colour):
        """Makes numbers, paper objects, and gives them a position on the grid"""
        retry = True
        while retry:
            retry = False
            grid_position = [random.randrange(1,self.row), random.randrange(1,self.column)]
            for n in self.numbers:
                if (grid_position in self.bad_positions) or (n.grid_position == grid_position):
                    retry = True
                    break
            position = self.my_grid_list[grid_position[0]][grid_position[1]]
        return Paper(num,position,self.numfont,random_image(),colour,grid_position)

    def generate_grid(self):
        """Generates the grid structure to spawn numbers on paper images"""
        self.grid = [[None for x in range(self.column)] for y in range(self.row)]
        for row in range(self.row):
            self.my_grid_list.append([])
            for column in range(self.column):
                self.my_grid_list[row].append([(self.margin+self.g_width)*column+self.margin,\
                    (self.margin+self.g_height)*row+self.margin])

    def next_sum(self):
        """Clearing round variables"""
        self.num_objects_clicked = []
        self.numbers_clicked = []
        self.the_current_sum = 0
        self.display_sum()
        self.sum_clicked = renderfont(str(sum(self.numbers_clicked)),\
                self.numfont,True,Game.BLACK)
        self.render_life(self.lives_index)
        self.start = time.time()
        if self.time_attack:
            self.time_elapsed = 0
            self.full_bar_width = 450

    def add_to_sum(self,num_object,adding,number):
        """Appends numbers you selected to check if they are the sum"""
        if adding:
            self.the_current_sum += number
            self.numbers_clicked.append(number)
            self.num_objects_clicked.append(num_object)
            if self.the_current_sum == self.the_sum:
                self.update_score(self.numbers_clicked) 
                self.remove_nums_from_field()     
        else:
            try:
                self.the_current_sum -= number
                self.numbers_clicked.remove(number)
                self.num_objects_clicked.remove(num_object)
            except:
                # Tried to click a number that is already removed. 
                pass
        self.sum_clicked = renderfont(str(sum(self.numbers_clicked)),\
                self.numfont,True,Game.BLACK)

    def get_clicked(self,pos):
        """Gets the number that is clicked."""
        for n in self.numbers:
            if self.screen.blit(n.image.convert(),n.position).collidepoint(pos):
                if self.correct_colour(n.colour):
                    add_or_subtract = n.clicked()
                    self.add_to_sum(n,add_or_subtract,n.number)
                    if self.the_current_sum > self.the_sum:
                        add_or_subtract = n.clicked()
                        self.add_to_sum(n,add_or_subtract,n.number)
                        self.dock_life()
                        self.s_wrong.set_volume(self.volume)
                        self.s_wrong.play()
                    else:
                        self.s_key_list[self.player_clicks%8].set_volume(self.volume)
                        self.s_key_list[self.player_clicks%8].play()
                else:
                    self.s_wrong.set_volume(self.volume)
                    self.s_wrong.play()
                    unclick = n.clicked()
                    self.subtract_from_sum(n)
                    self.dock_life()
                self.player_clicks += 1

    def subtract_from_sum(self,n):
        """Forces an unclick on the paper objects"""
        unlick = n.clicked()

    def dock_life(self):
        """Docks a life, how can you even make a mistake with addition?"""
        try:
            self.lives_index += 1
            self.lives_board = renderfont(self.lives[self.lives_index],\
                self.livesfont, True,Game.WHITE)
        except:
            self.game_over()
            self.state = Game.ENDROUND

    def render_life(self,index):
        """Renders life when needed to be updated"""
        try:
            self.lives_board = renderfont(self.lives[index],\
                self.livesfont, True,Game.WHITE)
        except:
            self.game_over()
            self.state = Game.ENDROUND

    def correct_colour(self,colour_chosen):
        """Checks if the colour choosen is the correct colour"""
        if colour_chosen == Game.COLOUR_ARRAY[self.selected_colour_index] \
            or self.colour_of_sum == Game.BLACK:
            return True
        else:
            return False

    def update_score(self,nums_clicked):
        """Updates the score when a sum is reached"""
        self.score += sum(nums_clicked)*len(nums_clicked)
        self.score_board = renderfont(str(self.score),self.gamefont,True,(238,41,41))
    
    def generate_numarray(self):
        """Generates an array of numbers that will show up in the field"""
        return [random.randrange(1,self.max_number) for i in xrange(self.amt_of_nums)]

    def generate_sum(self,color_array):
        """Randomly selects a power set to display the sum to add to"""
        possible = self.generate_possible_combos(color_array)
        return sum(random.choice(possible))

    def generate_possible_combos(self,number_array):
        """Generates a power set of all possible combos of number to get sum"""
        a = power_set(number_array)
        return filter(None,a)

    def rotate_image(self):
        """Designate a rect to keep the image centered and rotates it"""
        self.angle += 1
        self.angle = self.angle%360
        orig_rect = self.png_light_rect
        this_light_image = pygame.transform.rotate(self.png_light,self.angle%360)
        rect_border = orig_rect.copy()
        rect_border.center = this_light_image.get_rect().center
        this_light_image = this_light_image.subsurface(rect_border).copy()
        return this_light_image

    def blit_play_button(self):
        """Shows the play button and creates hover over effect"""
        pos = pygame.mouse.get_pos()
        if self.screen.blit(self.btnPlay,(335,350)).collidepoint(pos):        
            if self.screen.blit(self.btnPlayo,(335,350)).collidepoint(self.m_pos):
                self.click.play()
                if self.state == Game.START_SCREEN:
                    self.last_gamestate = Game.START_SCREEN
                elif self.state == Game.ENDROUND:
                    self.last_gamestate = Game.ENDROUND
                self.state = Game.SELECT_LEVEL
                self.time_attack = False
                self.opacity = 0
                self.s_intro.stop()
                self.s_selectlvl.play(-1, 0, 1000)
                self.s_selectlvl.set_volume(self.volume)
        if self.screen.blit(self.btnScore,(335,400)).collidepoint(pos):
            if self.screen.blit(self.btnScoreHover,(335,400)).collidepoint(self.m_pos):
                self.click.play()
                if self.state == Game.ENDROUND:
                    self.last_gamestate = Game.ENDROUND
                elif self.state == Game.START_SCREEN:
                    self.last_gamestate = Game.START_SCREEN
                self.state = Game.HIGHSCORE
                self.opacity = 0
        if self.screen.blit(self.btnTime,(335,450)).collidepoint(pos):           
            if self.screen.blit(self.btnTimeHover,(335,450)).collidepoint(self.m_pos):
                self.click.play()
                self.time_attack = True
                if self.state == Game.START_SCREEN:
                    self.last_gamestate = Game.START_SCREEN
                self.state = Game.SELECT_LEVEL
                self.opacity = 0
                self.s_intro.stop()
                self.s_selectlvl.play(-1, 0, 1000)
                self.s_selectlvl.set_volume(self.volume)
        if self.screen.blit(self.btnIntro,(335,500)).collidepoint(pos):      
            if self.screen.blit(self.btnIntroHover,(335,500)).collidepoint(self.m_pos):
                self.click.play()
                if self.state == Game.START_SCREEN:
                    self.last_gamestate = Game.START_SCREEN
                elif self.state == Game.ENDROUND:
                    self.last_gamestate = Game.ENDROUND
                self.state = Game.INSTRUCTION
                self.opacity = 0

    def display_timelimit(self):
        """Displays the timelimit bar"""
        if self.time_elapsed != 0:
            self.full_bar_width = 450*((self.time_limit-self.time_elapsed)/self.time_limit)
        pygame.draw.rect(self.screen,Game.GREEN,\
            [150,560,self.full_bar_width,30]) # Start width: 450

    def tick_clock(self):
        """Checks to see if player surpassed the time limit on Time attack"""
        self.time_elapsed = time.time() - self.start
        if self.time_elapsed > self.time_limit:
            for i in self.num_objects_clicked:
                i.clicked()
            self.lives_index += 1
            self.next_sum()

    def blit_level_button(self,btn,btnhover,height,diff):
        """Shows the diffuclty buttons and selects the game diffculty"""
        if self.screen.blit(btn,(200,height)).collidepoint(pygame.mouse.get_pos()):            
            if self.screen.blit(btnhover,(200,height)).collidepoint(self.m_pos):
                self.difficulty = diff
                self.set_difficulty()
                self.state = Game.PLAYING
                self.score = 0
                self.create_highscore()
                self.the_current_sum = 0
                self.opacity = 0
                self.update_score(self.numbers_clicked)
                self.sum_clicked = renderfont(str(sum(self.numbers_clicked)),\
                self.numfont,True,Game.BLACK)
                self.s_selectlvl.stop()
                self.s_mainloop.play(-1, 0, 1000)
                self.s_mainloop.set_volume(self.volume)
                if self.time_attack:   
                    self.time_limit = (diff//2+1)*9
                    self.start = time.time()
                
    def set_name(self,press):
        """Allows players to input their names for high scores"""
        if len(self.name) > 20:
            self.name = self.name[:-1]
        else:
            for i in xrange(97, 123):
                if press[i] == 1:
                    letter = pygame.key.name(i)
                    self.name += letter
            if press[8]:
                self.name = self.name[:-1]
            elif press[32]:
                self.name += "_"
        self.name_text = renderfont(self.name.upper(),self.gamefont_sm,True,Game.BLACK)

    def create_highscore(self):
        """Creates a highscore object"""
        if self.name == '':
            self.name = 'none'
        self.highscores = HighScores(self.score,self.name)

    def show_highscore(self,height):
        """Sorts the highscores with the best score down, then displays"""
        for key,val in sorted(self.score_list.iteritems(),None,key=operator.itemgetter(1),reverse=True)[:8]:
            self.screen.blit(renderfont("%s .... %d" % (key,val),self.numfont,\
                True,Game.BLACK),(250,height))
            height += 50

    def transition(self,background,background_rect):
        """Displays or removes the messages with magic involved"""
        if self.opacity < 256:
            self.opacity += 17
        temp = pygame.Surface((background.get_width(),background.get_height())).convert()
        temp.blit(self.screen,background_rect)
        temp.blit(background, (0, 0))
        temp.set_alpha(self.opacity)        
        self.screen.blit(temp,(0,0))

    def display_sound(self):           
        if self.screen.blit(self.btnS_on,(20,560)).collidepoint(self.m_pos):
            self.sound_off = not self.sound_off
            if self.sound_off:
                self.volume = 0
                pygame.mixer.pause()
                self.btnS_on = self.btnS_off
            else:
                self.volume = 0.3
                self.btnS_on = self.btnS
                pygame.mixer.unpause()
            self.m_pos = 0,0

    def display_msg(self):
        """Displays or removes the messages with magic involved"""
        if self.opacity < 255:
            self.screen.blit(self.msg_render,(75,270))
        else:
            pygame.time.delay(7000)
            self.game_msg = ''
            self.opactiy = 0

    def draw_select_levelscreen(self):
        """Update the display for the main game page""" 
        self.transition(self.bg_dif,self.bg_dif_rect)
        for i in xrange(0,6,2):
            self.blit_level_button(self.difficulty_buttons[i],self.difficulty_buttons[i+1]\
                    ,250+i*50,i)
        self.screen.blit(self.name_text,(205,166))
        if self.screen.blit(self.btnBack,(650,550)).collidepoint(pygame.mouse.get_pos()):
            if self.screen.blit(self.btnBackHover,(650,550)).collidepoint(self.m_pos):
                self.click.play()
                self.s_selectlvl.stop()
                self.state = self.last_gamestate
                self.s_intro.play(-1, 0, 1000)
                self.opacity = 0
        self.display_sound()
        pygame.display.flip()

    def draw_highscore_screen(self):
        """Update the display for the main game page"""
        self.transition(self.bg_score,self.bg_score_rect)
        self.show_highscore(155)
        if self.screen.blit(self.btnBack,(650,550)).collidepoint(pygame.mouse.get_pos()):
            if self.screen.blit(self.btnBackHover,(650,550)).collidepoint(self.m_pos):
                self.state = self.last_gamestate
                self.opacity = 0
        self.display_sound()
        pygame.display.flip()

    def draw_instruction_screen(self):
        """Draws the instruction screen for the game state"""
        self.transition(self.bg_instruct,self.bg_instruct_rect)
        if self.screen.blit(self.btnBack,(650,550)).collidepoint(pygame.mouse.get_pos()):
            if self.screen.blit(self.btnBackHover,(650,550)).collidepoint(self.m_pos):
                self.state = self.last_gamestate
                self.opacity = 0
        self.display_sound()
        pygame.display.flip()

    def draw_startscreen(self):
        """Updates the display for the start screen"""
        self.transition(self.bg_front,self.bg_front_rect)
        self.screen.blit(self.rotate_image(),(0,-200)) 
        self.blit_play_button()
        self.screen.blit(self.png_sign,self.png_sign_rect)
        self.display_sound()
        pygame.display.flip()

    def draw_endscreen(self):
        """Draws the end screen of the game (game over)"""
        self.transition(self.bg_end,self.bg_end_rect)
        self.blit_play_button()
        self.screen.blit(self.score_board,(350,220))
        self.display_sound()
        pygame.display.flip()

    def draw(self):
        """Update the display for the main game page""" 
        self.transition(self.bg_game,self.bg_game_rect)
        self.screen.blit(self.score_board,(650,530))
        self.screen.blit(self.lives_board,(735,30))
        self.screen.blit(self.liveshelper,(625,30))
        self.screen.blit(self.sum_board,(80,50))
        self.screen.blit(self.sum_clicked,(103,118))
        self.display_sound()
        for n in self.numbers:
            if n.kill:
                self.numbers.remove(n)
            n.display_paper(self.screen)
        if self.time_attack:
            self.display_timelimit()
            self.tick_clock()
        if self.game_msg != '':
            self.display_msg()
            self.start = time.time()
        pygame.display.flip()

Game().run()
pygame.quit()
sys.exit()