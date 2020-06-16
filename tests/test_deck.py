import sys
import os

root_dir = os.path.abspath(os.path.join( os.path.dirname( __file__ ), '..' ))
python_dir = os.path.join(root_dir, 'python')
sys.path.append(python_dir)

import unittest
from tests import load_tests
load_tests.__module__ = __name__
from unittest.mock import Mock

sys.modules['vim'] = Mock()

from mtgcard.card import Card

from vim_mtg.deck import add_section
from vim_mtg.deck import add_to_section
from vim_mtg.deck import move_card
from vim_mtg.deck import move_cards
from vim_mtg.deck import get_section
from vim_mtg.deck import get_deck
from vim_mtg.deck import find_section
from vim_mtg.deck import mana_curve
from vim_mtg.deck import print_mana_curve
from vim_mtg.deck import process_deck
from vim_mtg.deck import sectioned_deck
from vim_mtg.deck import surrounding_blanklines
from vim_mtg.deck import card_line_print
from vim_mtg.deck import std_deck
from vim_mtg.deck import total_cards
from vim_mtg.deck import legal_formats
from vim_mtg.deck import legal_formats_print
from vim_mtg.deck import devotion
from vim_mtg.deck import devotion_print
from vim_mtg.deck import deck_stats

def setUpModule():

    global DECK_MAIN
    global DECK_SB
    global DECK_OTHER
    DECK_MAIN = 'Main'
    DECK_SB = 'Sideboard'
    DECK_OTHER = 'Other'


class PrintManaCurveTest(unittest.TestCase):

    def test_empty_deck(self):

        curve = [0,0,0,0,0,0,0]

        expected_result = '''
        1   5    10   15   20
 1: 0  |
 2: 0  |
 3: 0  |
 4: 0  |
 5: 0  |
6+: 0  |
 0: 0  |
        '''.lstrip('\n').rstrip().splitlines()
        actual_result = print_mana_curve(curve)
        self.assertEqual(actual_result, expected_result)

    def test_one_card(self):

        curve = [0,0,4,0,0,0,0]

        expected_result = '''
        1   5    10   15   20
 1: 0  |
 2: 4  |    
 3: 0  |
 4: 0  |
 5: 0  |
6+: 0  |
 0: 0  |
        '''.lstrip('\n').rstrip().splitlines()
        actual_result = print_mana_curve(curve)
        self.assertEqual(actual_result, expected_result)


    def test_lands(self):
        curve = [24,0,0,0,0,0,0]
        expected_result = '''
        1   5    10   15   20
 1: 0  |
 2: 0  |
 3: 0  |
 4: 0  |
 5: 0  |
6+: 0  |
 0: 24 |                        
'''.lstrip('\n').rstrip('\n').splitlines()
        actual_result = print_mana_curve(curve)
        self.assertEqual(actual_result, expected_result)


class ManaCurveTest(unittest.TestCase):

    def test_empty_list(self):
        expected_result = [0,0,0,0,0,0,0]
        deck = []
        actual_result = mana_curve(deck)
        self.assertEqual(actual_result, expected_result)

    def test_one_card(self):
        c = Card()
        c.cmc = 2
        deck = [{'card':c, 'count':4}]
        expected_result = [0,0,4,0,0,0,0]
        actual_result = mana_curve(deck)
        self.assertEqual(actual_result, expected_result)

    def test_two_cards(self):
        c1 = Card()
        c1.cmc = 2
        c2 = Card()
        c2.cmc = 1
        deck = [{'card':c1, 'count':4}, {'card':c2, 'count':3}]
        expected_result = [0,3,4,0,0,0,0]
        actual_result = mana_curve(deck)
        self.assertEqual(actual_result, expected_result)

    def test_two_cards_same_cmc(self):
        c1 = Card()
        c1.cmc = 2
        c2 = Card()
        c2.cmc = 2
        deck = [{'card':c1, 'count':4}, {'card':c2, 'count':3}]
        expected_result = [0,0,7,0,0,0,0]
        actual_result = mana_curve(deck)
        self.assertEqual(actual_result, expected_result)


