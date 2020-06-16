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

" Vim filetype plugin file
" Maintainer:       yoshi111@tutanota.com


if exists("b:did_ftplugin") && b:did_ftplugin
  finish
endif
let b:did_ftplugin = 1

let s:cpo_save = &cpo
set cpo&vim


" PLUGIN BEGIN

let b:undo_ftplugin = "setl wrap< cocu< cole< fdm< fdl<"
setlocal nowrap concealcursor=nv conceallevel=2 foldmethod=expr foldlevel=99


"-------------------------------------------------------------------------------
"                                Initialization                                 
"-------------------------------------------------------------------------------

if !mtg#init_python()
    echoerr "not initialized"
    finish
endif


"-------------------------------------------------------------------------------
"                                   Options                                     
"-------------------------------------------------------------------------------

let g:mtg_no_maps = get(g:, 'mtg_no_maps', 0)
let g:mtg_ansi = get(g:, 'mtg_ansi', 1)
let g:mtg_order = get(g:, 'mtg_order', 'cmc')
let g:mtg_main_sectioned = get(g:, 'mtg_main_sectioned', 1)
let g:mtg_process_other = get(g:, 'mtg_process_other', 0)
let g:mtg_multiple_search_buffers = get(g:, 'mtg_multiple_search_buffers', 0)
let g:mtg_default_format = get(g:, 'mtg_default_format', '')
let g:mtg_preview_show_price = get(g:, 'mtg_preview_show_price', 1)
let g:mtg_preview_verbose = get(g:, 'mtg_preview_verbose', 0)

" mappings
let g:mtg_process_command = get(g:, 'g:mtg_process_command', '<localleader>p')
let g:mtg_add_command = get(g:, 'g:mtg_add_command', '<localleader>a')
let g:mtg_preview_command = get(g:, 'mtg_preview_command', '<enter>')
let g:mtg_vpreview_command = get(g:, 'mtg_vpreview_command', '<enter>')
let g:mtg_prev_command = get(g:, 'mtg_prev_command', '<up>')
let g:mtg_next_command = get(g:, 'mtg_next_command', '<down>')
let g:mtg_move_card_to_main_command = get(g:, 'mtg_move_card_to_main_command', 'gm')
let g:mtg_move_card_to_sb_command = get(g:, 'mtg_move_card_to_sb_command', 'gs')
let g:mtg_move_card_to_other_command = get(g:, 'mtg_move_card_to_other_command', 'go')
let g:mtg_move_cards_to_main_command = get(g:, 'mtg_move_cards_to_main_command', 'gm')
let g:mtg_move_cards_to_sb_command = get(g:, 'mtg_move_cards_to_sb_command', 'gs')
let g:mtg_move_cards_to_other_command = get(g:, 'mtg_move_cards_to_other_command', 'go')
let g:mtg_search_input_command = get(g:, 'mtg_search_input_command', '<localleader>s')
let g:mtg_search_input_rev_command = get(g:, 'mtg_search_input_rev_command', '<localleader>r')
let g:mtg_set_order_command = get(g:, 'mtg_set_order_command', '<localleader>o')
let g:mtg_set_format_command = get(g:, 'mtg_set_format_command', '<localleader>f')


"-------------------------------------------------------------------------------
"                       Expose our commands to the user                         
"-------------------------------------------------------------------------------

" commands
command! -buffer MTGDeck call mtg#process_deck()
command! -buffer -nargs=1 -bang MTGSearch call mtg#card_search(
            \ <f-args>,
            \ ('<bang>'=='!'?1:0))
command! -buffer MTGOrder call mtg#set_order()
command! -buffer MTGFormat call mtg#set_format()
command! -buffer MTGSwitch call mtg#switch()
command! -buffer MTGUpdate call mtg#update()

" mappings
if ! g:mtg_no_maps
    if len(g:mtg_preview_command)
        execute 'nnoremap <silent> <buffer> '.g:mtg_process_command.' :call mtg#process_deck()<cr>'
    endif
    if len(g:mtg_add_command)
        execute 'nnoremap <silent> <buffer> '.g:mtg_add_command.' :call mtg#add()<cr>'
    endif
    if len(g:mtg_preview_command)
        execute 'nnoremap <silent> <buffer> '.g:mtg_preview_command.' :call mtg#card_preview_line()<cr>'
    endif
    if len(g:mtg_vpreview_command)
        execute 'vnoremap <silent> <buffer> '.g:mtg_vpreview_command.' y:call mtg#card_preview(@")<cr>'
    endif
    if len(g:mtg_prev_command)
        execute 'nnoremap <silent> <buffer> '.g:mtg_prev_command.' :call mtg#prev_card()<cr>'
    endif
    if len(g:mtg_next_command)
        execute 'nnoremap <silent> <buffer> '.g:mtg_next_command.' :call mtg#next_card()<cr>'
    endif
    if len(g:mtg_move_card_to_main_command)
        execute 'nnoremap <silent> <buffer> '.g:mtg_move_card_to_main_command.' :<c-u>call mtg#move_card(line("."), 1, v:count)<cr>'
    endif
    if len(g:mtg_move_card_to_sb_command)
        execute 'nnoremap <silent> <buffer> '.g:mtg_move_card_to_sb_command.' :<c-u>call mtg#move_card(line("."), 2, v:count)<cr>'
    endif
    if len(g:mtg_move_card_to_other_command)
        execute 'nnoremap <silent> <buffer> '.g:mtg_move_card_to_other_command.' :<c-u>call mtg#move_card(line("."), 3, v:count)<cr>'
    endif
    if len(g:mtg_move_cards_to_main_command)
        execute 'vnoremap <silent> <buffer> '.g:mtg_move_cards_to_main_command.' :call mtg#move_cards(1)<cr>'
    endif
    if len(g:mtg_move_cards_to_sb_command)
        execute 'vnoremap <silent> <buffer> '.g:mtg_move_cards_to_sb_command.' :call mtg#move_cards(2)<cr>'
    endif
    if len(g:mtg_move_cards_to_other_command)
        execute 'vnoremap <silent> <buffer> '.g:mtg_move_cards_to_other_command.' :call mtg#move_cards(3)<cr>'
    endif
    if len(g:mtg_search_input_command)
        execute 'nnoremap <silent> <buffer> '.g:mtg_search_input_command.' :call mtg#card_search_input(0)<cr>'
    endif
    if len(g:mtg_search_input_rev_command)
        execute 'nnoremap <silent> <buffer> '.g:mtg_search_input_rev_command.' :call mtg#card_search_input(1)<cr>'
    endif
    if len(g:mtg_set_order_command)
        execute 'nnoremap <silent> <buffer> '.g:mtg_set_order_command.' :call mtg#set_order()<cr>'
    endif
    if len(g:mtg_set_format_command)
        execute 'nnoremap <silent> <buffer> '.g:mtg_set_format_command.' :call mtg#set_format()<cr>'
    endif
endif


"-------------------------------------------------------------------------------
"                                   folding                                     
"-------------------------------------------------------------------------------

set foldexpr=mtg#fold(v:lnum)
set foldtext=mtg#foldtext()

" PLUGIN END


let &cpo = s:cpo_save
unlet s:cpo_save
