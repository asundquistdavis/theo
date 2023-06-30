from typing import Any, Optional, Sequence, Type, Union, Iterable
import numpy as np
from engine import Action
from gym import Env
from gym.spaces import Space
import random as r

class Observation(list):
    '''(phase,
        )'''
    ...

class GameActionSpace(Space):

    def __init__(self, actions)->None:
        self.actions = actions

    def contains(self, x) -> bool:
        return x in self.actions
    
    def sample(self, mask = None) -> Any:
        return r.choice(self.actions)
    
    def size(self):
        return (len(self.actions),)

class GameEnv(Env):

    def __init__(self) -> None:
        # enviroment space
        self.observation_space = ...
        
    @property
    def action_space(self): return ...

    def step(self, action)->Observation:
        ...

    def render(self)->None:
        ...

    def reset(self)->Action:
        ...