class GetDeckTest(unittest.TestCase):

    def test_empty(self):
        b = '''
'''.strip().splitlines()
        d = get_deck(b)
        self.assertEqual(d, [])

    def test_one_card(self):
        b = '''
4	Bonecrusher Giant
'''.strip().splitlines()
        d = get_deck(b)
        self.assertEqual(d[0]['count'], 4)
        self.assertEqual(d[0]['card'].name, 'Bonecrusher Giant')
        self.assertEqual(d[0]['card'].setcode, 'ELD')
        self.assertEqual(d[0]['card'].cmc, 3)

    def test_set_specified(self):
        b = '''
4	Shock 10E
'''.strip().splitlines()
        d = get_deck(b)
        self.assertEqual(d[0]['count'], 4)
        self.assertEqual(d[0]['card'].name, 'Shock')
        self.assertEqual(d[0]['card'].setcode, '10E')
        self.assertEqual(d[0]['card'].cmc, 1)

    def test_set_unspecified(self):
        b = '''
4	Shock
'''.strip().splitlines()
        d = get_deck(b)
        self.assertEqual(d[0]['count'], 4)
        self.assertEqual(d[0]['card'].name, 'Shock')
        self.assertEqual(d[0]['card'].setcode, 'M20')
        self.assertEqual(d[0]['card'].cmc, 1)

    def test_two_cards(self):
        b = '''
4	Shock
2	Mana Leak
'''.strip().splitlines()
        d = get_deck(b)
        self.assertEqual(d[1]['count'], 2)
        self.assertEqual(d[1]['card'].name, 'Mana Leak')
        self.assertEqual(d[1]['card'].cmc, 2)

    # value errors

    #     def test_invalid_card(self):
    #         b = '''
    # 4	Pikachu
    # '''.strip().splitlines()
    #         self.assertRaises(ValueError, get_deck, b)


class FindDeckTest(unittest.TestCase):

    def test_zero_lines(self):
        b = []
        expected_result = None
        actual_result = find_section(b, 1)
        self.assertEqual(actual_result, expected_result)

    def test_only_main(self):
        b = [DECK_MAIN]
        expected_result = (0, 0)
        actual_result = find_section(b, 1)
        self.assertEqual(actual_result, expected_result)

    def test_main_and_blank_line(self):
        b = [DECK_MAIN, '']
        expected_result = (0, 1)
        actual_result = find_section(b, 1)
        self.assertEqual(actual_result, expected_result)

    def test_main_and_card(self):
        b = [DECK_MAIN, '1 Shock']
        expected_result = (0, 1)
        actual_result = find_section(b, 1)
        self.assertEqual(actual_result, expected_result)

    def test_main_and_card_another(self):
        b = [DECK_MAIN, '4\tFervent Champion']
        expected_result = (0, 1)
        actual_result = find_section(b, 1)
        self.assertEqual(actual_result, expected_result)

    def test_main_and_blank_line_before_and_after(self):
        b = ['', DECK_MAIN, '']
        expected_result = (1, 2)
        actual_result = find_section(b, 1)
        self.assertEqual(actual_result, expected_result)

    def test_main_and_card_and_sideboard(self):
        b = [DECK_MAIN, '1 Shock', DECK_SB]
        expected_result = (0, 1)
        actual_result = find_section(b, 1)
        self.assertEqual(actual_result, expected_result)

    def test_main_sideboard(self):
        b = [DECK_MAIN, DECK_SB]
        expected_result = (0,0)
        actual_result = find_section(b, 1)
        self.assertEqual(actual_result, expected_result)

    def test_sideboard_one_card(self):
        b = [DECK_MAIN, DECK_SB, '1 Shock']
        expected_result = (1,2)
        actual_result = find_section(b, 2)
        self.assertEqual(actual_result, expected_result)

    # value errors

    def test_invalid_section(self):
        b = f'''
{DECK_SB}
2	Fervent Champion
'''.strip().splitlines()
        self.assertRaises(ValueError, find_section, b, 0)


class SurroundingBlankLinesTest(unittest.TestCase):

    def test_zero_blank_lines(self):
        l = ['item']
        expected_result = (0, 0)
        actual_result = surrounding_blanklines(l)
        self.assertEqual(actual_result, expected_result)

    def test_start_one_blank_line(self):
        l = ['', 'item']
        expected_result = (1, 0)
        actual_result = surrounding_blanklines(l)
        self.assertEqual(actual_result, expected_result)

    def test_end_one_blank_line(self):
        l = ['item', '']
        expected_result = (0, 1)
        actual_result = surrounding_blanklines(l)
        self.assertEqual(actual_result, expected_result)

    def test_start_and_end_one_blank_line(self):
        l = ['', 'item', '']
        expected_result = (1, 1)
        actual_result = surrounding_blanklines(l)
        self.assertEqual(actual_result, expected_result)

    def test_star_and_end_blank_lines_and_inner_blank_lines(self):
        l = ['', 'item1', '', 'item2', '']
        expected_result = (1, 1)
        actual_result = surrounding_blanklines(l)
        self.assertEqual(actual_result, expected_result)

    def test_start_two_blank_line(self):
        l = ['', '', 'item']
        expected_result = (2, 0)
        actual_result = surrounding_blanklines(l)
        self.assertEqual(actual_result, expected_result)

    def test_end_two_blank_line(self):
        l = ['item', '', '']
        expected_result = (0, 2)
        actual_result = surrounding_blanklines(l)
        self.assertEqual(actual_result, expected_result)

    def test_one_space_as_line_one(self):
        l = [' ', 'item']
        expected_result = (1, 0)
        actual_result = surrounding_blanklines(l)
        self.assertEqual(actual_result, expected_result)


