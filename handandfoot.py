from typing import Iterable, List, Tuple
from itertools import chain
from engine import Action, Packet, Transaction, Collection, Item, Settings, Game, Player, State
from collections import Counter
from random import shuffle

Phase = State.Phase

# The following HandAndFoot classes inherit from the game engine defined classes such as Item, Collection and Action.

class DrawHandAndFoot:
    ''''''

class PickUpHandAndFoot:
    ''''''

class MakeMeldHandAndFoot:
    ''''''

class DiscardHandAndFoot:
    ''''''

class PlayerHandAndFoot:
    ''''''

class SettingsHandAndFoot:
    ''''''

class GameHandAndFoot:
    ''''''

class PlayerHandAndFoot(Player):

    def __init__(self, game, name, type) -> None:
        self.hand = HandHandAndFoot()
        self.melds = SetOfMeldHandAndFoot()
        super().__init__(game, name, type)

    def available_adds(self, meld:'MeldHandAndFoot'=None):
        melds = self.melds
        hand = self.hand
        if not (meld is None):
            rank = meld.rank
            def generator(meld_wilds=True):
                possible_cards = hand.of_rank(rank)
                wilds_in_hand = hand.wilds()
                naturals_added:List[CardHandAndFoot] = []
                wilds_added:List[CardHandAndFoot] = []
                check_wild = meld_wilds
                while possible_cards or check_wild:
                    wilds_in_meld = meld.wilds() + wilds_added
                    tree_meld = meld.cards + wilds_added + naturals_added
                    full_meld_length = len(tree_meld)
                    can_add_wild = bool(max(min((full_meld_length-len(wilds_in_meld))//2-len(wilds_in_meld), len(wilds_in_hand)), 0)) and meld_wilds
                    # print('---')
                    # print(full_meld_length//3-len(wilds_in_meld))
                    # print(len(wilds_in_hand))
                    # print(max(min(full_meld_length//3-len(wilds_in_meld), len(wilds_in_hand)-len(wilds_added)), 0))
                    if can_add_wild: 
                        wilds_added.append(wilds_in_hand.pop())
                        check_wild = False
                        if len(meld.cards + naturals_added + wilds_added) > 7: return
                        yield MeldHandAndFoot(rank, *meld.cards, *naturals_added, *wilds_added)
                    else:
                        if possible_cards:
                            naturals_added.append(possible_cards.pop())
                            check_wild = True
                            if len(meld.cards + naturals_added + wilds_added) > 7: return
                            yield MeldHandAndFoot(rank, *meld.cards, *naturals_added, *wilds_added)
                        else:
                            check_wild = False
            wilds_in_hand = hand.wilds()
            return chain(generator(meld_wilds=False), generator()) if wilds_in_hand else generator(False)
        return tuple(tuple(self.available_adds(meld=meld)) for meld in melds)


    def available_melds(self, pickup:'CardHandAndFoot' or None=None, rank:int=None, dirty=True)->Tuple['MeldHandAndFoot']:
        cards = CollectionOfCardsHandAndFoot(*self.hand.items, pickup) if pickup else self.hand
        melds = []
        if not rank is None:
            if rank == 3: return []
            rank = 0 if rank == 2 else rank
            has_meld = self.melds.has(rank, MeldHandAndFoot.call_rank)
            if has_meld:
                return []
            wilds = cards.wilds()
            number_to_meld = 3
            if rank == 0:
                if len(wilds) >= number_to_meld:
                    cards_to_meld = wilds[:number_to_meld]
                    return (MeldHandAndFoot(0, *cards_to_meld),)
                else: return []
            cards_of_rank = cards.of_rank(rank)
            if len(cards_of_rank) >= number_to_meld:
                melds.append(MeldHandAndFoot(rank, *cards_of_rank[:number_to_meld]))
            if not (rank == 7) and dirty:
                number_of_usable_wilds = min(number_to_meld//3, len(wilds))
                usable_wilds = wilds[:number_of_usable_wilds]
                if number_of_usable_wilds > 0 and (len(cards_of_rank) + number_of_usable_wilds >= number_to_meld):
                    meldable_cards = cards_of_rank[:number_to_meld-number_of_usable_wilds] + usable_wilds
                    melds.append(MeldHandAndFoot(rank, *meldable_cards[:number_to_meld]))
            return melds
        if pickup:
            return tuple(meld for meld in (self.available_melds(pickup, pickup.rank, dirty=False))) 
        return tuple(meld for melds_of_rank in (self.available_melds(pickup, rank) for rank in cards.ranks()) for meld in melds_of_rank)
    
class GameHandAndFoot(Game):

    player_type = PlayerHandAndFoot

    def __init__(self):
        self.deck = DeckHandAndFoot.build_deck()
        self.pile = PileHandAndFoot()
        super().__init__()


# Classes that extend Item:
class CardHandAndFoot(Item):

    RANK_MAP =  {0: 'joker', 1: 'ace', 11: 'jack', 12: 'queen', 13: 'king'}
    
    def __init__(self, rank:int, suit:str) -> None:
        self.rank = rank
        self.rank_name = CardHandAndFoot.RANK_MAP[self.rank] if self.rank in CardHandAndFoot.RANK_MAP.keys() else self.rank
        self.suit = suit
        name = f'{self.rank_name} of {self.suit}' 
        super().__init__(name)

    def __repr__(self): return f'card: {self.name}'

# Classes that extend Collection:
class CollectionOfCardsHandAndFoot(Collection):

    def __init__(self, *cards_i:CardHandAndFoot, cards_l:List[CardHandAndFoot]=[]):
        super().__init__(*cards_i, items_l = cards_l)
        self.cards:List[CardHandAndFoot] = self.items

    def of_rank(self, rank): return [card for card in self.cards if card.rank == rank]
    
    def wilds(self): return self.of_rank(0) + self.of_rank(2)
    
    def ranks(self): '''returns number of cards at each rank'''; return set(card.rank for card in self.cards)

    def shuffle(self)->None: shuffle(self.cards)

    def draw(self)->CardHandAndFoot: return self.items.pop(0)

    def get_sorted(self):
        return sorted(self.cards, key=lambda card: card.rank)  
    
class DeckHandAndFoot(CollectionOfCardsHandAndFoot):

    RANKS = range(13)
    SUITS = ['hearts', 'diamonds', 'spades', 'clubs']

    def build_deck(number_of_jokers=2, number_of_repeats=4)->'DeckHandAndFoot':
        cards = ([CardHandAndFoot(rank+1, suit) for suit in DeckHandAndFoot.SUITS for rank in DeckHandAndFoot.RANKS] + [CardHandAndFoot(0, 'wild')] * number_of_jokers) * number_of_repeats
        return DeckHandAndFoot(*cards)

    def __init__(self, *cards_i: CardHandAndFoot, cards_l: List[CardHandAndFoot] = []):
        super().__init__(*cards_i, cards_l=cards_l)

    def deal(self, number_of_cards=13):
        cards = self.cards[0:number_of_cards]
        return cards
    
class HandHandAndFoot(CollectionOfCardsHandAndFoot):

    def __init__(self, *cards_i: CardHandAndFoot, cards_l: List[CardHandAndFoot] = []):
        super().__init__(*cards_i, cards_l=cards_l)

    def make_meld(self, meld:'MeldHandAndFoot'):
        tuple(self.cards.remove(card) for card in meld.cards)
        return meld
    
class MeldHandAndFoot(CollectionOfCardsHandAndFoot):

    def __init__(self, rank, *cards_i: CardHandAndFoot, cards_l: List[CardHandAndFoot] = []):
        self.rank = rank
        super().__init__(*cards_i, cards_l=cards_l)

    def call_rank(self):
        return self.rank

    def __repr__(self):
        wilds = len(self.wilds())
        naturals = len(self) - wilds
        return f'meld: {self.rank} - {naturals}/{wilds}'

class SetOfMeldHandAndFoot(Collection):

    def __init__(self, *melds_i: Item, melds_l: List[Item] = []):
        super().__init__(*melds_i, items_l=melds_l)
        self.melds:Iterable[MeldHandAndFoot] = self.items

    def length_of_rank(self, rank)->int: return max((len(meld) for meld in self.melds if meld.rank == rank), default=0)

class PileHandAndFoot(CollectionOfCardsHandAndFoot):

    def __init__(self, *cards_i: CardHandAndFoot, cards_l: List[CardHandAndFoot] = []):
        super().__init__(*cards_i, cards_l=cards_l)

    def pickup(self):
        set = Collection()


# Classes that extend Action:
# These classes controll the HandAndFoot specific actions that a palyer (or the game) can take

# deals hands and feet to players
class DealHandAndFoot(Action):
    ...

# draw from the HandAndFoot deck is the basic draw
class DrawHandAndFoot(Action):

    def __init__(self, game:GameHandAndFoot, player:PlayerHandAndFoot) -> None:
        self.game = game
        self.player = player
        deck = game.deck
        draw = DeckHandAndFoot.draw
        hand = player.hand
        self.transaciton = Transaction('draw', deck, draw, hand)

    def sub(self):
        return self

    def run(self):
        return self.transaciton()

    def __repr__(self) -> str: return '<draw from deck>'

class PickUpHandAndFoot(Action):
    
    def __init__(self, game:GameHandAndFoot, player:PlayerHandAndFoot, meld:MeldHandAndFoot=None) -> None:
        self.game = game
        self.player = player
        self.pile = game.pile
        self.pickup = self.pile.pickup
        self.hand = player.hand
        self.meld = meld
        self.transaction = Transaction('pickup', self.pile, self.pickup, self.hand)

    def sub(self)->Iterable[Action]:
        if not self.pile: return None
        pickup:CardHandAndFoot  = self.pile.items[-1]
        return [PickUpHandAndFoot(self.game, self.player, meld=meld) for meld in self.player.available_melds(pickup)]

    def play(self) -> None:
        self.transaction()
        MakeMeldHandAndFoot(self.game, self.player, self.meld)

    def __repr__(self) -> str: return f'<pick up from pile: {self.meld}>'

class MakeMeldHandAndFoot(Action):
    
    def __init__(self, game:GameHandAndFoot, player:PlayerHandAndFoot, meld:MeldHandAndFoot=None) -> None:
        self.game = game
        self.player = player
        self.hand = player.hand
        self.melds = player.melds
        self.make_meld = self.hand.make_meld
        self.meld = meld
        self.transaction = Transaction('make meld', self.hand, self.make_meld, self.melds, meld=meld)

    def sub(self):
        return [MakeMeldHandAndFoot(self.game, self.player, meld=meld) for meld in self.player.available_melds()]

    def play(self):
        self.transaction()

    def __repr__(self) -> str: return f'make meld: {self.meld}'

class AddToMeldHandAndFoot(Action):

    def __init__(self, game:GameHandAndFoot, player:PlayerHandAndFoot, meld:MeldHandAndFoot=None, cards:Iterable[CardHandAndFoot]=None) -> None:
        self.game = game
        self.player = player
        self.hand = player.hand
        self.meld = meld
        self.cards = cards

    def sub(self):
        return self.player.available_adds()

class BreakInHandAndFoot(Action):
    ...

class PlayCardsHandAndFoot(Action):
    ...

class DiscardHandAndFoot(Action):
    
    def __init__(self, game:GameHandAndFoot, player:PlayerHandAndFoot, card:CardHandAndFoot=None) -> None:
        self.game:GameHandAndFoot = game
        self.player:PlayerHandAndFoot = player
        self.card:CardHandAndFoot = card
        self.discard = self.player.discard
        self.transaction = Transaction('discard', player.hand, self.discard, self.game.pile)

    def sub(self):
        return [DiscardHandAndFoot(self.game, self.player, card) for card in self.player.hand]
    
    def play(self):...

class ScoreHandAndFoot(Action):
    ...

class CleanUpHandAndFoot(Action):
    ...

class SettingsHandAndFoot(Settings):

    start_phase = Phase('start', [DealHandAndFoot])
    aquire_phase = Phase('aquire', [DrawHandAndFoot, PickUpHandAndFoot])
    play_phase = Phase('play', [PlayCardsHandAndFoot, DiscardHandAndFoot])
    end_phase = Phase('end', [ScoreHandAndFoot, CleanUpHandAndFoot])
    phases = [start_phase, aquire_phase, play_phase, end_phase]
    default = None

if __name__ == '__main__':
    game = GameHandAndFoot()
    state = State([SettingsHandAndFoot.aquire_phase])
    game.state = state
    player:PlayerHandAndFoot = game.add_player('andrew', 'human').players[0]
    game.deck.shuffle()
    player.hand += game.deck.deal()
    player.melds = [MeldHandAndFoot(4, CardHandAndFoot(4, 'diamonds'), CardHandAndFoot(4, 'diamonds'), CardHandAndFoot(4, 'diamonds'))]
    print('4s', len(player.hand.of_rank(4)), '/', len(player.hand.wilds()))
    print('melds', player.melds)
    print(player.available_adds())
