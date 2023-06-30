import random as r
from datetime import datetime as dt
from typing import Union

class Item:
    """Fundamental unit of data"""
    ...

class Card:
    """
    Cards are items that can be shuffled, dealt in a collection
    """
    ...

class Collection:
    """
    An iterable of items with methodsfor finding\n mathcing items and for reducing under an operation.
    """
    ...

class Collection_Of_Cards:
    """
    Extends a Collections with methods for shuffling and dealing cards.
    """
    ...

class Game:
    """
    High level engine that controls turns, plays and scores.
    """
    ...

class Rules:
    """
    Set of parameters that determine how the game is played.
    """
    ...

class Action:
    """
    Basic actions performed by players.
    """
    ...

class Interface:
    """
    Handles inputs and outputs.
    """
    ...

class Player:
    """
    Unique entity for a user in a single game.
    """
    ...

class Packet:
    """
    Fundamental unit of information
    """
    ...


class Item:

    def __init__(self, collection:Collection, type='none', pv=0) -> None:
        self.collection:Collection = collection
        self.type = type
        self.pv = pv # pricipal value

    def __repr__(self) -> str:
        return self.type

class Card(Item):

    def __init__(self, collection, name) -> None:
        self.name = name
        super().__init__(collection,'card', 0)

    def __repr__(self) -> str:
        return f'card: {self.name}'

class Collection(list):

    ref = 'collection'

    def EMPTY(owner):
        """Initializes an empty collection"""
        return Collection(owner)

    def __init__(self, owner, alt_ref='') -> None:
        self.owner:Union[Game, Player] = owner
        self.alt_ref = alt_ref

    def __repr__(self) -> str:
        ref = self.alt_ref if self.alt_ref != '' else self.ref
        owner = self.owner
        return f'{ref} for {owner}'
    
    @property
    def list(self) -> list:
        """Returns a list of items in the collection"""
        return [item for item in self]
    
    def create_item(self, type='none', pv=0):
        """Creates a new Item and appends it to the end of the collection"""
        item = Item(self, type, pv)
        transaction(item, self, False)
        return item

    def get(self, type):
        """yeilds an iterable of all items in the collection that match the given type"""
        yield (item for item in self if item.type == type)
    
    def reduce(self, type, operation=lambda item: item.pv):
        """Returns the inner product of the subset of items with a given type and the 'operation'. By deafault the operation is to access the principal value of the item."""
        return sum(operation(item) for item in self if item.type == type)