class TotalCardsTest(unittest.TestCase):

    def test_empty_deck(self):
        b = '''
'''.strip().splitlines()
        expected_result = 0
        actual_result = total_cards(get_deck(b))
        self.assertEqual(actual_result, expected_result)

    def test_one_card(self):
        b = '''
1	Mana Leak
'''.strip().splitlines()
        expected_result = 1
        actual_result = total_cards(get_deck(b))
        self.assertEqual(actual_result, expected_result)

    def test_two_cards(self):
        b = '''
2	Mana Leak
'''.strip().splitlines()
        expected_result = 2
        actual_result = total_cards(get_deck(b))
        self.assertEqual(actual_result, expected_result)



class CardLinePrintTest(unittest.TestCase):

    def test_without_mana(self):
        b = '''
1 Bonecrusher Giant
'''.strip().splitlines()
        deck = get_deck(b)
        expected_result = '''
1 Bonecrusher Giant
        '''.strip()
        lname = lname=len(deck[0]['card'].name)
        actual_result = card_line_print(deck[0])
        self.assertEqual(actual_result, expected_result)

    def test_with_mana_no_ansi(self):
        b = '''
1 Bonecrusher Giant
'''.strip().splitlines()
        deck = get_deck(b)
        expected_result = '''
1  Bonecrusher Giant  2R
        '''.strip()
        lname = len(deck[0]['card'].name)
        actual_result = card_line_print(deck[0], lname=lname, lmana=15,
                ansi=False)
        self.assertEqual(actual_result, expected_result)

    def test_with_mana(self):
        b = '''
1 Bonecrusher Giant
'''.strip().splitlines()
        deck = get_deck(b)
        expected_result = '''
1  Bonecrusher Giant  [1;38;5;253m2[0m[1;38;5;216mR[0m
        '''.strip()
        lname = len(deck[0]['card'].name)
        actual_result = card_line_print(deck[0], lname=lname, lmana=15)
        self.assertEqual(actual_result, expected_result)

    def test_0cmc_with_mana(self):
        b = '''
1 Forest
'''.strip().splitlines()
        deck = get_deck(b)
        expected_result = '''
1  Forest
        '''.strip()
        lname = len(deck[0]['card'].name)
        actual_result = card_line_print(deck[0], lname=lname, lmana=15)
        self.assertEqual(actual_result, expected_result)

class StdDeckTest(unittest.TestCase):

    def test_one_card(self):
        b = '''
4	Bonecrusher Giant
'''.strip().splitlines()
        deck = get_deck(b)
        expected_result = '''
4 Bonecrusher Giant
        '''.strip().splitlines()
        actual_result = std_deck(deck)
        self.assertEqual(actual_result, expected_result)

    def test_two_cards(self):
        b = '''
4	Bonecrusher Giant
4	Fervent Champion
'''.strip().splitlines()
        deck = get_deck(b)
        expected_result = '''
4 Fervent Champion
4 Bonecrusher Giant
        '''.strip().splitlines()
        actual_result = std_deck(deck)
        self.assertEqual(actual_result, expected_result)

    def test_one_card_with_mana(self):
        b = '''
4	Bonecrusher Giant
'''.strip().splitlines()
        deck = get_deck(b)
        expected_result = '''
4  Bonecrusher Giant  [1;38;5;253m2[0m[1;38;5;216mR[0m
        '''.strip().splitlines()
        actual_result = std_deck(deck, mana=True)
        self.assertEqual(actual_result, expected_result)

    def test_one_card_with_mana_no_ansi(self):
        b = '''
4	Bonecrusher Giant
'''.strip().splitlines()
        deck = get_deck(b)
        expected_result = '''
4  Bonecrusher Giant  2R
        '''.strip().splitlines()
        actual_result = std_deck(deck, mana=True, ansi=False)
        self.assertEqual(actual_result, expected_result)



