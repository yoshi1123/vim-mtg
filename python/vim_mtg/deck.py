# viMTG - The VIM 'Magic: The Gathering' deck builder.
# Copyright (C) 2020  yoshi1@tutanota.com
#
# viMTG is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# viMTG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with viMTG.  If not, see <https://www.gnu.org/licenses/>.

"""The Python part for the mtg filetype."""


import re
import mtgcard.mtgdb
import mtgcard.colors
import mtgcard.util

from vim_mtg.vim_interface import vim_error, vim_warning, settings


add_setcode = 0
debug = 0

# formats
SHOWN_FORMATS = mtgcard.settings.SHOWN_FORMATS

# header format
hdr_fmt = '{} {}'

# header count regex
r_count = ' \d+'

# card line regex
r_card_line = r'^(\d+)(?:\s?x)?\s{1,2}(.+?)(?:\s+([A-Z0-9]{3}))?(?:  |$)'
re_card_ln = re.compile(r_card_line)

# section headers
DECK_MAIN = 'Main'
DECK_SB = 'Sideboard'
DECK_OTHER = 'Other'
sections = {
        1: DECK_MAIN,
        2: DECK_SB,
        3: DECK_OTHER
        }


def find_section(blist, section_nr):
    """Returns (firstline,lastline) of deck section.

    From `start_line` to line before `end_pattern`.

    :param list blist:   list containing deck sections (e.g., a buffer list)
    :param int  section: section number
    :raises ValueError:  if invalid section number

    Example for `find_section(b, 1)`:

        0 |
        1 |Main:       <-- first
        2 |1 Shock
        3 |            <-- last
        4 |Sideboard:

    returns (1, 3)

    """
    try:
        section_name = sections[section_nr]
    except KeyError as e:
        raise ValueError("invalid section number")
    next_sections = list(sections.values())[section_nr:]
    next_sections.append('----')
    r_start = re.compile(r'^{}(?:{})?'.format(section_name, r_count))
    r_end = r'^(?:{})(?:{})?'.format('|'.join(next_sections), r_count)

    firstline = None
    for i, l in enumerate(blist):
        if r_start.match(l):
            firstline = i
            break
    if firstline is None:
        return None

    lastline = len(blist)-1
    for i, l in enumerate(blist[firstline+1:]):
        if re.match(r_end, l):
            lastline = firstline + i
            break

    return (firstline, lastline)


def surrounding_blanklines(blist):
    """Return number of blank lines at start and end.

    :param list blist: list containing deck sections (e.g., a buffer list)

    """
    start_count = 0
    end_count = 0
    section = blist
    for line in section:
        if re.match('^\s*$', line):
            start_count += 1
        else:
            break
    section.reverse()
    for line in section:
        if re.match('^\s*$', line):
            end_count += 1
        else:
            break
    return (start_count, end_count)


def get_deck(deck_lines, verbose=False, warnings=True):
    """Return a deck (as below) from a list of 'count name' lines.

    :param list deck_lines: list of 'count name' strings
    :param int  verbose:    whether to fetch legalities and price for cards
    :param int  warnings:   whether to display warnings for invalid lines

    Example return value:

        [
           {   'card': Card,
               'count': 4
           },
           {   'card': Card,
               'count': 3
           },
           ...
        ]

    """
    db = mtgcard.mtgdb.Interface()
    deck = []
    for l in deck_lines:
        m = re_card_ln.match(l)
        if not m:
            if warnings:
                if not re.match('^(?:Creatures|Planeswalkers|Instants'
                        '|Sorceries|Enchantments|Artifacts|Lands|Other|$)', l):
                    vim_warning("invalid line discarded: '{}'".format(l))
            continue
        count = int(m.group(1))
        name = m.group(2)
        setcode = m.group(3)
        try:
            if not setcode:
                c = db.get_card(name, verbose=verbose)
            else:
                c = db.get_card(name, setcode, verbose=verbose)
            if c.types[0] == 'Token':
                raise ValueError
        except ValueError as e:
            if warnings:
                vim_warning("invalid line discarded: '{}'".format(l))
            continue
        # if already in deck, combine
        found = False
        for i, e in enumerate(deck):
            if e['card'].name.lower() == name.lower():
                deck[i]['count'] += count
                found = True
                break
        if not found:
            deck.append( {'count': count, 'card': c} )

    return deck


