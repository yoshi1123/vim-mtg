" viMTG - The VIM 'Magic: The Gathering' deck builder.
" Copyright (C) 2020  yoshi1@tutanota.com
"
" viMTG is free software: you can redistribute it and/or modify
" it under the terms of the GNU General Public License as published by
" the Free Software Foundation, either version 3 of the License, or
" (at your option) any later version.
"
" viMTG is distributed in the hope that it will be useful,
" but WITHOUT ANY WARRANTY; without even the implied warranty of
" MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
" GNU General Public License for more details.
"
" You should have received a copy of the GNU General Public License
" along with viMTG.  If not, see <https://www.gnu.org/licenses/>.


"-------------------------------------------------------------------------------
"                                Initialization                                 
"-------------------------------------------------------------------------------

let s:autoload_path = expand('<sfile>:p:h')
let s:script_path = expand('<sfile>:p:h:h')

" persistant temp files
if ! exists('s:prevfile')
    let s:prevfile = tempname().'-mtg_card'
endif
if ! exists('s:searchfile')
    let s:searchfile = tempname().'-mtg_search'
endif

let s:_init_python = -1
function! mtg#init_python() abort
    " if initialized sucessfully, return 1, otherwise return 0

    if s:_init_python == -1
        let s:_init_python = 0

        """"""""""""""
        "  sys.path  "
        """"""""""""""
python3 << endOfPython
import sys
import os.path

python_path = os.path.join(vim.eval('s:script_path'), 'python')
try:
    sys.path.index(python_path)
except ValueError as e:
    sys.path.insert(0, python_path)

mtgcard_path = os.path.join(python_path, 'mtgcard')
try:
    sys.path.index(mtgcard_path)
except ValueError as e:
    sys.path.insert(0, mtgcard_path)
endOfPython

        """""""""""""
        "  imports  "
        """""""""""""

        python3 from vim_mtg import deck, card
        python3 from vim_mtg import vim_interface

    " else
    "     call mtg#warning("vim-mtg already initialized")
    endif

    " successfully initialized
    let s:_init_python = 1
    return s:_init_python
endfunction


function! mtg#reinit_python() abort
    " reload both vim and python scripts

    let s:_init_python = -1
    call mtg#init_python()

    exe 'so '.s:autoload_path.'/mtg/card.vim'
    exe 'so '.s:autoload_path.'/mtg/util.vim'
    py3 import importlib
    py3 import mtgcard
    py3 importlib.reload(mtgcard)
    py3 importlib.reload(deck)
    py3 importlib.reload(card)
    py3 importlib.reload(vim_interface)

    if &ft ==# 'deck'
        let b:did_ftplugin = 0
        set ft=deck
    elseif &ft ==# 'mtg'
        let b:did_ftplugin = 0
        set ft=mtg
    endif

endfunction


"---------------------------------------------------------------------------
"                             Python Functions                              
"---------------------------------------------------------------------------

function! mtg#process_deck() abort
python3 << endPython
# get settings
ansi = vim_interface.settings.get('ansi', 'bool')
main_sectioned = vim_interface.settings.get('main_sectioned', 'bool')
process_other = vim_interface.settings.get('process_other', 'bool')

# process buffer
try:
    b = deck.process_deck(list(vim.current.buffer),
        main_sectioned=main_sectioned, process_other=process_other, ansi=ansi)
except FileNotFoundError as e:
    vim_interface.vim_error("MTG database not found: run ':MTGUpdate'")
else:
    # update buffer
    if vim.current.buffer[:] != b:
        vim.current.buffer[:] = b
endPython
endfunction


function! mtg#card_preview_line() abort
python3 << endPython
verbose_print = vim_interface.settings.get('preview_verbose', 'bool')
ansi = vim_interface.settings.get('ansi', 'bool')
try:
    card.preview_line(vim.current.line, verbose=verbose_print, ansi=ansi)
except ValueError as e:
    vim_interface.vim_warning(str(e))
except FileNotFoundError as e:
    vim_interface.vim_error("MTG database not found: run ':MTGUpdate'")
endPython
endfunction


function! mtg#card_preview(name, ...) abort
    let l:setcode = get(a:000, 0, -1)
python3 << endPythong
verbose_print = vim_interface.settings.get('preview_verbose', 'bool')
ansi = vim_interface.settings.get('ansi', 'bool')
name = vim.eval("a:name")
setcode = vim.eval("get(a:000, 0, '')")
prevfile = vim.eval("s:prevfile")
if setcode == '': setcode = None
try:
    card.preview(name, setcode, prevfile, verbose=verbose_print, ansi=ansi)
except ValueError as e:
    vim_interface.vim_warning(str(e))
except FileNotFoundError as e:
    vim_interface.vim_error("MTG database not found: run ':MTGUpdate'")
endPythong
endfunction


