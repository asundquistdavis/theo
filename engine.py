from typing import Any, List, Dict, Callable, Iterable
from itertools import chain


class Item:
    '''Basic data structure in game.'''

class Collection:
    '''Collection of Item-like or other Collection-like objects. Forms an algebra on Items and Collections.'''

class Transaction:
    '''Used to exchange items between collections.'''

class Action:
    '''Used to perform set of transactions that define a single player action.'''

class Player:
    '''object hold all information for a unique player entity.'''

class IO:
    '''Object that determine how inputs and outputs are handle per player.'''

class Game:
    '''Engine that runs the game.'''

class State:
    '''Holds game state information'''

    class Phase:
        '''Specicifies which actions can be made at a given time'''

class Settings:
    '''Holds game settings.'''

    class Transactions:
        '''Settings specific to transactions.'''

    class Actions:
        '''Settings specific to actions.'''

    class IOs:
        '''Settings specific to IOs.'''

    class Player:
        '''Settings specific to a single player.'''

class Verbose_string:
    ''''''

class Packet:
    '''Contains info to print, '''

class Item:

    def __init__(self, name) -> None:
        self.name = name

    def __repr__(self):
        return f'<{type(self)}: {self.name}>'
    
    def __eq__(self, other):
        assert type(self) == type(other)
        return self.name == other.name

class Collection:
    
    def __init__(self, *items_i:Item or 'Collection', items_l:List[Item or 'Collection']=[]):
        self.items = list(items_l) if items_l else list(items_i) if items_i else []
        self.items = list(item for item in self.items if item)

    def __iter__(self):
        return (item for item in self.items)
    
    def __repr__(self):
        return f'{type(self)}: {str(self.items)}'
    
    def __add__(self, other):
        if issubclass(type(other), Item, Collection):
            return type(self)(*self.items, other)
    
    def __iadd__(self, other):
        if issubclass(type(other), (Item, Collection)):
            self.items.append(other)
        if type(other) == list:
            self.items += other
        return self

    def __sub__(self, other):
        if issubclass(type(other), list):
            type(self)(*(item for other_item in other for item in self.items if other_item!=item))

    def __isub__(self, other):
        if issubclass(type(other), (Item, Collection)):
            self.items.remove(other)
        return self
    
    def __imul__(self, other):
        if issubclass(type(other), Collection):
            return self.__class__(*self.items, *other.items)
        elif issubclass(type(other), Item):
            return self.__class__(*self.items, other)
        
    def __len__(self):
        return len(self.items)
    
    def has(self, value:Any, method:Callable=None)->bool:
        return any(item for item in self.items if method(item) == value)
    

class Action:

    def __init__(self) -> None:
        ...

    def sub(self:Action)->Iterable[Action]:
        """returns all actions from parent"""
        ...

    def play(self)->None:
        """Permforms action"""

class Player:

    inc = 0

    def __init__(self, game:'Game', name:str=None, type:str=None):
        self.game:Game = game
        self.name = name if name else f'player: {Player.inc}'
        self.type = type
        # self.io = IO(self.game.settings.ios[type])
        Player.inc += 1

    def choose_action(self, actions:List[Action])->Action:
        '''select action from list'''
        ...

    def play_action(self):
        '''select action/sub-action until no further sub and play action'''
        actions:List[Action] = self.game.available_actions(self)
        action = self.choose_action(actions)
        action.play()

    def play_turn(self):
        '''plays actions until '''
        self.is_turn = True
        while self.is_turn:
            self.play_action()
    
    def __repr__(self) -> str:
        return f'<player: {self.name} ({self.type})>'


class Transaction:

    def __init__(self, text:str, source:Collection, method:Callable, target:Collection, **method_args):
        self.text:str = text
        self.source:Collection = source
        self.method:callable = method
        self.target:Collection = target
        self.method_args = method_args

    def __call__(self)->Collection or Item:
        method = self.method
        object:Item or Collection[Item] = method(self.source, **self.method_args)
        self.target += object
        return object

