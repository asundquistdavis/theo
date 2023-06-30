# from hf import *
from time import sleep
from components import *

def test_add_player():
    game = Game()
    print(game)
    print(game.add_player('andrew'))
    print(game.add_player('tom'))
    print(game)
    sleep(1)
    print(game.start())
    print(game)

# def test_COC():
#     coc = Collection_Of_Cards('Andrew')
#     coc.append(Card('Ace'))
#     coc.append(Card('Diamond'))
#     coc.append(Card('Diamond2'))
#     coc.append(Card('Diamond3'))
#     coc.append(Card('Diamond4'))
#     coc.append(Card('Diamond5'))
#     coc.shuffle()
#     return coc.deal(2)

# def test_Tran():
#     coc = Collection_Of_Cards('Andrew')
#     coc.create_card('card1')
#     print(coc.list)
#     coc2 = Collection_Of_Cards('Tom')
#     print(coc2.list)
#     transaction(coc[0], coc2)
#     print(coc2.list)

if __name__ == '__main__':
    test_add_player()
