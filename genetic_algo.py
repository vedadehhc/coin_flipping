from dataclasses import dataclass
from enum import Enum
import math
from random import randint, random, seed
import numpy as np

class Flipper:
    def __init__(self, cheater: bool):
        self.cheater = cheater
    
    def prob_heads(self):
        return 0.75 if self.cheater else 0.5

    def flip(self) -> int:
        f = random()
        return (random() < self.prob_heads())

@dataclass
class Observation:
    heads: int
    tails: int
    
    def __hash__(self):
        return (self.heads << 10) + self.tails

WAIT = 0
PARDON = 1
ACCUSE = 2

class Agent:
    MAX_FLIP = 10
    def __init__(self, file=None, initialize=True):
        self.score = 0
        
        if file is None:
            self.policy = np.zeros((self.MAX_FLIP, self.MAX_FLIP), np.uint8)
            
            if initialize:
                for h in range(self.MAX_FLIP):
                    for t in range(self.MAX_FLIP):
                        self.policy[h,t] = randint(0, 2)
                self.policy[0, 0] = 0
        else:
            self.policy = np.load(file)
    
    def save(self, file):
        np.save(file, self.policy)

    def observe(self, heads: int, tails: int) -> int:
        if heads >= self.MAX_FLIP:
            sub = self.observe(self.MAX_FLIP - 1, tails)
            if sub == WAIT: return ACCUSE
            return sub
        
        if tails >= self.MAX_FLIP:
            sub = self.observe(heads, self.MAX_FLIP - 1)
            if sub == WAIT: return PARDON
            return sub
        
        return self.policy[heads, tails]

    def check(self, flipper: Flipper):
        h = 0
        t = 0
        action = WAIT
        while action == WAIT:
            self.score -= 1
            flip = flipper.flip()
            h += flip
            t += 1 - flip
            action = self.observe(h, t)
        
        # check if we were correct
        if action == ACCUSE:
            if flipper.cheater: self.score += 15
            else: self.score -= 30
        elif action == PARDON:
            if flipper.cheater: self.score -= 30
            else: self.score += 15
        else:
            print("ERROR")
            exit()

    def breed(a, b, mutation_rate=0.05):
        c = Agent(initialize=False)
        for i in range(c.MAX_FLIP):
            for j in range(c.MAX_FLIP):
                r = random()
                if r < mutation_rate:
                    c.policy[i,j] = math.floor(3 * r / mutation_rate)
                else:
                    c.policy[i,j] = a.policy[i,j] if r < (0.5+ (mutation_rate/2)) else b.policy[i,j]
        c.policy[0,0] = 0
        return c

def save_all(agents: list[Agent], dir):
    for i, a in enumerate(agents):
        a.save(f"./coin_flipping_data/{dir}/agent-{i}.npy")

def genetic_algorithm():
    m = 1000 # num flippers
    flippers = [Flipper(2*i < m) for i in range(m)]
    
    n = 1000 # num agents
    top = 10
    agents = [Agent() for i in range(n)]


    EPOCHS = 1000
    SEED = 10
    SAVE_RATE = 10

    dir = "fully-random-m5"
    max_scores = np.zeros((EPOCHS))

    print("Init Complete\n")

    for en in range(EPOCHS):

        for i in range(n):
            agents[i].score = 0
            # seed(SEED)
            for j in range(m):
                agents[i].check(flippers[j])
        
        agents.sort(key=lambda a: a.score, reverse=True)
        max_score = agents[0].score
        max_scores[en] = max_score

        # todo: breed
        k = top
        while k < n:
            for i in range(top):
                for j in range(i+1, top):
                    agents[k] = agents[i].breed(agents[j])
                    k += 1
                    if k >= n: break
                else:
                    continue
                break
        
        print(f"EPOCH {en+1} / {EPOCHS} completed")
        print("Max Score:", max_score, agents[0].score)

        if en % SAVE_RATE == 0:
            save_all(agents, dir)
            np.save(f"./coin_flipping_data/{dir}/scores.npy", max_scores)
            print("Saved all agents and scores!")

        print()
    
    save_all(agents)