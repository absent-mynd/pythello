import json
from pythello import BLACK, WHITE, INVERSE_COLOR
 
class PythelloStats:
    
    def __init__(self):       
        # Opening JSON file
        f = open('data.json')
        
        # returns JSON object as
        # a dictionary
        self.data = json.load(f)
        self.filename = "data.json"
        
        # Closing file
        f.close()
        
    def update_data(self):
        f = open('data.json')
        self.data = json.load(f)
        f.close()
        
    def add_agent_to_stats(self, agent):
        self.update_data()
        d = self.data
        if agent in d:
            return
        d[agent] = {}
        for other_agent in d.keys():
            d[agent][other_agent] = {
                "wins" : 0,
                "winsB" : 0,
                "winsW" : 0,
                "losses": 0,
                "lossesB": 0,
                "lossesW": 0,
                "ties": 0,
                "tiesB": 0,
                "tiesW": 0,
                "total": 0,
                "winpct" : 0,
                "winpctB": 0,
                "losepct": 0,
                "losepctW": 0,
                "losepctB": 0,
                "tiepct": 0,
                "tiepctW": 0,
                "winpctW": 0,
                "tiepctB": 0
            }
            d[other_agent][agent] = {
                "wins" : 0,
                "winsB" : 0,
                "winsW" : 0,
                "losses": 0,
                "lossesB": 0,
                "lossesW": 0,
                "ties": 0,
                "tiesB": 0,
                "tiesW": 0,
                "total": 0,
                "winpct": 0,
                "winpctB": 0,
                "losepct": 0,
                "losepctW": 0,
                "losepctB": 0,
                "tiepct": 0,
                "tiepctW": 0,
                "winpctW": 0,
                "tiepctB": 0
            }
        f = open(self.filename, 'w')
        json.dump(self.data, f, indent=4)
        f.close()
            
    def update_percentages(self, agent_data, color):
        agent_data["winpct"] = int(100 * agent_data["wins"]/agent_data["total"])
        agent_data["losepct"] = int(100 * agent_data["losses"]/agent_data["total"])
        agent_data["tiepct"] = int(100 * agent_data["ties"]/agent_data["total"])
        
        if color is BLACK:
            agent_data["winpctB"] = int(100 * agent_data["winsB"]/(agent_data["tiesB"] + agent_data["lossesB"] + agent_data["winsB"]))
            agent_data["losepctB"] = int(100 *agent_data["lossesB"]/(agent_data["tiesB"] + agent_data["lossesB"] + agent_data["winsB"]))
            agent_data["tiepctB"] = int(100 *agent_data["tiesB"]/(agent_data["tiesB"] + agent_data["lossesB"] + agent_data["winsB"]))
        else:
            agent_data["winpctW"] = int(100 *agent_data["winsW"]/(agent_data["tiesW"] + agent_data["lossesW"] + agent_data["winsW"]))
            agent_data["losepctW"] = int(100 *agent_data["lossesW"]/(agent_data["tiesW"] + agent_data["lossesW"] + agent_data["winsW"]))
            agent_data["tiepctW"] = int(100 *agent_data["tiesW"]/(agent_data["tiesW"] + agent_data["lossesW"] + agent_data["winsW"]))
            
    def update_stat_win(self, winner_str, loser_str, winner_color):
        self.update_data()
        winner = self.data[winner_str][loser_str]
        loser = self.data[loser_str][winner_str]
        winner["total"] += 1
        loser["total"] += 1
        
        winner["wins"] += 1
        loser["losses"] += 1
        
        if winner_color is BLACK:
            winner["winsB"] += 1
            loser["lossesW"] += 1
        else:
            winner["winsW"] += 1
            loser["lossesB"] += 1
            
        self.update_percentages(winner, winner_color)
        self.update_percentages(loser, INVERSE_COLOR[winner_color])
        
        f = open(self.filename, 'w')
        json.dump(self.data, f, indent=4)
        f.close()
         
    def update_stat_tie(self, agent1_str, agent2_str, agent1_color):
        self.update_data()
        agent1 = self.data[agent1_str][agent2_str]
        agent2 = self.data[agent2_str][agent1_str]
        agent1["total"] += 1
        agent2["total"] += 1
        
        agent1["ties"] += 1
        agent2["ties"] += 1
        if agent1_color is BLACK:
            agent1["tiesB"] += 1
            agent2["tiesW"] += 1
        else:
            agent1["tiesW"] += 1
            agent2["tiesB"] += 1    
            
        self.update_percentages(agent1, agent1_color)
        self.update_percentages(agent2, INVERSE_COLOR[agent1_color])
        
        f = open(self.filename, 'w')
        json.dump(self.data, f, indent=4)
        f.close()
        
    