class SectionedDeckTest(unittest.TestCase):

    def test_one_card(self):
        b = '''
4	Fervent Champion
'''.strip().splitlines()
        deck = get_deck(b)
        expected_result = '''
Creatures 4
4  Fervent Champion  R
'''.lstrip('\n').splitlines()
        actual_result = sectioned_deck(deck, ansi=False)
        self.assertEqual(actual_result, expected_result)

    def test_two_types(self):
        b = '''
4	Fervent Champion
1	Chandra, Acolyte of Flame
'''.strip().splitlines()
        deck = get_deck(b)
        expected_result = '''
Creatures 4
4  Fervent Champion           R

Planeswalkers 1
1  Chandra, Acolyte of Flame  1RR
'''.lstrip('\n').splitlines()
        actual_result = sectioned_deck(deck, ansi=False)
        self.assertEqual(actual_result, expected_result)

    def test_two_types_one_invalid(self):
        b = '''
4	Fervent Champion
1       Pikachu
1	Chandra, Acolyte of Flame
'''.strip().splitlines()
        deck = get_deck(b)
        expected_result = '''
Creatures 4
4  Fervent Champion           R

Planeswalkers 1
1  Chandra, Acolyte of Flame  1RR
'''.lstrip('\n').splitlines()
        actual_result = sectioned_deck(deck, ansi=False)
        self.assertEqual(actual_result, expected_result)


class ProcessDeckTest(unittest.TestCase):

    def test_empty(self):
        b = '''
'''.strip().splitlines()

        expected_result = '''
'''.strip().splitlines()

        actual_result = process_deck(b, main_sectioned=False, ansi=False)
        self.assertEqual(actual_result, expected_result)

    def test_main_empty(self):
        b = f'''
{DECK_MAIN}
'''.strip().splitlines()

        expected_result = f'''
{DECK_MAIN} 0


----
'''.strip().splitlines()

        actual_result = process_deck(b, main_sectioned=False, ansi=False)[0:4]
        self.assertEqual(actual_result, expected_result)

    def test_main_one_card(self):
        b = f'''
{DECK_MAIN}
4	Fervent Champion
'''.strip().splitlines()

        expected_result = f'''
{DECK_MAIN} 4

4 Fervent Champion

----
'''.strip().splitlines()

        actual_result = process_deck(b, main_sectioned=False, ansi=False)[0:5]
        self.assertEqual(actual_result, expected_result)

    def test_main_one_card_sectioned(self):
        b = f'''
{DECK_MAIN}
4	Fervent Champion
'''.strip().splitlines()

        expected_result = f'''
{DECK_MAIN} 4

Creatures 4
4  Fervent Champion  R


----
'''.strip().splitlines()

        actual_result = process_deck(b, main_sectioned=True, ansi=False)[0:7]
        self.assertEqual(actual_result, expected_result)

    def test_main_and_sideboard(self):
        b = f'''
{DECK_MAIN}
2	Fervent Champion
{DECK_SB}
2	Fervent Champion
'''.strip().splitlines()

        expected_result = f'''
{DECK_MAIN} 2

Creatures 2
2  Fervent Champion  R


{DECK_SB} 2

2  Fervent Champion  R

----
'''.strip().splitlines()

        actual_result = process_deck(b, main_sectioned=True, ansi=False)[0:11]
        self.assertEqual(actual_result, expected_result)

    def test_other(self):
        b = f'''
{DECK_OTHER}

2	Fervent Champion
'''.strip().splitlines()

        expected_result = f'''
{DECK_OTHER} 2

2 Fervent Champion
'''.strip().splitlines()

        actual_result = process_deck(b, main_sectioned=True, ansi=False)[0:11]
        self.assertEqual(actual_result, expected_result)

    def test_not_process_other(self):
        b = f'''
{DECK_OTHER}
2	Fervent Champion
'''.strip().splitlines()

        expected_result = f'''
{DECK_OTHER} 2
2	Fervent Champion
'''.strip().splitlines()

        actual_result = process_deck(b, main_sectioned=True,
                process_other=False, ansi=False)[0:11]
        self.assertEqual(actual_result, expected_result)


