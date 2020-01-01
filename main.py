"""
Copyright 2020 (c) GlibGlob Ltd.
Author: Laurence Psychic
Email: vesper.porta@protonmail.com

Tarrot card reader.
"""

from random import random, shuffle, sample

from load_data import load_stat_csv


tarot_data = None


class CardDeck(object):
    """docstring for Tarrot"""
    deck = []
    selected = []
    dealt_to = {}

    def shuffle(self, with_selected=True):
        """
        Simple shuffle for a list of numbers
        """
        if with_selected:
            self.deck += self.selected
            self.selected = []
        shuffle(self.deck)

    def select(self, count=5, deal_to=None):
        """
        Collect a number of cards from the deck.
        """
        selection = self.deck[:count]
        if deal_to:
            if deal_to in self.dealt_to:
                self.dealt_to[deal_to] += selection
            else:
                self.dealt_to[deal_to] = selection
        self.selected += selection
        self.deck = self.deck[count + 1:]

    def random(self, count=5, deal_to=None):
        """
        Collect a number of cards from the deck, at random.
        """
        self.selected += sample(self.deck, count)
        count = 0
        for card in self.selected:
            try:
                index = self.deck.index(card)
                self.deck = self.deck[:index] + self.deck[index + 1:]
            except ValueError:
                pass

    def __init__(self, cards=79):
        super(CardDeck, self).__init__()
        self.deck = list(range(cards))
        self.shuffle()


def main():
    tarot_data = load_stat_csv('tarots')
    tarot = CardDeck(cards=len(tarot_data.stats))
    tarot.select()
    for card in tarot.selected:
        upright = bool(random() > 0.5)
        drawn = tarot_data.stats[card]
        print(
            'Card {} : {} = {}'.format(
                '⬆' if upright else '⬇',
                drawn.name,
                drawn.upright if upright else drawn.reversed
            )
        )


if __name__ == '__main__':
    main()