def total_cards(deck):
    """Return the number of a cards in the deck `deck`.

    :param list deck: a deck as [{'card': Card, 'count': COUNT}, ...]

    """
    total = 0
    for c in deck:
        total += c['count']
    return total


def mana_curve(deck):
    """Return a list of card counts based on converted mana cost.

    :param list deck: a deck as [{'card': Card, 'count': COUNT}, ...]

    Return value elements:

        [0cmc, 1cmc, 2cmc, 3cmc, 4cmc, 5cmc, 6+cmc]

    """
    curve = [0,0,0,0,0,0,0]
    for c in deck:
        cost = int(c['card'].cmc)
        if cost > 6: cost = 6
        count = c['count']
        curve[cost] = curve[cost] + count

    return curve


def print_mana_curve(curve):
    """Return print of mana curve.

    :param list curve: list of cards based on CMC (see :func:`mana_curve`)

    """
    curve_print = []
    curve_print.append('        1   5    10   15   20')
    total = 0
    for cmc,count in enumerate(curve):
        if cmc == 0: continue
        s_cmc = str(cmc) if cmc != 6 else '6+'
        curve_print.append( '{:>2s}: {:<2d} {:s}{:s}'.format( s_cmc, count, '|',
                                                              count*' ' ) )
    curve_print.append( '{:>2s}: {:<2d} {:s}{:s}'.format( str(0), curve[0], '|',
                                                          curve[0]*' ' ) )

    return curve_print


def card_line_print(dcard, lname=None, lmana=None, add_setcode=False, ansi=True):
    """Return a formatted card line.

    :param dict dcard:       a deck card as {'card': Card, 'count': COUNT}
    :param int  lname:       length of name
    :param int  lmana:       length of manacost
    :param bool add_setcode: whether to add set code for each card
    :param bool ansi:        whether color

    """
    if lmana is None:
        if add_setcode:
            line = '{:d} {:s} {:s}'.format(dcard['count'],
                                    dcard['card'].name,
                                    dcard['card'].setcode)
        else:
            line = '{:d} {:s}'.format(dcard['count'], dcard['card'].name)
    else:
        mana = dcard['card'].manacost
        if mana is not None:
            if ansi:
                mana = mtgcard.colors.colorize_mana(mana, 0)[0]
        else:
            mana = ''
        line = "{:<3d}{:{lname}s}{:{lmana}s}".format(dcard['count'],
                                                     dcard['card'].name,
                                                     mana,
                                                     lname=lname+2,
                                                     lmana=lmana).strip()
    return line


def std_deck(deck, add_setcode=False, mana=False, ansi=True):
    """Return a standard deck list sorted by CMC.

    :param list deck:        a deck as [{'card': Card, 'count': COUNT}, ...]
    :param bool add_setcode: whether to add set code for each card
    :param bool mana:        whether to include manacost
    :param bool ansi:        whether color

    """
    # sort deck by cmc, name
    deck = sorted(deck, key=lambda c: c['card'].name)
    deck = sorted(deck, key=lambda c: c['card'].cmc)

    # create new deck lines sorted by cmc, with 0 cmc last
    formatted_lines = []
    append = []
    if mana:
        # column widths
        lname = max([len(c['card'].name) for c in deck]) if deck else 0
        lmana = 15
        for c in deck:
            if 'Land' in c['card'].types:
                append.append(card_line_print(c, lname, lmana, ansi=ansi))
            else:
                formatted_lines.append(card_line_print(c, lname, lmana,
                    ansi=ansi))
    else:
        for c in deck:
            if add_setcode:
                if 'Land' in c['card'].types:
                    append.append(card_line_print(c))
                else:
                    formatted_lines.append(card_line_print(c))
            else:
                if 'Land' in c['card'].types:
                    append.append(card_line_print(c))
                else:
                    formatted_lines.append(card_line_print(c))
    formatted_lines = formatted_lines + append
    return formatted_lines