class AddSectionTest(unittest.TestCase):

    def test_add_main(self):
        b = []
        expected_result = [f'{DECK_MAIN}']
        actual_result = add_section(b, 1)
        self.assertEqual(actual_result, expected_result)

    def test_add_main_one_empty_line(self):
        # this is what a real vim empty buffer will look like
        b = ['']
        expected_result = [f'{DECK_MAIN}']
        actual_result = add_section(b, 1)
        self.assertEqual(actual_result, expected_result)

    def test_add_main_twice(self):
        b = f'''
{DECK_MAIN}
'''.strip().splitlines()
        expected_result = f'''
{DECK_MAIN}
'''.strip().splitlines()
        actual_result = add_section(b, 1)
        self.assertEqual(actual_result, expected_result)

    def test_add_sb(self):
        b = f'''
{DECK_MAIN}
2 Fervent Champion
'''.strip().splitlines()
        expected_result = f'''
{DECK_MAIN}
2 Fervent Champion
{DECK_SB}
'''.strip().splitlines()
        actual_result = add_section(b, 2)
        self.assertEqual(actual_result, expected_result)


    def test_add_sb_to_main_other(self):
        b = f'''
{DECK_MAIN}
2 Fervent Champion
{DECK_OTHER}
2 Fervent Champion
'''.strip().splitlines()
        expected_result = f'''
{DECK_MAIN}
2 Fervent Champion
{DECK_SB}
{DECK_OTHER}
2 Fervent Champion
'''.strip().splitlines()
        actual_result = add_section(b, 2)
        self.assertEqual(actual_result, expected_result)


    def test_add_sb_to_separator(self):
        b = f'''
{DECK_MAIN}
2 Fervent Champion
----
'''.strip().splitlines()
        expected_result = f'''
{DECK_MAIN}
2 Fervent Champion
{DECK_SB}
----
'''.strip().splitlines()
        actual_result = add_section(b, 2)
        self.assertEqual(actual_result, expected_result)

    # value errors

    def test_invalid_section(self):
        b = f'''
{DECK_SB}
2	Fervent Champion
'''.strip().splitlines()
        self.assertRaises(ValueError, add_section, b, 0)

class AddToSectionTest(unittest.TestCase):

    def test_to_main(self):
        b = f'''
{DECK_MAIN}
2	Fervent Champion
'''.strip().splitlines()
        expected_result = f'''
{DECK_MAIN}
1 Embercleave
2	Fervent Champion
'''.strip().splitlines()
        actual_result = add_to_section(b, 'Embercleave', 1, 1)
        self.assertEqual(actual_result, expected_result)


    def test_to_main_no_main(self):
        b = f'''
'''.strip().splitlines()
        expected_result = f'''
{DECK_MAIN}
1 Embercleave
'''.strip().splitlines()
        actual_result = add_to_section(b, 'Embercleave', 1, 1)
        self.assertEqual(actual_result, expected_result)


    def test_to_main_three_blank_lines(self):
        b = f'''
{DECK_MAIN}



'''.lstrip().splitlines()
        expected_result = f'''
{DECK_MAIN}
1 Embercleave



'''.lstrip().splitlines()
        actual_result = add_to_section(b, 'Embercleave', 1, 1)
        self.assertEqual(actual_result, expected_result)


    def test_to_main_separator(self):
        b = f'''
{DECK_MAIN}
---
'''.lstrip().splitlines()
        expected_result = f'''
{DECK_MAIN}
1 Embercleave
---
'''.lstrip().splitlines()
        actual_result = add_to_section(b, 'Embercleave', 1, 1)
        self.assertEqual(actual_result, expected_result)


    def test_to_sb_with_main_and_other(self):
        b = f'''
{DECK_MAIN}
{DECK_SB}
{DECK_OTHER}
---
'''.lstrip().splitlines()
        expected_result = f'''
{DECK_MAIN}
{DECK_SB}
1 Embercleave
{DECK_OTHER}
---
'''.lstrip().splitlines()
        actual_result = add_to_section(b, 'Embercleave', 1, 2)
        self.assertEqual(actual_result, expected_result)


    def test_to_new_sb_with_main_and_other(self):
        b = f'''
{DECK_MAIN}
{DECK_OTHER}
---
'''.lstrip().splitlines()
        expected_result = f'''
{DECK_MAIN}
{DECK_SB}
1 Embercleave
{DECK_OTHER}
---
'''.lstrip().splitlines()
        actual_result = add_to_section(b, 'Embercleave', 1, 2)
        self.assertEqual(actual_result, expected_result)


    def test_to_other_with_count_two(self):
        b = f'''
{DECK_OTHER}
'''.lstrip().splitlines()
        expected_result = f'''
{DECK_OTHER}
2 Embercleave
'''.lstrip().splitlines()
        actual_result = add_to_section(b, 'Embercleave', 2, 3)
        self.assertEqual(actual_result, expected_result)

    # value errors

    def test_invalid_section(self):
        b = f'''
{DECK_SB}
2	Fervent Champion
'''.strip().splitlines()
        self.assertRaises(ValueError, add_to_section, b, 'Embercleave', 1, 0)


