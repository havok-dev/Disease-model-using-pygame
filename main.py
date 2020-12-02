#importing libraries
import numpy as np
import pygame,sys
#Defining the rgb values of the colours in the program
BLACK=(0,0,0)
WHITE=(255,255,255)
BLUE=(53, 128, 232)
GREEN=(70, 245, 12)
RED=(245, 12, 12)
GREY=(230,230,230)
YELLOW=(190,175,50)

BACKGROUND=WHITE
#making the dot
class person(pygame.sprite.Sprite):         #it will inherit Sprite class from pygame
    def __init__(                           #defining an initializer (where variables are initialized
        self,
        x,                                  #coordinate on x axis
        y,                                  #coordinate on y axis
        width,
        height,                                #width and height of the screen
        color=BLACK,                            #colour
        radius=5,                                #radius
        velocity=[0,0],                            #2-d velocity (has value for x and y)
        randomize=False,                          #this variable is declare to have randomized movement of the clas
    ):
        #defining attribute of the class
        super().__init__()                          #calling initializer of parent class
        self.image=pygame.Surface(
            [radius*2,radius*2])                    #pygame take mage to assign we assign a surface of width and height of radius *2
        self.image.fill(BACKGROUND)                 #we fill it with the colour of backgrounf
        pygame.draw.circle(                            # we draw a circles with this in image of color, position and radius
            self.image,color,(radius,radius),radius
        )

        self.rect=self.image.get_rect()             #defining hitbox and position and hitbox of the surface
        self.pos=np.array([x,y],dtype=np.float64)   #define the position  in form og numpy array
        self.vel=np.asarray(velocity,dtype=np.float64)  #define velocity on form of numpy array
        self.kill_switch_on=False                       #defining a kill switch to check if the person has died or not
        self.recovered=False                             #defining a recovered variable to check if person as recvered or not
        self.randomize=randomize                         # this to see if the dot ca have variable velocity
        self.WIDTH=width                                # the width and height variables
        self.HEIGHT=height
        self.alltoinfected=True
    def update(self):                               #this function will update the position and all other attributes of the class
        self.pos+=self.vel                          #this will add the value of vel in position array ,
        x,y=self.pos                                #the is assign the value of position num  array to x,y of dot
        if x<0:                                     #if the dot will hit the left boundary of screen
            self.pos[0]=self.WIDTH                  #the first value of pos array is changed
            x=self.WIDTH                            #the value of width is changed
        if x> self.WIDTH:                           #if dot hits the right side of the screen
            self.pos[0]=0
            x=0
        if y<0:                                     #if the dot hits the down side of screed
            self.pos[1]=self.HEIGHT
            y=self.HEIGHT
        if y>self.HEIGHT:                            #if the dot hits the upside of screen
            self.pos[1]=0
            y=0
        self.rect.x=x                                  #updating the values of the rectangle
        self.rect.y=y
        vel_norm=np.linalg.norm(self.vel)               #getting noralized velocity using numpy function
        if vel_norm>3:                                     #this is done or else the dot will become extreamely fast
            self.vel/=vel_norm
        if self.randomize:                                  #this will add randomization by changing the velocity
            self.vel+=np.random.rand(2)*2-1
        if self.kill_switch_on:                             #this will check if the dot has died or recovered
            self.cyclestodeath-=1
            if self.cyclestodeath<=0:
                self.kill_switch_on=False
                a=np.random.rand()
                if self.mortality_rate>a:
                    self.kill()
                else:
                    self.recovered=True

    def respawn(self,color,radius=5):                   #this function is used when we respawn someone when they come in contact, basically this will return a new dot
        return person(
            self.rect.x,
            self.rect.y,
            self.WIDTH,
            self.HEIGHT,
            color=color,
            velocity=self.vel
        )
    def killswitch(self,cyclestodeath=20,mortality_rate=0.2):           #this will start the kill switch on part when the person gets infected
        self.kill_switch_on=True
        self.cyclestodeath= cyclestodeath
        self.mortality_rate=mortality_rate