class Collection_Of_Cards(Collection):

    def EMPTY(owner):
        """Initializes an empty collection"""
        return Collection_Of_Cards(owner)

    def __init__(self, owner, alt_ref='') -> None:
        super().__init__(owner, alt_ref)

    @property
    def length(self) -> int:
        """Returns the number of cards in the collection."""
        return len(self)
    
    def create_card(self, name):
        """Creates a new Card/Item and appends it to the end of the collection"""
        card = Card(self, name)
        transaction(card, self, False)
        return card

    def shuffle(self) -> Packet:
        """Randomly shuffles all cards in collection."""
        r.shuffle(self)
        return ...

    def draw(self) -> Card:
        """Returns the first card in the collection."""
        return self[0]

    def deal(self, number_of_cards:int=1) -> list:
        """"Partitions the collection of cards into sets of length 'number_of_cards'"""
        number_of_partitions = -(-self.length//number_of_cards) # round up
        partitions = [[] for i in range(number_of_partitions)] # init list of empty list
        for number, card in enumerate(self):
            partition_number = number % number_of_partitions 
            partitions[partition_number].append(card)
        return partitions
    
def transaction(item:Item, target:Collection, remove_from_source:bool=True)->Item:
    """
    Moves an item from one collection to another.
    """
    source:Collection = item.collection
    if remove_from_source:
        source.remove(item)
    target.append(item)
    item.collection = target
    return item
    
class Game:

    _PLACEHOLDER = ... # Stores placeholder game

    @property
    def PLACEHOLDER():
        if Game._PLACEHOLDER != ...:
            return Game._PLACEHOLDER
        return Game()
    
    def __call__(self):
        self.rules.start()

    def __init__(self, rules:Rules=None) -> None:
        self.players:list[Player] = []
        self.actions:list[Action] = []
        self.turn_number:int = 0
        self.current_player = None
        self.current_action = None
        self.start_time:dt = None
        self.reference:str = 'game'
        self.rules:Rules = rules
        self.state:tuple[int, str] = 0, 'new game'
        self.interface:Interface = Interface(self)

    def __repr__(self) -> str:
        reference = self.reference
        time_info = f'started at {self.start_time.strftime("%H:%M:%S")} on {self.start_time.strftime("%D")}' if self.start_time else 'not started'
        players_info = 'with ' +  ', '.join(str(player) for player in self.players[:-1]) + ' and ' + str(self.players[-1]) if self.players else 'with no one'
        return f'{reference}: {time_info} {players_info}.'
    
    def add_player(self, name) -> Packet:
        """Create new player and adds them to game. Returns 'palyer added'."""
        player = Player(self, name)
        self.players.append(player)
        return Packet(self, 'player added', f'{player} added to {self}')
    
    def start(self) -> Packet:
        """Starts the game."""
        self.start_time = dt.utcnow()
        return Packet(self, 'game started', f'{self}')
    
    def prompt_action(self, player:Player) -> Packet:
        """Populates possible actions for given player. Returns a packet with actions."""
        available_actions = [(action, parameters) for action in self.rules.actions for parameters in action.parameters_space(self, player) if action.valid(parameters)]
        player.available_actions = available_actions
        packet = Packet(self, 'available actions')
        return ...

    def play_action(self, player:Player, action:Action) -> Packet:
        """Declares selected action. Returns a packet with declaration."""
        packet = action(player)
        return packet
    
    @property
    def CONSOLE1V1(self):
        start_packets = (
            Packet(self, 'new game', 'welcome to your new game. please enter first player name:', prompt=True, prompt_type='text')
        )
        return Rules(self, start_packets=start_packets)
    
class Mode:

    def __init__(self, num_human_players=1, num_ai_players=1, human_players_io='console', ai_players_default_strat=AI.game.DEFAULT) -> None:
        self.num_human_players = num_human_players
        self.num_ai_players = num_ai_players
        self.human_players_io = None 
        self.ai_players_default_strat = None

    def __repr__(self) -> str:
        pass

class Rules:

    def __init__(self, game, start_packets=None) -> None:
        self.game:Game = game
        self.reference = 'rules'
        self.actions = [Action]
        self.local_rules = None
        self.start_packets:tuple[Packet] = start_packets

    def __repr__(self) -> str:
        return f'{self.reference} for {str(self.game)}'
    
    def start(self):
        (self.game.interface(packet) for packet in self.start_packets)

class Action:

    parameters_space = lambda game, player: (player),
    valid = lambda parameters: True
    describe = 'default action'

    def __init__(self, type:str='default') -> None:
        self.type = type


    def __call__(self, game:Game, player:Player) -> Packet:
        """"""
        return Packet(game, 'action', self.describe)

class Interface:

    def __init__(self, game) -> None:
        self.game:Game = game
        self.log_type:str = self.game.rules.log_type

    def __call__(self, packet:Packet):
        p = packet.prompt
        lt = self.log_type

    def log_console(self, packet:Packet, verbosity=0):
        """Logs a packet to the console."""
        ...

    def prompt_console(self, packet:Packet, verbosity=0):
        try:
            response = int(input(packet.message))
        except:
            return self.prompt_console(packet, verbosity)
        return response

class Player:
    
    def __init__(self, game:Game, name:str) -> None:
        self.game:Game = game
        self.name:str = name
        self.score:int = 0
        self.local_rules:Rules = game.rules.local_rules
        self.inventory:Collection = Collection.EMPTY(self)
        self.hand:Collection_Of_Cards = Collection_Of_Cards.EMPTY(self)
        self.available_actions = []

    def __repr__(self) -> str:
        return self.name

class Packet:

    ref = 'packet'

    def __init__(self, game, message_type:str, message:str= 'none', source:Collection=None, target:Collection=None, item:Item=None, prompt=False, prompt_type='select') -> None:
        self.game:Game = game
        self.message_type:str = message_type
        self.time = dt.utcnow()
        self.message:str = message
        self.source:Collection = source
        self.target:Collection = target
        self.item:Item = item
        self.prompt:bool = prompt
        self.prompt_type:str = prompt_type

    def __repr__(self) -> str:
        ref = self.ref
        time = self.time.strftime('%H:%M:%S')
        date = self.time.strftime('%D')
        return f'{ref}: {self.message_type} at {time} on {date}.'

class AI:

    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        pass

    class Games:

        instances = []

        def __init__(self) -> None:
            AI.Games.instances.append(self)

        def __repr__(self) -> str:
            pass

        class AIS:

            def __init__(self) -> None:
                pass

            def __repr__(self) -> str:
                pass

    @property
    def game(slef):
        return 