class GetSectionTest(unittest.TestCase):

    def test_main(self):
        b = f'''
{DECK_MAIN}
2	Fervent Champion
'''.strip().splitlines()
        expected_result = 1
        actual_result = get_section(b, 1)
        self.assertEqual(actual_result, expected_result)

    def test_sb(self):
        b = f'''
{DECK_SB}
2	Fervent Champion
'''.strip().splitlines()
        expected_result = 2
        actual_result = get_section(b, 1)
        self.assertEqual(actual_result, expected_result)

    def test_sb_with_main(self):
        b = f'''
{DECK_MAIN}
{DECK_SB}
2	Fervent Champion
'''.strip().splitlines()
        expected_result = 2
        actual_result = get_section(b, 2)
        self.assertEqual(actual_result, expected_result)

    def test_sb_with_main(self):
        b = f'''
{DECK_MAIN}
{DECK_SB}
----
2	Fervent Champion
'''.strip().splitlines()
        expected_result = -1
        actual_result = get_section(b, 3)
        self.assertEqual(actual_result, expected_result)


    # value errors

    def test_line_does_not_exist(self):
        b = f'''
{DECK_SB}
2	Fervent Champion
'''.strip().splitlines()
        self.assertRaises(ValueError, get_section, b, 2)
        self.assertRaises(ValueError, get_section, b, -1)


class MoveCardTest(unittest.TestCase):

    def test_one_card_from_main_to_sb(self):
        b = f'''
{DECK_MAIN}
2	Fervent Champion
{DECK_SB}
'''.strip().splitlines()
        expected_result = f'''
{DECK_MAIN}
{DECK_SB}
2 Fervent Champion
'''.strip().splitlines()
        actual_result = move_card(b, 1, 2)
        self.assertEqual(actual_result, expected_result)

    def test_one_card_from_sb_to_main(self):
        b = f'''
{DECK_MAIN}
{DECK_SB}
2	Fervent Champion
'''.strip().splitlines()
        expected_result = f'''
{DECK_MAIN}
2 Fervent Champion
{DECK_SB}
'''.strip().splitlines()
        actual_result = move_card(b, 2, 1)
        self.assertEqual(actual_result, expected_result)

    def test_one_card_from_main_to_sb_count(self):
        b = f'''
{DECK_MAIN}
2	Fervent Champion
{DECK_SB}
'''.strip().splitlines()
        expected_result = f'''
{DECK_MAIN}
1	Fervent Champion
{DECK_SB}
1 Fervent Champion
'''.strip().splitlines()
        actual_result = move_card(b, 1, 2, 1)
        self.assertEqual(actual_result, expected_result)

    def test_one_card_from_main_to_sb_count_3(self):
        b = f'''
{DECK_MAIN}
4 Fervent Champion
{DECK_SB}
'''.strip().splitlines()
        expected_result = f'''
{DECK_MAIN}
1 Fervent Champion
{DECK_SB}
3 Fervent Champion
'''.strip().splitlines()
        actual_result = move_card(b, 1, 2, 3)
        self.assertEqual(actual_result, expected_result)

    def test_one_card_from_main_to_sb_invalid_card(self):
        b = f'''
{DECK_MAIN}
1 Pikachu
{DECK_SB}
'''.strip().splitlines()
        expected_result = f'''
{DECK_MAIN}
1 Pikachu
{DECK_SB}
'''.strip().splitlines()
        actual_result = move_card(b, 1, 2, 1)
        self.assertEqual(actual_result, expected_result)

    def test_not_in_section(self):
        b = f'''
2 Fervent Champion
{DECK_MAIN}
{DECK_SB}
'''.strip().splitlines()
        expected_result = f'''
{DECK_MAIN}
{DECK_SB}
2 Fervent Champion
'''.strip().splitlines()
        actual_result = move_card(b, 0, 2)
        self.assertEqual(actual_result, expected_result)

    def test_after_separator(self):
        b = f'''
{DECK_MAIN}
2 Fervent Champion
2 Embercleave
{DECK_SB}
{DECK_OTHER}
----
1 Chandra, Acolyte of Flame
'''.strip().splitlines()
        expected_result = f'''
{DECK_MAIN}
2 Fervent Champion
2 Embercleave
{DECK_SB}
{DECK_OTHER}
----
1 Chandra, Acolyte of Flame
'''.strip().splitlines()
        actual_result = move_card(b, 6, 2)
        self.assertEqual(actual_result, expected_result)

    # value errors

    def test_invalid_index(self):
        b = f'''
{DECK_SB}
2	Fervent Champion
'''.strip().splitlines()
        self.assertRaises(ValueError, move_card, b, -1, 2)
        self.assertRaises(ValueError, move_card, b, 2, 2)

    def test_invalid_section(self):
        b = f'''
{DECK_SB}
2	Fervent Champion
'''.strip().splitlines()
        self.assertRaises(ValueError, move_card, b, 1, 0)