function! mtg#card_search(query, reverse) abort
python3 << endPython
ansi = vim_interface.settings.get('ansi', 'bool')
order = vim_interface.settings.get('order', 'str')
format = vim_interface.settings.get('default_format', 'str')
query = vim.eval('a:query')
if not format:
    format=None
reverse = bool(int(vim.eval('a:reverse')))
multibuf = vim_interface.settings.get('multiple_search_buffers', 'bool')
if multibuf:
    # let card.search create a new file
    searchfile = None
else:
    searchfile = vim.eval("s:searchfile")
try:
    card.search(vim.current.buffer, query, format=format, order=order,
        reverse=reverse, searchfile=searchfile, ansi=ansi)
except FileNotFoundError as e:
    vim_interface.vim_error("MTG database not found: run ':MTGUpdate'")
endPython
endfunction


function! mtg#add_to_deck(name, count, section_nr, ...) abort
    let l:dict = get(a:000, 0, {})
python3 << endPython
name = vim.eval('a:name')
count = int(vim.eval('a:count'))
section_nr = int(vim.eval('a:section_nr'))

bufnr = int(vim.eval("get(l:dict, 'bufnr', -1)"))
linenr = int(vim.eval("get(l:dict, 'linenr', -1)"))
if bufnr == -1: bufnr = None
if linenr == -1: linenr = None

if bufnr is None:
    blist = list(vim.current.buffer[:])
    try:
        vim.current.buffer[:] = deck.add_to_section(blist, name, count, section_nr)
    except FileNotFoundError as e:
        vim_interface.vim_error("MTG database not found: run ':MTGUpdate'")
else:
    blist = list(vim.buffers[bufnr][:])
    try:
        vim.buffers[bufnr][:] = deck.add_to_section(blist, name, count, section_nr)
    except FileNotFoundError as e:
        vim_interface.vim_error("MTG database not found: run ':MTGUpdate'")
endPython
endfunction


function! mtg#move_card(line_nr, section_nr, ...) abort
python3 << endPython
index = int(vim.eval('a:line_nr'))-1
section_nr = int(vim.eval('a:section_nr'))
count = int(vim.eval('get(a:000, 0, 0)'))
if count == 0: count = None

# move card
try:
    b = deck.move_card(list(vim.current.buffer), index, section_nr, count=count)
except FileNotFoundError as e:
    vim_interface.vim_error("MTG database not found: run ':MTGUpdate'")
    vim.command("return 0")
except ValueError as e:
    vim_interface.vim_error(e)
    vim.command("return 0")
else:
    # update buffer
    if vim.current.buffer[:] != b:
        vim.current.buffer[:] = b
        # vim.current.window.cursor = (vim.current.window.cursor[0]+1, vim.current.window.cursor[1])
    vim.command("return 1")

endPython
endfunction


function! mtg#move_cards(section_nr) abort range
python3 << endPython
firstline = int(vim.eval('a:firstline'))
lastline = int(vim.eval('a:lastline'))
indexes = range(firstline-1,lastline+1-1)
section_nr = int(vim.eval('a:section_nr'))

# move cards
try:
    b = deck.move_cards(list(vim.current.buffer), indexes, section_nr)
except FileNotFoundError as e:
    vim_interface.vim_error("MTG database not found: run ':MTGUpdate'")
    vim.command("return 0")
except ValueError as e:
    vim_interface.vim_error(e)
    vim.command("return 0")
else:
    # update buffer
    if vim.current.buffer[:] != b:
        vim.current.buffer[:] = b
    vim.command("return 1")
endPython
endfunction


function! mtg#update() abort
python3 << endPython
import mtgcard.update
print("updating database...")
mtgcard.update.update_database(verbose=False)
print("update complete")
endPython
endfunction

"-------------------------------------------------------------------------------
"                                Vim Functions                                  
"-------------------------------------------------------------------------------

function! mtg#error(message) abort
    echohl Error | echo "error: ".a:message | echohl | exe "normal \<esc>"
endfunction

function! mtg#warning(message) abort
    echohl WarningMsg | echo "warning: ".a:message | echohl | exe "normal \<esc>"
endfunction

function! mtg#list_names() abort
    " cache to s:nameslist and use cache if 'format' is the same
    if ! exists('s:lastformat')
        let s:lastformat = ''
    endif
    if exists('s:curformat')
        let s:lastformat = s:curformat
    endif
    let s:curformat = g:mtg_default_format
    if s:curformat == s:lastformat && exists('s:nameslist')
        return s:nameslist
    else
        python3 << endOfPython
try:
    nameslist = card.list_names(vim.eval("s:curformat"))
except FileNotFoundError as e:
    vim.command("return -1")
endOfPython
        let s:nameslist = py3eval("nameslist")
        return s:nameslist
    endif
endfunction