class Simulation:                                                           #this is the simulation class
    def __init__(self,width=600,height=400):                                #iinitializing the hieght and width window
        self.WIDTH=width
        self.HEIGHT=height

        self.susceptible_container=pygame.sprite.Group()                    #making a group of
        self.infected_container = pygame.sprite.Group()
        self.recovered_container = pygame.sprite.Group()
        self.all_container = pygame.sprite.Group()

        self.n_susceptible=50
        self.n_infected=10
        self.n_quarantined=80
        self.n_recovered=0
        self.T=1000
        self.cyclestodeath=20
        self.mortalityrate=0.2
        self.probablitytogetinfected=0.5

    def start(self,randomize=False):
        self.N=self.n_susceptible+self.n_infected+self.n_quarantined
        pygame.init()                                                                  #initializing the game
        screen=pygame.display.set_mode([self.WIDTH,self.HEIGHT])                        #setting the screen size
        container=pygame.sprite.Group()

        for i in range(self.n_susceptible):                                                                #this loop will make all the susceptible humans
            x=np.random.randint(0,self.WIDTH+1)                                                             #randomly assigning the value of x,y and velocity and assigning it to a person class
            y=np.random.randint(0,self.HEIGHT+1)
            vel=np.random.rand(2)*2-1
            human=person(x,y,self.WIDTH,self.HEIGHT,color=GREEN,velocity=vel,randomize=randomize)                    #adding that person to the respective containers
            self.susceptible_container.add(human)
            self.all_container.add(human)

        for i in range(self.n_quarantined):                                                                 #initializing the quarantined humans
            x=np.random.randint(0,self.WIDTH+1)
            y=np.random.randint(0,self.HEIGHT+1)
            vel=[0,0]
            human=person(x,y,self.WIDTH,self.HEIGHT,color=GREEN,velocity=vel,randomize=False)
            self.susceptible_container.add(human)
            self.all_container.add(human)
        for i in range(self.n_infected):                                                                    #initializing the infected people
            x=np.random.randint(0,self.WIDTH+1)
            y=np.random.randint(0,self.HEIGHT+1)
            vel=np.random.rand(2)*2-1
            human=person(x,y,self.WIDTH,self.HEIGHT,color=RED,velocity=vel,randomize=randomize)
            human.killswitch(                                                                                       # turning on the kill switch
                self.cyclestodeath,
                self.mortalityrate
            )
            self.infected_container.add(human)
            self.all_container.add(human)

        T=100000                                                #assigning the time it going to run
        stats=pygame.Surface((self.WIDTH//4,self.HEIGHT//4))            #this is used to make a graph , it will cover a portion of the the screen
        stats.fill(GREY)                                                   #intially filled with grey
        stats.set_alpha(230)                                                  #seting a point
        stats_pos= (self.WIDTH//40,self.HEIGHT//40)                             #setting in

        clock=pygame.time.Clock()                               #initialize the clock

        for i in range(T):                                          #game loop
            for event in pygame.event.get():                            #if you want to exit
                if event.type==pygame.QUIT:
                    sys.exit()

            self.all_container.update()                                 #updating all the containers

            screen.fill(BACKGROUND)                                     #fill the screen
            #UPDATE STATS
            stats_height=stats.get_height()                                     #extract variable of height and width
            stats_width=stats.get_width()
            n_infected=len(self.infected_container)                             #number of people infect now is ewqual to len of infected container
            n_population=len(self.all_container)                                #similar
            n_recovered=len(self.recovered_container)                           #similar
            t=int((i/self.T)*stats_width)                                       #current time
            y_infect=int(stats_height-(n_infected/n_population)*stats_height)   #the height of infected, dead,and recovered
            y_dead=int(((self.N-n_population)/self.N)*stats_height)
            y_recovered=int((n_recovered/n_population)*stats_height)
            stats_graph=pygame.PixelArray(stats)                        #we make a graph with pixel array,
            stats_graph[t,y_infect:]=pygame.Color(*GREEN)               #giving the colours
            stats_graph[t,:y_dead]=pygame.Color(*YELLOW)
            stats_graph[t,y_dead:y_dead+y_recovered]=pygame.Color(*BLUE)

            #how the virus will spread
            collision_group=pygame.sprite.groupcollide(     #this is called when two dots collide and will be added to group collide
                self.susceptible_container,                 #of susceptible and infected container
                self.infected_container,
                True,                                       #susceptible person will be erased
                False,                                      #infected will stay
            )

            for human in collision_group:                   #to added the human in the collision group in the infected container
                a=np.random.rand()
                if a<=self.probablitytogetinfected:            #concept of probablity
                    new_human=human.respawn(RED)                #respawn the person
                    new_human.vel*= -1                          #reversing velocity
                    new_human.killswitch(                       #turning on the kill switch
                        self.cyclestodeath,
                        self.mortalityrate
                )
                    self.infected_container.add(new_human)
                    self.all_container.add(new_human)
                else:
                    new_human=human.respawn(GREEN)
                    new_human.vel*= -1
                    self.susceptible_container.add(new_human)
                    self.all_container.add(new_human)

            #any recoveries?
            recovered=[]
            for human in self.infected_container:                       #to added the recovered dot in different container
                if human.recovered:
                    n_recovered+=1
                    new_human=human.respawn(BLUE)
                    self.recovered_container.add(new_human)
                    self.all_container.add(new_human)
                    recovered.append(human)

            if len(recovered)>0:                                            #when we add the person in the recovered container then we have to remove it from infected container
                self.infected_container.remove(*recovered)
                self.all_container.remove(*recovered)



            self.all_container.draw(screen)                                    #to draw all the function on the graph
            del stats_graph                                                    #delete stats graph so we can unlock stats
            stats.unlock()
            screen.blit(stats,stats_pos)                                        #draw stat at stat pos
            pygame.display.flip()
            clock.tick(30)                                                     #to show how the clock ticks

        pygame.quit()


if __name__=="__main__":
    covid=Simulation()
    covid.cyclestodeath=int(input("Enter the cycles to death:"))
    covid.probablitytogetinfected=int(input("Enter the probablity to get infected:"))/100
    covid.mortalityrate=int(input("Enter the mortality rate:"))/100
    covid.n_susceptible=int(input("Enter the amount of people susceptable in the sample space:"))
    covid.n_quarantined=int(input("Enter the amount of people quarantined:"))
    covid.n_infected=int(input("Enter the amount of people infected:"))
    covid.start(randomize=True)