def sectioned_deck(deck, add_setcode=False, ansi=True):
    """Return a standard deck list sorted by CMC.

    :param list deck:        a deck as [{'card': Card, 'count': COUNT}, ...]
    :param bool add_setcode: whether to add set code for each card
    :param bool ansi:        whether color
    :raises AssertionError:  if cannot find a card's type section

    """
    if deck == []: return []
    # sort deck by cmc, name
    deck = sorted(deck, key=lambda c: c['card'].name)
    deck = sorted(deck, key=lambda c: c['card'].cmc)

    creatures     = []
    planeswalkers = []
    instants      = []
    sorceries     = []
    enchantments  = []
    artifacts     = []
    lands         = []
    other         = []

    for c in deck:
        if 'Creature' in c['card'].type:
            creatures.append(c)
        elif 'Land' in c['card'].type:
            lands.append(c)
        elif 'Planeswalker' in c['card'].type:
            planeswalkers.append(c)
        elif 'Instant' in c['card'].type:
            instants.append(c)
        elif 'Sorcery' in c['card'].type:
            sorceries.append(c)
        elif 'Enchantment' in c['card'].type:
            enchantments.append(c)
        elif 'Artifact' in c['card'].type:
            artifacts.append(c)
        else:
            if debug:
                raise AssertionError('did not find a section for card: %s'
                        %(c['card'].name,))
            else:
                other.append(c)

    if len(deck) != len(creatures)+len(planeswalkers)+len(instants)+ \
                    len(sorceries)+len(enchantments)+len(artifacts)+len(lands):
        names = [c['card'].name for c in deck]
        if debug:
            raise AssertionError('did not find a section for some cards: %s'
                    % (names,))

    # column widths
    lname = max([len(c['card'].name) for c in deck])
    lmana = 15

    # create new deck lines sorted by cmc, with lands last
    lines = []
    append = []

    def append_sec(l, s):
        """Append section to `lines`.

        :param list l: a subdeck as [{'card': Card, 'count': COUNT}, ...]
        :param str  s: category heading

        """
        if len(l) > 0:
            lines.append("{} {}".format(s, total_cards(l)))
            for c in l:
                lines.append(card_line_print(c, lname, lmana, ansi=ansi))
            lines.append('')

    append_sec(creatures, "Creatures")
    append_sec(planeswalkers, "Planeswalkers")
    append_sec(instants, "Instants")
    append_sec(sorceries, "Sorceries")
    append_sec(enchantments, "Enchantments")
    append_sec(artifacts, "Artifacts")
    append_sec(lands, "Lands")
    append_sec(other, "Other")

    lines.pop()

    return lines


def add_section(blist, section_nr):
    """Return `blist` with added section number `section_nr`.

    :param list blist:      list containing deck sections (e.g., a buffer list)
    :param int  section_nr: number of the section to add
    :raises ValueError:     if invalid section number

    If `blist` already contains section number `section_nr`, return `blist`.

    Sections:

        1   Main
        2   Sideboard
        3   Other

    """
    try:
        section_name = sections[section_nr]
    except KeyError as e:
        raise ValueError("invalid section number")
    next_sections = list(sections.values())[section_nr:]
    next_sections.append('----')
    r_start = re.compile(r'^{}(?:{})?'.format(section_name, r_count))
    r_end = r'^(?:{})(?:{})?'.format('|'.join(next_sections), r_count)

    # find (1) list index of next section or (2) last list index
    i_next = None
    for i, l in enumerate(blist):
        if re.match(r_start, l):
            return blist
        if re.match(r_end, l):
            i_next = i
            break

    if i_next == None:
        if blist == ['']:
            blist[0] = section_name
        else:
            blist.append(section_name)
    else:
        # if main_sectioned:
        #     blist.insert(i_next, '')
        # blist.insert(i_next, '')
        blist.insert(i_next, section_name)

    return blist


def add_to_section(blist, name, count, section_nr):
    """Add '`count` `name`' to section number `section_nr` in deck.

    :param list blist:      list containing deck sections (e.g., a buffer list)
    :param str  name:       name of card to add
    :param int  count:      how many `name`s to add
    :param int  section_nr: section number

    If section `section_nr` is not found. That section is created first.

    Sections:

        1   Main
        2   Sideboard
        3   Other

    """
    if not count: count = 1
    line = "{} {}".format(count, name)
    sec_lines = find_section(blist, section_nr)
    if sec_lines is not None:
        (firstline, lastline) = sec_lines
        (start_bl, end_bl) = surrounding_blanklines(blist[firstline:lastline+1])
        # first_card_line = firstline+start_bl
        first_card_line = firstline
        blist.insert(first_card_line+1, line)
    else:
        # add_section(blist, section_nr, main_sectioned=main_sectioned)
        add_section(blist, section_nr)
        add_to_section(blist, name, count, section_nr)

    return blist


