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

"""The Python part for the card filetype."""


import re
from os import path
import vim
import mtgcard.mtgcard
import mtgcard.parser
import mtgcard.util
from vim_mtg import deck
from vim_mtg.vim_interface import vim_error, vim_warning, settings

from pprint import pprint


def list_names(format=None):
    """Return a list of all card names, or card names in `format` if specified.

    :param str format: MTG format

    Formats:

        standard
        pioneer
        modern
        commander
        brawl
        pauper
        legacy
        vintage

    """
    db = mtgcard.mtgdb.Interface()
    if format:
        query = 'format:%s' % (format,)
    else:
        query = ''
    nameslist = mtgcard.mtgcard.list_cards(db, query, onlynames=True, onename=True)[0]
    if nameslist:
        nameslist = nameslist.splitlines()
        return nameslist


def preview_line(line, prevfile=None, verbose=False, ansi=True):
    """Preview card on `line` in preview window.

    :param int  line:     line of card (e.g., '1 Black Lotus')
    :param str  prevfile: preview file to use (default: automatically create)
    :param bool verbose:  whether to display extra information in preview
    :param bool ansi:     whether color

    """
    match = deck.re_card_ln.match(line)
    if match:
        name = match.group(2)
        setcode = match.group(3)
        preview(name, setcode, verbose=verbose, ansi=ansi)
    else:
        vim_warning("card not found")


def preview(name, setcode=None, prevfile=None, verbose=False, ansi=True):
    """Preview card `name` in preview window.

    :param str  name:     name of card to preview
    :param str  setcode:  set code of card to preview
    :param str  prevfile: preview file to use (default: automatically create)
    :param bool verbose:  whether to display extra information in preview
    :param bool ansi:     whether color

    """
    db = mtgcard.mtgdb.Interface()
    show_price = settings.get('preview_show_price', 'bool')

    if show_price:
        card = db.get_card(name, setcode, verbose=True)
    else:
        card = db.get_card(name, setcode)

    if verbose:
        card_print = mtgcard.mtgcard.get_and_print_card(db, card=card,
                verbose=True, ansi=ansi)
    else:
        card_print = card.print_card(ansi=ansi)

    if card.layout in ('transform', 'meld') and not verbose:
        other_print = mtgcard.util.get_transform_meld_sideb(card).print_card(ansi=ansi)
        card_print += '\n' + other_print

    if card_print is not None:
        card_print = card_print.splitlines()
    else:
        vim_error("card not found")
        return None

    if prevfile is None:
        prevfile = vim.eval("tempname().'-mtg_card'")
    # if name and buf.options['ft'] == 'deck':
    if name:
        vim.command('silent! vert pedit! '+prevfile)
        vim.command('silent! wincmd P')
        if vim.current.window.options['previewwindow']:

            vim.current.buffer.options['modifiable'] = True
            vim.current.buffer.options['readonly']   = False

            # format START
            vim.current.buffer.options['ft'] = 'mtg'
            vim.command('doautocmd filetype')
            vim.current.window.options['number'] = False
            vim.current.window.options['wrap'] = False
            try:
                if verbose:
                    vim.options['winwidth'] = 72
                    # vim.options['winminwidth'] = 72
                else:
                    # vim.options['winminwidth'] = 36
                    vim.options['winwidth'] = 36
            except vim.error as e:
                vim_error(str(e))

            vim.current.buffer[:] = card_print
            if show_price:
                if card.price is not None:
                    price = '${:.2f}'.format(card.price * mtgcard.settings.US_TO_CUR_RATE)
                else:
                    price = ''
                vim.current.window.options['statusline'] = "[Preview] {}: {}".format(
                    mtgcard.settings.CURRENCY, price)
            else:
                vim.current.window.options['statusline'] = "[Preview]"

            vim.command('exe "vert resize ".&winwidth')
            vim.command('nnoremap <silent> <buffer> q <c-w>c')
            vim.command('''
                    nnoremap <silent> <buffer> t :let g:mtg_preview_verbose = <c-r>=g:mtg_preview_verbose ? 0 : 1<cr><cr>:call mtg#card_preview("'''+name+'''")<cr><c-w>p:exe 'vert resize '.&winwidth<cr>
            '''.strip())
            # format END

            vim.current.buffer.options['buftype']    = 'nofile'
            vim.current.buffer.options['bufhidden']  = 'wipe'
            vim.current.buffer.options['buflisted']  = False
            vim.current.buffer.options['swapfile']   = False
            vim.current.buffer.options['modifiable'] = False
            vim.current.buffer.options['readonly']   = True
            vim.current.buffer.options['modified']   = False

            vim.command( 'silent! wincmd p' )

            return True