function! mtg#reset_names_cache() abort
    unlet s:nameslist
endfunction

function! mtg#get_section() abort
    return py3eval('deck.get_section(vim.current.buffer[:], vim.current.window.cursor[0]-1)')
endfunction

function! mtg#add_to_current(name) abort
    " name, count, section_nr
    let l:section = mtg#get_section()
    if l:section == v:none
        call mtg#warning("no current section found")
        return 0
    endif
    call mtg#add_to_deck(a:name, 1, mtg#get_section())
endfunction

function! mtg#add() abort
    if exists('g:loaded_fzf') && g:loaded_fzf == 1
        let names = mtg#list_names()
        if type(names) == v:t_list
            call fzf#run({'source': names, 'sink': function('mtg#add_to_current'), 'down': '~40%'})
        else
            call mtg#error("MTG database not found: run ':MTGUpdate'")
        endif
    else
        call mtg#error("fzf plugin required")
    endif
endfunction

function! mtg#set_order() abort
    echo "current: ".g:mtg_order
    if match(buffer_name(''), '-mtg_search') > 0 && exists('b:mtg_prev_query')
        " in search buffer
        let l:keys = ['c', 'n', 'p', 's', 'C', 'N', 'P', 'S']
        let l:options = ['cmc (asc)', 'name (asc)', 'price (asc)', 'setcode (asc)',
                    \ 'cmc (desc)', 'name (desc)', 'price (desc)', 'setcode (desc)']
        let l:result = mtg#util#prompt('sort order', l:keys, l:options, 4)
        let l:new_value = matchstr(l:result, '^[^ ]\+')
        let l:order = matchstr(l:result, '(\zs[^)]\+\ze')
        let l:reverse = l:order ==# 'asc' ? 0 : 1
        if l:new_value != 'invalid'
            let g:mtg_order = l:new_value
        endif
        call mtg#card_search(b:mtg_prev_query, l:reverse)
    else
        let l:keys = ['c', 'n', 'p']
        let l:options = ['cmc', 'name', 'price', 'setcode']
        let l:new_value = mtg#util#prompt('order', l:keys, l:options)
        if l:new_value != 'invalid'
            let g:mtg_order = l:new_value
        endif
    endif
endfunction

function! mtg#set_format() abort
    echo "current: ".g:mtg_default_format
    let l:keys = ['s', 'p', 'm', 'c', 'b', 'a', 'l', 'v', 'n']
    let l:options = ['standard', 'pioneer', 'modern', 'commander', 'brawl', 'pauper', 'legacy', 'vintage', '']
    let l:new_value = mtg#util#prompt('default format', l:keys, l:options)
    if l:new_value != 'invalid'
        let g:mtg_default_format = l:new_value
    endif
endfunction

function! mtg#switch() abort
    let g:mtg_main_sectioned = g:mtg_main_sectioned ? 0 : 1
    MTGDeck
    if g:mtg_main_sectioned
        echo "Main sectioned"
    else
        echo "Main not sectioned"
    endif
endfunction

function! mtg#card_search_input(reverse) abort
    let l:default = g:mtg_default_format != "" ? printf(" (%s)", g:mtg_default_format) : ""
    let l:query = input("query".l:default.": ")
    call mtg#card_search(l:query, a:reverse)
endfunction

function! mtg#next_card() abort
    norm 0
    call search('\v^\d+%(\s=x)=\s{1,2}(.{-1,})\ze%( +([A-Z0-9]{3}))=%(  |$)', 'W')
    call mtg#card_preview_line()
endfunction

function! mtg#prev_card() abort
    norm 0
    call search('\v^\d+%(\s=x)=\s{1,2}(.{-1,})\ze%( +([A-Z0-9]{3}))=%(  |$)', 'bW')
    call mtg#card_preview_line()
endfunction

function! mtg#fold(lnum) abort
    let DECK_MAIN = 'Main'
    let DECK_SB = 'Sideboard'
    let DECK_OTHER = 'Other'
    let sections = '('.join([DECK_MAIN, DECK_SB, DECK_OTHER], '|').')'
    let s_count = '\d+'
    let r_section = printf('\v^%s\ze%( %s)=$', sections, s_count)
    let line = getline(a:lnum)
    if line =~ r_section
        return ">1"
    elseif line == '----'
        return ">1"
    else
        return "="
    endif
endfunction

function! mtg#foldtext() abort
    let line = getline(v:foldstart)
    let title = substitute(getline(v:foldstart), '$', ' ', '')

    let foldsize = (v:foldend - v:foldstart + 1)
    let linecount = '['.foldsize.' lines]'
    let line_dig = len(line('$'))

    " let title = line
    if line == '----'
        let title = 'Stats'
    endif

    return printf("+%s%".(line_dig+1)."s lines: %s", v:folddashes, foldsize, title)
endfunction
