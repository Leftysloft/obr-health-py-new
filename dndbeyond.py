from math import floor
import requests

class DnDBeyond:      
    STATS = (
        "strength",
        "dexterity",
        "constitution",
        "intelligence",
        "wisdom",
        "charisma"
    )

    @staticmethod
    def score_to_mod(score):
        return floor((score - 10) / 2)
    
    def __init__(self, character_id):
        self.character_id = character_id
        self.character_data = self.get_character_data()
        self.character_image = self.character_data.get("decorations", {}).get("avatarUrl", "")[:-51]
        #print(self.character_url)

    def update(self):
        self.character_data = self.get_character_data()
        
    def get_character_data(self):
        req = requests.get(f"https://character-service.dndbeyond.com/character/v5/character/{self.character_id}")
        #print("hello")
        if req.status_code != 200:
            return None
        try:
            j = req.json()
            if not "success" in j or not "data" in j:
                return None
            return j["data"]

        except ValueError:
            return None

    def get_character_scores(self, score=None):
        base_scores = {}
        for base_score in map(lambda stat: {self.STATS[stat["id"]-1]: stat["value"]}, self.character_data["stats"]):
            base_scores.update(base_score)
            #print("base scores", base_scores)
        bonuses = {}
        for bonus_stat in self.character_data["bonusStats"]:
            bonuses[self.STATS[bonus_stat["id"]-1]] = bonus_stat["value"] if bonus_stat["value"] is not None else 0
            #print("bonuses", bonuses)
        for modifier_list in self.character_data["modifiers"].values():
            for modifier in modifier_list:
                if modifier["subType"].endswith("-score"):
                    ability_score = modifier["subType"].split("-")[0]
                    if ability_score not in self.STATS:
                        continue
                    value = modifier["value"]
                    if modifier["type"] == "bonus" and value is not None:
                        bonuses[ability_score] += value
                    elif modifier["type"] == "set":
                        base_scores[ability_score] = value
        total_scores = {
            ability: score + bonuses[ability] for ability, score in base_scores.items()
        }
        #print("total scores", total_scores)
        return total_scores if score is None else total_scores[score]

    def get_character_level(self):
        return sum(c["level"] for c in self.character_data["classes"])
                
    def get_character_strength(self):
        return sum(c["strength"] for c in self.character_data["prerequisites"])
   
    def get_character_hp(self):
            constitution_mod = self.score_to_mod(self.get_character_scores("constitution"))
            #print(constitution_mod)
            
            for modifier_list in self.character_data["modifiers"].values():
                for modifier in modifier_list:
                    if modifier["subType"] == "hit-points-per-level":
                        if modifier["type"] == "bonus":
                            constitution_mod += modifier["value"]
                    #print (self.character_data["modifiers"].values())
            
            added_hp = constitution_mod * self.get_character_level()
            override_hit_points = self.character_data["overrideHitPoints"]
            max_hp = self.character_data["baseHitPoints"] + added_hp if override_hit_points is None else override_hit_points
            #print("added", added_hp)
            #print("override", override_hit_points)
            #print("max", max_hp)
            #print("dndbpy", self.character_id)
            return {
                "max": max_hp,
                "current": max_hp - self.character_data["removedHitPoints"],
                "temp": self.character_data["temporaryHitPoints"],
                "image": self.character_image,
                "char_id": self.character_id
            }
    
    