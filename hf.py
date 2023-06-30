from components import Card, Deck, Action, Player, Rules, Game, Item

class HFRules(Rules):

    def DEFAULT(game):
        return HFRules(game)

    def __init__(self, game, preload='default') -> None:
        if preload == 'default':
            self.CARD_NAMES = lambda rank, suit: 'joker' if rank == 0 else 'ace' if rank == 1 else 'jack' if rank == 11 else 'queen' if rank == 12 else 'king' if rank == 13 else rank
            self.NUMBER_OF_DECKS = 5
            self.CARD_BASE_POINTS = lambda rank: 50 if rank == 0 else 20 if rank < 3 else 0 if rank == 3 else 5 if rank < 8 else 10
            self.CARD_QUANTITIES = lambda rank, suit: self.NUMBER_OF_DECKS
            super().__init__(self, game)

    def parse_raw_card(self, rank, suit):
        name = self.CARD_NAMES(rank, suit)
        base_points = self.CARD_BASE_POINTS(rank)
        quantity = self.CARD_QUANTITIES(rank, suit)
        return name, base_points, quantity

class HFCard(Card):
    def __init__(self, game, rank, suit='wild') -> None:
        self.game:Game = game
        self.rank = rank
        self.suit = suit
        name, self.base_points = self.game.rules.parse_raw_card(rank, suit)
        super().__init__(self, name)

    def __repr__(self) -> str:
        return self.name

class HFDeck(Deck):
    def __init__(self, play_type='2v2') -> None:
        cards = [HFCard(rank, suit) for rank, suit in HFDeck.pop_raw_cards(play_type)]
        super().__init__(cards)

    def pop_raw_cards(play_type):
        base_deck = [(rank, suit) for rank in range(1, 14) for suit in ('hearts', 'clubs', 'diamonds', 'spades')]
        raw_cards = []
        if play_type == '2v2':
            raw_cards = base_deck*5
        return raw_cards


class HFPlayer(Player):
    def __init__(self, name, score=0) -> None:
        super().__init__(name, score)


# Actions

class DrawHFCard(Action):
    def __init__(self, ) -> None:
        parameters = {
            
        }
        super().__init__('drawhfcard', parameters)


class HFGame(Game):
    def __init__(self, players=..., turns=..., deck=Deck.NONE) -> None:
        super().__init__(players, turns, deck)
        self.reference = 'hand and foot game'

    def start():
        pass
