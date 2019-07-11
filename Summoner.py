class Summoner:
    def __init__(self,level,details,ruleset):
        self.ruleset = ruleset
        self.level = level
        self.name = details["name"]
        self.color = details["color"]
        stats = details["stats"]
        self.team_mod = []
        self.enemy_mod = []

        if ruleset != "Silenced Summoners":
            #print(details)
            for key in stats:
                if key == "mana":
                    continue
                if stats[key] >= 0:
                    self.team_mod.append(stats[key])
                    self.enemy_mod.append(0)
                else:
                    self.team_mod.append(0)
                    self.enemy_mod.append(stats[key])
        else:
            self.team_mod = [0]*6
            self.enemy_mod = [0]*6

        if ruleset == "Unprotected":
            self.team_mod[3] = 0
            self.enemy_mod[3] = 0