class IO:

    def __init__(self, type:str='console'):
        self.type = type
        if self.type == 'console':
            self.log = self.log_to_console
            self.choose = self.choose_in_console

    def log_to_console(self, message:str):
        print(message)
    
    def choose_in_console(self, choices:List[Action]):
        self.log('choices:')
        tuple(self.log(f'({index}) {choice.text}') for index, choice in enumerate(choices))
        raw_choice = input('enter int for selection: ')
        try:
            return choices[int(raw_choice)]
        except:
            self.log('invalid choice. try again')
            self.choose(choices)

class State:
    
    def __init__(self, phases:List[State.Phase], start:State.Phase=None ) -> None:
        self.turn:int = 0
        self.phases:List[State.Phase] = phases
        self.phase:State.Phase = start if start else self.phases[0]
        self.is_playing:bool = True
        self.active_player:Player or None = None

    class Phase:

        def __init__(self, name:str, actions:List[Action]=[]) -> None:
            self.name:str = name
            self._actions:List[Action] = actions

        def actions(self, **kwargs)->Iterable[Action]:
            for action in self._actions:
                yield action(**kwargs)

        def __eq__(self, __value: object) -> bool:
            assert type(__value) == type(self)
            return __value.name == self.name
        
        def __repr__(self) -> str:
            return f'<{type(self)}: {self.name}>'


class Game:

    player_type = Player
    
    # phases ['draw', 'meld', '']
    # available_action {'start_of_turn': List[Action], }

    def __init__(self, **kwargs):
        self.settings:Settings = Settings(**kwargs)
        self.players:List[Player] = []
        self.state:State = State([Settings.NULL_PHASE])

    def add_player(self, name=None, type=None)->Game:
        player = self.player_type(self, name, type)
        self.players.append(player)
        return self

    def next_state(self):
        '''mutates self.state to next state'''
        ...

    def available_actions(self, player:Player)->Iterable[Action]:
        '''returns available actions'''
        phase_actions = self.state.phase.actions(game=self, player=player)
        return [action for action in chain(action.sub() for action in phase_actions) if action]

    def play(self):
        while self.state.is_playing:
            self.state.active_player.play_turn()
            self.next_state()


class Settings:

    NULL_PHASE = State.Phase('null', [])

    def __init__(self, **kwargs) -> None:
        self.actions = Settings.Actions(**kwargs)
        self.ios = Settings.IOs(**kwargs)
        self.transactions = Settings.Transactions(**kwargs)
        self.states = Settings.States(**kwargs)

    class IOs:        

        def __init__(self, human_ios=None, ai_ios=None, io_type=None, **_) -> None:
            if io_type:
                if io_type=='default':
                    self.human_ios =  self.human_ios = 'console'
            else:
                self.human_ios = human_ios if human_ios else 'console'
                self.ai_ios = ai_ios if ai_ios else 'console'
            self.types = {'human': self.human_ios, 'ai': self.ai_ios}
            self.errors = {}

    class Transactions:
        ...
        
    class Actions:
        ...

    class States:

        def __init__(self, phases:List[State.Phase]=..., **_) -> None:
            self.phases = phases

class Packet:
    ...
        
class GameTrial(Game):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class PlayerTrial(Player):

    def __init__(self, game: Game, name: str = None, type: str = None):
        super().__init__(game, name, type)

if __name__=='__main__': 
    item = Item(name='mouse', curviture=3.5, speed='off the charts')
    collection = Collection(item)
    collection *= item
    print(collection)


'''

---- stubs ----

Game
    players: List[Player]
    turn: int
    active_player: Player
    phase: str
    actions: dict[str, List[Action]]

    next_turn(self):
        order = self.turn%len(self.players)
        self.active_player  = players[order]

    play(self):
        while self.playing:
            self.active_player.play_turn()
            self.next_turn()

Player
    io:IO

    play_turn(self):
        while self.playing:
            self.play_action()

    play_action(self):
        phase = self.game.phase
        actions = self.game.actions[phase]
        action = self.io.choose(actions)
        sub_actions = action.sub()
        while sub_actions:
            subaction = self.io.choose(sub_action)
            sub_actions = sub_action.sub()
        

IO

    choose(self, choices: List[Action])->Action:
        #implementation depends on io init - can go to console, ai or server

'''