def get_section(blist, index):
    """Return section number of line `index` or None if none.

    :param list blist:  list containing deck sections (e.g., a buffer list)
    :param int  index:  element index in `blist`
    :raises ValueError: if the index is out of bounds of `blist`

    Section number -1 refers to auto generated stats section.

    """
    if index < 0 or index > len(blist)-1:
        raise ValueError("buffer list does not contain index")
    sec_list = list(sections.values())+['----']
    r_section = re.compile(r'^({})(?:{})?'.format('|'.join(sec_list), r_count))
    section_nr = None
    i = index
    while i >= 0:
        match = r_section.match(blist[i])
        if match:
            section_name = match.group(1)
            if section_name == '----':
                return -1
            keys = list(sections.keys())
            values = list(sections.values())
            section_nr = keys[values.index(section_name)]
            break
        i -= 1
    return section_nr


def move_card(blist, index, section_nr, count=None):
    """Move deck line `index` to section number `section_nr`.

    :param list blist:      list containing deck sections (e.g., a buffer list)
    :param int  index:      element index in `blist`
    :param int  section_nr: section number
    :param int  count:      how many `name`s to move

    Sections:

        1   Main
        2   Sideboard
        3   Other

    """
    cur_section = get_section(blist, index)

    if cur_section == -1:
        return blist

    if cur_section == section_nr:
        return blist

    line = blist[index]
    card = get_deck([line])

    if card == []:
        return blist
    blist.pop(index)

    if count is None:
        count = card[0]['count']

    # update source line
    i_count = card[0]['count']-count
    name = card[0]['card'].name
    if i_count > 0:
        # updated_line = re.sub('^\d+', '%-2s'%(i_count,), line)
        updated_line = re.sub('^\d+', '%s'%(i_count,), line)
        blist.insert(index, updated_line)

    add_to_section(blist, name, count, section_nr)

    return blist


def move_cards(blist, indexes, section_nr):
    """Move deck lines `indexes` to section number `section_nr`.

    :param list blist:      list containing deck sections (e.g., a buffer list)
    :param list indexes:    list of indexes in `blist`
    :param int  section_nr: section number

    Sections:

        1   Main
        2   Sideboard
        3   Other

    """
    sec_m_range = None
    sec_s_range = None
    sec_o_range = None
    current_range = None
    ranges = []
    i_in_range = []

    # for each index, add it to a section
    for i in indexes:

        # if i is not in current section, loop until element is inserted
        while True:
            if current_range is None:
                # new section range
                cur_section = get_section(blist, i)
                if cur_section == -1:
                    break
                if cur_section is not None:
                    sec_name = sections[cur_section]
                    if cur_section == section_nr:
                        # discard index if it is already in target section
                        current_range = None
                        break
                    # note: starts on header
                    current_range = find_section(blist, cur_section)
                    cur_range_s = current_range[0]
                    cur_range_e = current_range[1]
                    if i == cur_range_s:
                        # skip section headers
                        break
                    if cur_range_s == cur_range_e:
                        # discard index it is an empty section
                        current_range = None
                        break
                    cur_range_s += 1
                else:
                    # not in section
                    sec_name = "None"
                    cur_range_s = i
                    cur_range_e = i

            if i >= cur_range_s and i <= cur_range_e:
                i_in_range.insert(0, i)
                break
            else:
                ranges.append(i_in_range)
                # range complete; iterate to find section of i
                current_range = None
                i_in_range = []
    ranges.append(i_in_range)
    ranges = [r for r in ranges if r != []]

    ranges.reverse()
    for i_list in ranges:
        subdeck = get_deck([blist[i] for i in i_list])
        for i in i_list:
            blist[i] = '\0'
        for c in subdeck:
            add_to_section(blist, c['card'].name, c['count'], section_nr)

    blist = [l for l in blist if l != '\0']
    return blist


def legal_formats(deck):
    """Return a set of legal formats for the deck `deck`.

    :param list deck: a deck as [{'card': Card, 'count': COUNT}, ...]

    Example return value:

        {'standard', 'vintage'}

    """
    if len(deck) == 0: return set()
    legal_fmts = set(SHOWN_FORMATS)
    for c in deck:
        cur = c['card'].formats
        if cur == None: cur = {}
        cur_fmts = {f for f in cur.keys() if cur[f] == 'Legal'}
        legal_fmts = legal_fmts & cur_fmts
    return legal_fmts


def legal_formats_print(legal_fmts):
    """Return a list of a formatted print of formats and their legal status.

    :param set legal_fmts: formats that are legal as {'FORMAT', ...}

    """
    deck_fmts = {f: 'Legal' for f in legal_fmts}
    fmts_print = mtgcard.util.legality_print(deck_fmts, ansi=False)
    return fmts_print


