import random
class Monster:

    def __init__(self,level,details,pos,ruleset):
        self.ruleset = ruleset
        self.pos = pos
        self.level = level
        self.name = details["name"]
        self.color = details["color"]
        stats = details["stats"]
        self.stats = []
        self.base_stats = []
        self.poisoned = False
        for key in stats:
            if key == "mana" or key == "abilities":
                continue
            self.stats.append(stats[key][level - 1])
            self.base_stats.append(stats[key][level-1])
        if ruleset == "Unprotected":
            self.base_stats[3] = 0
            self.stats[3] = 0
        elif ruleset == "Armored Up":
            self.base_stats[3] += 2
            self.stats[3] += 2

        if self.stats[0] > 0:
            self.type = "melee"
            self.damage = self.stats[0]
            self.can_attack = True
        elif self.stats[1]>0:
            self.type = "ranged"
            self.damage = self.stats[1]
            self.can_attack = True
            self.base_stats[5] += 0.1
            self.stats[5] += 0.1
        elif self.stats[2]>0:
            self.type = "magic"
            self.damage = self.stats[2]
            self.can_attack = True
            self.base_stats[5] += 0.2
            self.stats[5] += 0.2
        else:
            self.type = "passive"
            self.can_attack = False

        #self.stats[5] += level*0.0001

        if ruleset == "Back to Basics":
            self.abilities = []
        else:
            abilities = stats["abilities"][0:level]
            mon_abilities = []
            for ability in abilities:
                if ruleset == "Healed Out":
                    if ability == "Heal":
                        continue
                    elif ability == "Tank Heal":
                        continue
                    elif ability == "Triage":
                        continue
                elif ruleset == "Fog of War":
                    if ability == "Sneak":
                        continue
                    elif ability == "Snipe":
                        continue
                elif ruleset == "Super Sneak":
                    if ability == "Reach":
                        continue

                mon_abilities += ability
            if ruleset == "Super Sneak" and type == "melee":
                mon_abilities += "Sneak"
            if ruleset == "Target Practice" and (type == "magic" or type == "ranged"):
                mon_abilities += "Snipe"


            self.abilities = mon_abilities

        self.can_resurrect = "Resurrect" in self.abilities
        self.divine_shield_up = "Divine Shield" in self.abilities


        self.calc_global_stat_modifiers()
        self.mod = [0]*6

        self.healable = True
        self.alive = True
        self.enraged = False
        self.stun = False

    def start_turn(self,team,team_enemy):
        if self.alive:
            if self.stun:
                self.stun = False
                return True

            if "Cleanse" in self.abilities:
                team.monsters[0].healable = True
                team.monsters[0].poison = False
                team.monsters[0].stun = False

                reverse_debuff = []
                for i in team.monsters[0].mod:
                    if i < 0:
                        reverse_debuff.append(i*-1)

                team.monsters[0].apply_buff(reverse_debuff,False,True)

            if not self.enraged and "Enrage" in self.abilities:

                if self.base_stats[4] > self.stats[4]:
                    self.enraged = True
                    self.stats[0] += 2
                    self.stats[5] += 1
            if self.poisoned:
                self.stats[4] -= 1

                if self.stats[4]<= 0:
                    self.stats[4] = 0
                    self.alive = False

            if "Repair" in self.abilities:
                dents = 0
                target = team.monsters[0]
                for mon in team.monsters:
                    diff = mon.base_stats[3]-mon.stats[3]
                    if diff > dents and target.alive:
                        target = mon
                        dents = diff


                target.stats[3] += 2
                if target.stats[3] > target.base_stats[3]:
                    target.stats[3] = target.base_stats[3]

            if "Heal" in self.abilities and self.healable:
                self.stats[4] += int(round(self.base_stats[4]*0.3,0))

                if self.stats[4] > self.base_stats[4]:
                    self.stats[4] = self.base_stats[4]

            elif "Tank Heal" in self.abilities:
                if team.monsters[0].alive and team.monsters[0].healable:
                    team.monsters[0].stats[4] += int(round(team.monsters[0].base_stats[4]*0.3,0))
                    if team.monsters[0].stats[4] > team.monsters[0].base_stats[4]:
                        team.monsters[0].stats[4] = team.monsters[0].base_stats[4]
            elif "Triage" in self.abilities:
                wounded = 0
                target = team.monsters[0]
                for mon in team.monsters:
                    diff = mon.base_stats[4]-mon.stats[4]
                    if diff > wounded and target.healable and target.alive:
                        target = mon
                        wounded = diff


                target.stats[4] += 2
                if target.stats[4] > target.base_stats[4]:
                    target.stats[4] = target.base_stats[4]




    def apply_buff(self,modifier,summoner,reverse):
        if summoner:
            for i in range(0,len(modifier)):
                self.base_stats[i] += modifier[i]
                self.stats[i] += modifier[i]
            if self.type == "melee":
                self.damage = self.stats[0]
            elif self.type == "ranged":
                self.damage = self.stats[1]
            elif self.type == "magic":
                self.damage = self.stats[2]
            else:
                self.damage = 0

        else:

            if not reverse:
                for i in range(0,len(modifier)):
                    if modifier[i] < 0 and int(self.base_stats[i]) <= 1:
                        continue
                    self.stats[i] += modifier[i]
                    self.mod[i] += modifier[i]
            else:
                for i in range(0,len(modifier)):
                    if modifier[i] < 0:
                        if self.mod[i] > 0:
                            self.stats[i] += modifier[i]
                            self.stats[i] += modifier[i]
                    else:
                        if self.mod[i] < 0:
                            self.stats[i] += modifier[i]
                            self.mod[i] += modifier[i]



    def calc_global_stat_modifiers(self):
        self.team_mod = [0]*6
        self.enemy_mod = [0]*6

        if "Weaken" in self.abilities:
            self.enemy_mod[0] -= 1
            self.enemy_mod[4] -= 1
        if "Slow" in self.abilities:
            self.enemy_mod[5] -= 1
        if "Demoralize" in self.abilities:
            self.enemy_mod[0] -= 1
        if "Silence" in self.abilities:
            self.enemy_mod[2] -=1

        if "Inspire" in self.abilities:
            self.team_mod[0] += 1
        if "Protect" in self.abilities:
            self.team_mod[3] += 2
        if "Swiftness" in self.abilities:
            self.team_mod[5] += 1
        if "Strengthen" in self.abilities:
            self.team_mod[4] += 1

    def find_target(self,monsters):
        mod = 1
        #Shield -1 damage to ranged and melee

        if "Opportunity" in self.abilities:
            weakest = 1000
            i = 0
            target = 0
            for mon in monsters:
                if mon.stats[4] < weakest:
                    weakest = mon.stats[4]
                    target = i
                i += 1
            return target

        if self.type == "melee":
            if self.pos == 0:
                return 0
            elif self.pos == 1 and "Range" in self.abilities:
                    if len(monsters)>2:
                        return 1
                    else:
                        return 0
            elif "Sneak" in self.abilities:
                return len(monsters) - 1
            elif "Melee Mayhem" == self.ruleset:
                return 0

        elif self.type == "ranged" or self.type == "magic":
            if self.pos == 0 and self.type == "ranged":
                return -1
            else:
                if "Sneak" in self.abilities:
                    return len(monsters) - 1
                elif "Snipe" in self.abilities:

                    if len(monsters)>1:
                        backrow = monsters[1:len(monsters)]
                        i = 1
                        pas = -1
                        for monster in backrow:
                            if monster.type == "magic" or monster.type == "ranged":
                                return i
                            if pas == -1 and monster.type == "passive":
                                pas = i
                            i += 0
                        if pas == -1:
                            pas = 0

                        return pas
                    else:
                        return 0
                else:
                    return 0
        return -1

    def attack_standard(self,own,target,damage=0):
        if damage == 0:
            damage = self.damage

        mod = 0
        if "Shield" in target.abilities and own.type != "magic":
            mod = -1
        if "Void" in target.abilities and own.type == "magic":
            mod = -1
        if target.stats[3] > 0 and self.type != "magic":
            rem_armor = target.stats[3] - (damage + mod)
            if "Piercing" in own.abilities and rem_armor < 0:
                rem_health = target.stats[4] + rem_armor
                if rem_health < 0:
                    rem_health = 0
                target.stats[4] = rem_health
            if rem_armor < 0 or "Shatter" in self.abilities:
                rem_armor = 0

            target.stats[3] = rem_armor
        else:
            rem_health = target.stats[4] - (damage + mod)
            if rem_health < 0:
                rem_health = 0
            target.stats[4] = rem_health

    def attack(self, monster,previous_monster,next_monster):
        if monster.divine_shield_up:
            monster.divine_shield_up = False
            return False
        if self.type == "melee" or self.type == "ranged":
            if self.ruleset != "Reverse Speed":
                evasion_rate = int(monster.stats[5] -self.stats[5])
                if evasion_rate > 0:
                    evasion_rate *= 0.1

            else:
                evasion_rate = int(monster.stats[5] - self.stats[5])
                if evasion_rate < 0:
                    evasion_rate = abs(evasion_rate)
                    evasion_rate *= 0.1


            if "Flying" not in self.abilities and "Flying" in monster.abilities:
                evasion_rate += 0.25
            if "Dodge" in monster.abilities:
                evasion_rate += 0.25
            evasion_rate = min(0.9,evasion_rate)

            if "Aim True" != self.ruleset and random.random() < evasion_rate:
                return False

            mod = 0
            if "Stun" in self.abilities:
                if random.random() < 0.5:
                    monster.stun = True
            if "Affliction" in self.abilities:
                if random.random() < 0.5:
                    monster.healable = False
            if "Poison" in self.abilities:
                if random.random() < 0.5:
                    monster.poisoned = True

            self.attack_standard(self,monster)

            if "Retaliate" in monster.abilities and monster.alive and monster.type == "melee":
                if random.random() <= 0.5:
                    self.attack_standard(monster,self)
            if "Thorns" in monster.abilities and monster.alive and monster.type == "melee":
                self.attack_standard(monster,self,2)
            if "Return Fire" in monster.abilities:
                self.attack_standard(monster,self,max(self.damage-1,1))

            if "Double Strike" in self.abilities:
                self.attack_standard(self,monster)



        elif self.type == "magic":
            mod = 0
            if "Void" in monster.abilities:
                mod = -1

            if self.ruleset == "Weak Magic":
                self.attack_standard(self,monster,self.damage+mod)
            else:
                rem_health = monster.stats[4] - (self.damage + mod)
                if rem_health < 0:
                    rem_health = 0
                monster.stats[4] = rem_health

            if "Magic Reflect" in monster.abilities:
                reflected_damage = max(1,(self.damage -1))
                if monster.alive:
                    self.stats[4] -= reflected_damage
        if "Blast" in self.abilities:
            if next_monster:
                self.attack_standard(self,next_monster,max(1,round(self.damage*0.6,0)))
            if previous_monster:
                self.attack_standard(self,previous_monster,max(1,round(self.damage*0.6,0)))
        if self.stats[4] <= 0:
            self.alive = False
        if monster.stats[4] <= 0:
            monster.alive = False
            if "Trample" in self.abilities and self.alive:
                if next_monster:
                    self.attack_standard(self,next_monster)
                    if next_monster.stats[4] <= 0:
                        next_monster.alive = False

        if previous_monster:
            previous_monster.alive = previous_monster.stats[4] > 0
        if next_monster:
            next_monster.alive = next_monster.stats[4] > 0

        monster.alive = monster.stats[4] > 0
        self.alive = self.stats[4] > 0
        return True

