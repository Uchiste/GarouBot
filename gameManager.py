from botclass import *
from enum import Enum,auto

class State(Enum):
    UNUSED = auto()
    RUNNING = auto()
    ENDED = auto()
    
class GameManager:
    def __init__(self):
        self.stackID=0
        self.games=[]
    
    def newGame(self,ctx):
        game=Game(ctx,self.stackID)
        self.games.append([game,State.UNUSED])
        self.stackID+=1
        return game
    
    def findGame(self,ctx,state):
        for game in self.games:
            if game[0] != None and game[0].server_id == ctx.guild.id and state==game[1]:
                return game[0]
        return None
    
    def runningGame(self,game):
        self.games[game.id][1]=State.RUNNING
        
    def endedGame(self,game):
        self.games[game.id][1]=State.ENDED