def devotion(deck):
    """Return a dict of devotion for each color in `deck`.

    :param list deck: a deck as [{'card': Card, 'count': COUNT}, ...]

    Example return value:

        {'W': 1, 'R': 1}

    """
    colors = {'W': 0, 'U': 0, 'B': 0, 'R': 0, 'G': 0, 'S': 0, 'C': 0}

    for c in deck:
        manacost = c['card'].manacost
        if manacost is None:
            continue
        match = re.findall('([WUBRGSC])(?:/([WUBRGSC]))?', manacost)
        if match:
            for t in match:
                for color in t:
                    if color:
                        colors[color] += 1 * c['count']
    colors = {k: v for k, v in colors.items() if v > 0}

    return colors


def devotion_print(devotion):
    """Return a print of deck devotion.

    :param dict devotion: devotion as {COLOR_LETTER: COUNT, ...}

    """
    total = sum(devotion.values())
    dev_print = []
    for color in devotion.keys():
        for k in ['W', 'U', 'B', 'R', 'G', 'C', 'S']:
            if color == k:
                dev_print.append("{:s}: {:<3d} ({:.0%})".format(color,
                    devotion[color], devotion[color]/total))
                break

    return dev_print


def deck_stats(deck):
    """Return cmc, avg_cmc, land count, and non-land count for deck `deck`.

    :param list deck: a deck as [{'card': Card, 'count': COUNT}, ...]

    """
    cmc = 0
    nonlands = 0
    lands = 0
    for c in deck:
        cost = int(c['card'].cmc)
        if cost > 6: cost = 6
        cmc += c['count'] * cost
        if c['card'].types[0] != 'Land':
            nonlands += c['count']
        else:
            lands += c['count']
    return {
        "cmc": cmc,
        "avg_cmc": cmc / nonlands if nonlands > 0 else 0,
        "lands": lands,
        "nonlands": nonlands,
    }


