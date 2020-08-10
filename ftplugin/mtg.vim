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
" Maintainer:       yoshi1@tutanota.com


if exists("b:did_ftplugin") && b:did_ftplugin
  finish
endif
let b:did_ftplugin = 1

let s:cpo_save = &cpo
set cpo&vim


" PLUGIN BEGIN

let b:undo_ftplugin = "setl nu< wrap< cocu< cole< fo< so<"
setlocal nonumber nowrap concealcursor=nv conceallevel=2 formatoptions-=t
setlocal scrolloff=3


"-------------------------------------------------------------------------------
"                                   Options                                     
"-------------------------------------------------------------------------------

let g:mtg_no_maps = get(g:, 'mtg_no_maps', 0)

" mappings
let g:mtg_card_right_command = get(g:, 'mtg_card_right_command', '<c-l>')
let g:mtg_card_left_command = get(g:, 'mtg_card_left_command', '<c-h>')
let g:mtg_card_up_command = get(g:, 'mtg_card_up_command', '<c-k>')
let g:mtg_card_down_command = get(g:, 'mtg_card_down_command', '<c-j>')
let g:mtg_ansi_paste_command = get(g:, 'g:mtg_ansi_paste_command', '<localleader>p')

let g:mtg_search_input_command = get(g:, 'mtg_search_input_command', '<localleader>s')
let g:mtg_search_input_rev_command = get(g:, 'mtg_search_input_rev_command', '<localleader>r')
let g:mtg_set_order_command = get(g:, 'mtg_set_order_command', '<localleader>o')
let g:mtg_set_format_command = get(g:, 'mtg_set_format_command', '<localleader>f')

"-------------------------------------------------------------------------------
"                       Expose our commands to the user                         
"-------------------------------------------------------------------------------

" commands
command! -buffer -nargs=1 -bang MTGSearch call mtg#card_search(
            \ <f-args>,
            \ ('<bang>'=='!'?1:0))
command! -buffer MTGOrder call mtg#set_order()

" mappings
if ! g:mtg_no_maps
    if len(g:mtg_ansi_paste_command)
        execute 'nnoremap <buffer> '.g:mtg_ansi_paste_command.' :call mtg#card#ansi_paste()<cr>'
    endif
    if len(g:mtg_card_left_command)
        execute 'nnoremap <silent> <buffer> '.g:mtg_card_left_command.' :call mtg#card#to_left()<cr>'
    endif
    if len(g:mtg_card_right_command)
        execute 'nnoremap <silent> <buffer> '.g:mtg_card_right_command.' :call mtg#card#to_right()<cr>'
    endif
    if len(g:mtg_card_up_command)
        execute 'nnoremap <silent> <buffer> '.g:mtg_card_up_command.' :call mtg#card#to_up()<cr>'
    endif
    if len(g:mtg_card_down_command)
        execute 'nnoremap <silent> <buffer> '.g:mtg_card_down_command.' :call mtg#card#to_down()<cr>'
    endif

    " search
    if len(g:mtg_search_input_command)
        execute 'nnoremap <buffer> '.g:mtg_search_input_command.' :call mtg#card_search_input(0)<cr>'
    endif
    if len(g:mtg_search_input_rev_command)
        execute 'nnoremap <buffer> '.g:mtg_search_input_rev_command.' :call mtg#card_search_input(1)<cr>'
    endif
    if len(g:mtg_set_order_command)
        execute 'nnoremap <buffer> '.g:mtg_set_order_command.' :call mtg#set_order()<cr>'
    endif
    if len(g:mtg_set_format_command)
        execute 'nnoremap <buffer> '.g:mtg_set_format_command.' :call mtg#set_format()<cr>'
    endif
endif

" PLUGIN END


let &cpo = s:cpo_save
unlet s:cpo_save