class MoveCardsTest(unittest.TestCase):

    def test_two_different_cards_from_main_to_sb(self):
        b = f'''
{DECK_MAIN}
2 Fervent Champion
2 Embercleave
{DECK_SB}
'''.strip().splitlines()
        expected_result = f'''
{DECK_MAIN}
{DECK_SB}
2 Fervent Champion
2 Embercleave
'''.strip().splitlines()
        actual_result = move_cards(b, [1, 2], 2)
        self.assertEqual(actual_result, expected_result)

    def test_empty_deck(self):
        b = f'''
{DECK_MAIN}
{DECK_SB}
'''.strip().splitlines()
        expected_result = f'''
{DECK_MAIN}
{DECK_SB}
'''.strip().splitlines()
        actual_result = move_cards(b, [0,1], 2)
        self.assertEqual(actual_result, expected_result)

    def test_not_in_section(self):
        b = f'''
2 Fervent Champion
{DECK_MAIN}
{DECK_SB}
'''.strip().splitlines()
        expected_result = f'''
{DECK_MAIN}
{DECK_SB}
2 Fervent Champion
'''.strip().splitlines()
        actual_result = move_cards(b, [0], 2)
        self.assertEqual(actual_result, expected_result)

    def test_after_separator(self):
        b = f'''
{DECK_MAIN}
2 Fervent Champion
2 Embercleave
{DECK_SB}
{DECK_OTHER}
----
1 Chandra, Acolyte of Flame
'''.strip().splitlines()
        expected_result = f'''
{DECK_MAIN}
2 Fervent Champion
2 Embercleave
{DECK_SB}
{DECK_OTHER}
----
1 Chandra, Acolyte of Flame
'''.strip().splitlines()
        actual_result = move_cards(b, [6], 2)
        self.assertEqual(actual_result, expected_result)

    def test_multiple_after_separator(self):
        b = f'''
{DECK_MAIN}
2 Fervent Champion
2 Embercleave
{DECK_SB}
{DECK_OTHER}
----
1 Chandra, Acolyte of Flame
1 Chandra, Acolyte of Flame
1 Chandra, Acolyte of Flame
1 Chandra, Acolyte of Flame
'''.strip().splitlines()
        expected_result = f'''
{DECK_MAIN}
2 Fervent Champion
2 Embercleave
{DECK_SB}
{DECK_OTHER}
----
1 Chandra, Acolyte of Flame
1 Chandra, Acolyte of Flame
1 Chandra, Acolyte of Flame
1 Chandra, Acolyte of Flame
'''.strip().splitlines()
        actual_result = move_cards(b, [6,7,8], 2)
        self.assertEqual(actual_result, expected_result)



    def test_multiple_not_in_section(self):
        b = f'''
2 Fervent Champion
2 Embercleave
1 Chandra, Acolyte of Flame
{DECK_MAIN}
{DECK_SB}
'''.strip().splitlines()
        expected_result = f'''
{DECK_MAIN}
{DECK_SB}
2 Fervent Champion
2 Embercleave
1 Chandra, Acolyte of Flame
'''.strip().splitlines()
        actual_result = move_cards(b, [0,1,2], 2)
        self.assertEqual(actual_result, expected_result)


    def test_cards_from_different_sections_not_adjacent(self):
        b = f'''
{DECK_MAIN}
2 Fervent Champion
2 Embercleave
{DECK_SB}
1 Chandra, Acolyte of Flame
{DECK_OTHER}
'''.strip().splitlines()
        expected_result = f'''
{DECK_MAIN}
2 Embercleave
{DECK_SB}
{DECK_OTHER}
2 Fervent Champion
1 Chandra, Acolyte of Flame
'''.strip().splitlines()
        actual_result = move_cards(b, [1,4], 3)
        self.assertEqual(actual_result, expected_result)

    def test_already_in_section(self):
        b = f'''
{DECK_MAIN}
2 Fervent Champion
2 Embercleave
{DECK_SB}
1 Chandra, Acolyte of Flame
'''.strip().splitlines()
        expected_result = f'''
{DECK_MAIN}
2 Fervent Champion
2 Embercleave
{DECK_SB}
1 Chandra, Acolyte of Flame
'''.strip().splitlines()
        actual_result = move_cards(b, [4], 2)
        self.assertEqual(actual_result, expected_result)

    def test_all_lines(self):
        b = f'''
{DECK_MAIN}
2 Fervent Champion
2 Embercleave
{DECK_SB}
1 Chandra, Acolyte of Flame
'''.strip().splitlines()
        expected_result = f'''
{DECK_MAIN}
{DECK_SB}
2 Fervent Champion
2 Embercleave
1 Chandra, Acolyte of Flame
'''.strip().splitlines()
        actual_result = move_cards(b, [0,1,2,3,4], 2)
        self.assertEqual(actual_result, expected_result)