def process_deck(blist, main_sectioned=False, process_other=True, ansi=True):
    """Return processed deck as a list with stats.

    :param list blist:          list containing deck sections (e.g., a buffer list)
    :param bool main_sectioned: whether main deck is sectioned by card type
    :param bool process_other:  whether to process section Other
    :param bool ansi:           whether color

    """
    # get buffer as list
    b = blist

    # initialize
    post_deck_lines = []

    ################
    #  find other  #
    ################

    line_numbers = find_section(b, 3)
    if line_numbers is None:
        other_deck = []
        other_deck_lines = None
    else:
        (firstline, lastline) = line_numbers
        if lastline == firstline:  # empty
            other_deck = []
            other_deck_lines = []
            other_deck_count = 0
        else:
            # get deck lines
            (start_bl, end_bl) = surrounding_blanklines(b[firstline:lastline+1])
            other_deck_lines = b[firstline+1+start_bl:lastline+1-end_bl]

            # get deck
            other_deck = get_deck(other_deck_lines,
                    warnings=process_other)

            # get deck count
            other_deck_count = total_cards(other_deck)

            # create deck lines sorted by cmc, with 0 cmc last
            other_deck_lines = std_deck(other_deck, add_setcode=add_setcode)

        header = [hdr_fmt.format(DECK_OTHER, other_deck_count,
                                     hdr_fmt=hdr_fmt)]
        if process_other:
            b[firstline:lastline+1] = header + [''] + other_deck_lines + ['']
        else:
            b[firstline] = header[0]


    ####################
    #  find sideboard  #
    ####################

    line_numbers = find_section(b, 2)
    if line_numbers is None:
        sb_deck = []
        sb_deck_lines = None
    else:
        (firstline, lastline) = line_numbers
        if lastline == firstline:  # empty
            sb_deck = []
            sb_deck_lines = []
            sb_deck_count = 0
        else:
            # get deck lines
            (start_bl, end_bl) = surrounding_blanklines(b[firstline:lastline+1])
            sb_deck_lines = b[firstline+1+start_bl:lastline+1-end_bl]

            # get deck
            sb_deck = get_deck(sb_deck_lines)

            # get deck count
            sb_deck_count = total_cards(sb_deck)

            # create deck lines sorted by cmc, with 0 cmc last
            if not main_sectioned:
                sb_deck_lines = std_deck(sb_deck, add_setcode=add_setcode)
            else:
                sb_deck_lines = std_deck(sb_deck, add_setcode=add_setcode,
                        mana=True, ansi=ansi)

            # create post deck lines sorted by cmc, with 0 cmc last
            if not main_sectioned:
                post_deck_lines = std_deck(sb_deck, add_setcode=add_setcode,
                        mana=True, ansi=ansi)
            else:
                post_deck_lines = std_deck(sb_deck, add_setcode=add_setcode)

        header = [hdr_fmt.format(DECK_SB, sb_deck_count,
                                     hdr_fmt=hdr_fmt)]
        b[firstline:lastline+1] = header + [''] + sb_deck_lines + ['']


    ####################
    #  find main deck  #
    ####################

    line_numbers = find_section(b, 1)
    if other_deck_lines is None and sb_deck_lines is None and not line_numbers:
        # add main, if there are no sections and there are cards
        def has_card_line(b):
            for l in b:
                if re_card_ln.match(l):
                    return True
            return False
        if has_card_line(blist):
            b.insert(0, DECK_MAIN)
            line_numbers = find_section(b, 1)

    if line_numbers is None:
        main_deck = []
        main_deck_lines = None
    else:
        (firstline, lastline) = line_numbers
        if lastline == firstline:  # empty
            main_deck = []
            main_deck_lines = []
            main_deck_count = 0
        else:
            # get deck lines
            (start_bl, end_bl) = surrounding_blanklines(b[firstline:lastline+1])
            main_deck_lines = b[firstline+1+start_bl:lastline+1-end_bl]

            # get deck
            main_deck = get_deck(main_deck_lines, verbose=True)

            # get deck count
            main_deck_count = total_cards(main_deck)

            # get deck legal formats
            main_fmts = legal_formats(main_deck)
            main_fmts_print = legal_formats_print(main_fmts)

            main_dev = devotion(main_deck)
            main_dev_print = devotion_print(main_dev)

            # create deck lines sorted by cmc, with 0 cmc last
            if not main_sectioned:
                main_deck_lines = std_deck(main_deck, add_setcode=add_setcode)
            else:
                main_deck_lines = sectioned_deck(main_deck, ansi=ansi)
                main_deck_lines.append('')

            # create post deck lines sorted by cmc, with 0 cmc last
            if len(post_deck_lines) != 0:
                post_deck_lines.insert(0, '')
            if not main_sectioned:
                post_deck_lines.insert(0, '')
                post_deck_lines = sectioned_deck(main_deck, ansi=ansi) + post_deck_lines
            else:
                post_deck_lines = std_deck(main_deck, add_setcode=add_setcode) + post_deck_lines

            # add blank space before post deck
            post_deck_lines.insert(0, '')
            post_deck_lines.insert(0, '')

        header = [hdr_fmt.format(DECK_MAIN, main_deck_count,
                                     hdr_fmt=hdr_fmt)]
        b[firstline:lastline+1] = header + [''] + main_deck_lines + ['']


        ###########
        #  stats  #
        ###########

        # add a separator for generated stats
        sep = '----'
        try: sepline = b[:].index(sep)+1
        except:
            if not re.match('^\s*$', b[-1]): b.append('')
            b.append(sep)
            sepline = len(b)
        b[sepline:] = []


        # stats
        stats = deck_stats(main_deck)

        # add mana curve
        curve = []
        curve.append('')
        curve.append('mana curve:')
        curve.extend(['  '+l for l in print_mana_curve(mana_curve(main_deck))])
        curve.append('')
        b.extend(curve)

        if main_deck_lines:
            # card counts
            b.append('cards:')
            b.append('  total: {:d}'.format( total_cards(main_deck) ))
            b.append('  non-lands: {:d}'.format( stats['nonlands'] ))
            b.append('  lands: {:d}'.format( stats['lands'] ))
            b.append('')
            # mana
            b.append('mana:')
            b.append('  cmc: {:.2f}'.format(stats['cmc']))
            b.append('  avg cmc: {:.2f}'.format(stats['avg_cmc']))
            b.append('')
            # add devotion for main
            b.append('devotion:')
            b.extend(['  '+l for l in main_dev_print])
            b.append('')
            # add legal formats for main
            b.append('legalities:')
            b.extend(['  '+l for l in main_fmts_print])

        # add post deck
        b = b + post_deck_lines

    if len(b) > 0 and b[-1] == '':
        b.pop()

    # return list
    return b
