from Summoner import Summoner
from Monster import Monster
class Team:
    def __init__(self,summoner,monsters,ruleset,sm_dict,player):
        self.player = player
        self.summoner = Summoner(summoner["level"],sm_dict[summoner["id"]],ruleset)
        self.monsters = []

        self.ruleset = ruleset
        if ruleset != "Silenced Summoners":
            self.team_mod = self.summoner.team_mod
            self.enemy_mod = self.summoner.enemy_mod
        else:
            self.team_mod = [0]*6
            self.enemy_mod = [0]*6

        pos = 0
        for monster in monsters:
            self.monsters.append(Monster(monster["level"],sm_dict[monster["id"]],pos,ruleset))
            pos += 1

    def recompute_pos(self):

        for i in range(0,len(self.monsters)):
            self.monsters[i].pos = i