class LegalityTest(unittest.TestCase):

    def test_one_card(self):
        b = f'''
2 Fervent Champion
'''.strip().splitlines()
        expected_result = {'modern', 'vintage', 'brawl', 'pioneer', 'legacy',
                'standard', 'commander'}
        actual_result = legal_formats(get_deck(b, verbose=True))
        self.assertEqual(actual_result, expected_result)

    def test_two_cards(self):
        b = f'''
2 Fervent Champion
2 Sol Ring
'''.strip().splitlines()
        expected_result = {'commander'}
        deck = get_deck(b, verbose=True)
        actual_result = legal_formats(deck)
        self.assertEqual(actual_result, expected_result)

    def test_no_cards(self):
        b = f'''
'''.strip().splitlines()
        expected_result = set()
        deck = get_deck(b, verbose=True)
        actual_result = legal_formats(deck)
        self.assertEqual(actual_result, expected_result)


class LegalityPrintTest(unittest.TestCase):

    def test_standard_card(self):
        b = f'''
2 Fervent Champion
'''.strip().splitlines()
        expected_result = f'''
Standard:  legal   Brawl:   legal
Pioneer:   legal   Pauper:
Modern:    legal   Legacy:  legal
Commander: legal   Vintage: legal
'''.strip().splitlines()
        deck = get_deck(b, verbose=True)
        legal_fmts = legal_formats(deck)
        actual_result = legal_formats_print(legal_fmts)
        self.assertEqual(actual_result, expected_result)

    def test_banned_and_restricted(self):
        b = f'''
2 Sol Ring
2 Fervent Champion
'''.strip().splitlines()
        expected_result = f'''
Standard:          Brawl:
Pioneer:           Pauper:
Modern:            Legacy:
Commander: legal   Vintage:
'''.strip().splitlines()
        deck = get_deck(b, verbose=True)
        legal_fmts = legal_formats(deck)
        actual_result = legal_formats_print(legal_fmts)
        self.assertEqual(actual_result, expected_result)

class DevotionTest(unittest.TestCase):

    def test_one_colorless(self):
        b = f'''
2 Island
'''.strip().splitlines()
        expected_result = {}
        deck = get_deck(b)
        actual_result = devotion(deck)
        self.assertEqual(actual_result, expected_result)

    def test_one_color(self):
        b = f'''
2 Fervent Champion
'''.strip().splitlines()
        expected_result = {'R': 2}
        deck = get_deck(b)
        actual_result = devotion(deck)
        self.assertEqual(actual_result, expected_result)

    def test_one_color_blue(self):
        b = f'''
2 Counterspell
'''.strip().splitlines()
        expected_result = {'U': 4}
        deck = get_deck(b)
        actual_result = devotion(deck)
        self.assertEqual(actual_result, expected_result)

    def test_two_colors(self):
        b = f'''
2 Gruul Spellbreaker
'''.strip().splitlines()
        expected_result = {'G': 2, 'R': 2}
        deck = get_deck(b)
        actual_result = devotion(deck)
        self.assertEqual(actual_result, expected_result)


class DevotionPrintTest(unittest.TestCase):

    def test_one_color(self):
        devotion = {'R': 2}
        expected_result = '''
R: 2   (100%)
'''.strip().splitlines()
        actual_result = devotion_print(devotion)
        self.assertEqual(actual_result, expected_result)

    def test_two_colors(self):
        devotion = {'G': 2, 'R': 2}
        expected_result = '''
G: 2   (50%)
R: 2   (50%)
'''.strip().splitlines()
        actual_result = devotion_print(devotion)
        self.assertEqual(actual_result, expected_result)


class StatsTest(unittest.TestCase):

    def test_one_card(self):
        b = f'''
2 Counterspell
2 Island
2 Bloodfell Caves
'''.strip().splitlines()
        deck = get_deck(b)
        s = deck_stats(deck)
        self.assertEqual(s['cmc'], 4)