def search(buf, query, format=None, order='cmc', reverse=False, searchfile=None,
        ansi=True):
    """List card images in a split buffer or None on fail.

    :param vim.buffer buf:        deck buffer
    :param str        query:      search query
    :param str        format:     format to search
    :param str        order:      sort order (cmc, name, or price)
    :param bool       reverse:    whether to reverse order
    :param str        searchfile: search file path
    :param bool       ansi:       whether color

    """
    db = mtgcard.mtgdb.Interface()
    # add format if available
    fquery = query
    if format:
        if query:
            fquery = 'format:%s %s' % (format, fquery)
        else:
            fquery = 'format:%s' % (format,)

    # get cards from query
    try:
        pquery = mtgcard.parser.parser.parse(fquery)
    except ValueError as e:
       print(e)
       return None
    cards = db.get_cards(pquery, sort=order, reverse=reverse)
    if cards is None:
        print( "no cards found" )
        return None
    card_list = mtgcard.mtgcard.list_cards_images(cards, 4, image=False, ansi=ansi)

    # create new search file if non supplied
    if searchfile is None:
        searchfile = vim.eval("tempname().'-mtg_search'")

    # if `buf` is not a deck buffer, try to get deck buffer in search buffer
    # variable
    if buf.options['ft'].decode('utf-8') != 'deck':
        try:
            sbufnr = int(vim.eval(f'''bufnr('{searchfile}')'''))
            if sbufnr == -1:
                raise KeyError
            sbuf = vim.buffers[sbufnr]
            dbuf = int(sbuf.vars['mtg_deck_bufnr'])
            dline = int(sbuf.vars['mtg_deck_linenr'])
        except KeyError as e:
            vim_error('cannot find deck buffer -- try from a deck buffer')
            return None
    else:
        dbuf = int(buf.number)
        dline = vim.eval(f'getbufinfo({buf.number})[0].lnum'.strip())

    # open search window
    for w in vim.current.tabpage.windows:
        if w.buffer.name == searchfile:
            # close already open search buffer
            winnr = w.number
            vim.command(str(winnr)+'close')
    vim.command('silent! botright sview '+searchfile)

    # setup search window and load results
    if vim.current.buffer.name == searchfile:

        vim.current.buffer.options['modifiable'] = True
        vim.current.buffer.options['readonly']   = False

        # format START
        vim.current.buffer.vars['mtg_deck_bufnr'] = int(dbuf)
        vim.current.buffer.vars['mtg_deck_linenr'] = int(dline)
        vim.current.buffer.vars['mtg_prev_query'] = query
        vim.current.buffer.options['ft'] = 'mtg'
        vim.command('doautocmd filetype')
        # vim.current.window.options['number'] = False
        # vim.current.window.options['wrap'] = False

        vim.current.buffer[:] = card_list
        vim.current.window.options['statusline'] = "{} matches ({})%=%p%%".format(
                len(cards), fquery.strip())
        # format END

        vim.current.buffer.options['buftype']    = 'nofile'
        vim.current.buffer.options['bufhidden']  = 'hide'
        vim.current.buffer.options['buflisted']  = True
        vim.current.buffer.options['swapfile']   = False
        vim.current.buffer.options['modifiable'] = False
        vim.current.buffer.options['readonly']   = True
        vim.current.buffer.options['modified']   = False

        vim.command(
                'nnoremap <silent> <buffer> <enter> '
                ':call mtg#card_preview(mtg#card#get_name())<cr>')

        vim.command(
                'nnoremap <silent> <buffer> a :<c-u>let cnt = v:count1<cr>'
                ':call mtg#add_to_deck(mtg#card#get_name(), cnt, 1, '
                    '{"bufnr":'+str(dbuf)+', "linenr":'+str(dline)+'})<cr>')

        vim.command(
                'nnoremap <silent> <buffer> s :<c-u>let cnt = v:count1<cr>'
                ':call mtg#add_to_deck(mtg#card#get_name(), cnt, 2, '
                    '{"bufnr":'+str(dbuf)+', "linenr":'+str(dline)+'})<cr>')

        vim.command(
                'nnoremap <silent> <buffer> o :<c-u>let cnt = v:count1<cr>'
                ':call mtg#add_to_deck(mtg#card#get_name(), cnt, 3, '
                    '{"bufnr":'+str(dbuf)+', "linenr":'+str(dline)+'})<cr>')

        vim.command(
                'nnoremap <silent> <buffer> q <c-w>c')
