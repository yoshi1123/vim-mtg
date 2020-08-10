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

" Vim syntax file
" Maintainer:       yoshi1@tutanota.com


" quit when a syntax file was already loaded
if exists("b:current_syntax")
  finish
endif


" mana
hi mtgW cterm=bold ctermfg=230
hi mtgU cterm=bold ctermfg=153
hi mtgB cterm=bold ctermfg=247
hi mtgR cterm=bold ctermfg=216
hi mtgG cterm=bold ctermfg=115
hi mtgC cterm=bold ctermfg=253
syn region mtgW matchgroup=Conceal start='\zs\e\[1;38;5;230m' end='\ze\e\[0m' concealends
syn region mtgU matchgroup=Conceal start='\zs\e\[1;38;5;153m' end='\ze\e\[0m' concealends
syn region mtgB matchgroup=Conceal start='\zs\e\[1;38;5;247m' end='\ze\e\[0m' concealends
syn region mtgR matchgroup=Conceal start='\zs\e\[1;38;5;216m' end='\ze\e\[0m' concealends
syn region mtgG matchgroup=Conceal start='\zs\e\[1;38;5;115m' end='\ze\e\[0m' concealends
syn region mtgC matchgroup=Conceal start='\zs\e\[1;38;5;253m' end='\ze\e\[0m' concealends
syn match Conceal '\e\[0m' conceal

" mana curve
hi mtgManaGraph ctermbg=Cyan
syn match mtgManaGraph ': [0-9][0-9 ] |\zs \+$'

" card type sections
hi mtgTypeSection ctermfg=DarkGray
for t in ['Creatures', 'Planeswalkers', 'Instants', 'Sorceries', 'Enchantments', 'Artifacts', 'Lands']
let r_section = printf('^%s \d\+$', t)
    exe 'syn match mtgTypeSection /'.r_section.'/'
endfor

" card type sections
hi link mtgDeckSection Title
hi link mtgDeckSectionCount Title
" hi mtgDeckSectionCount ctermfg=Gray
let DECK_MAIN = 'Main'
let DECK_SB = 'Sideboard'
let DECK_OTHER = 'Other'
let sections = '('.join([DECK_MAIN, DECK_SB, DECK_OTHER], '|').')'
let s_count = '\d+'
let r_section = printf('\v^%s\ze%( %s)=$', sections, s_count)
let r_section_count = printf('\v(^%s )@<=%s$', sections, s_count)
exe 'syn match mtgDeckSection /'.r_section.'/'
exe 'syn match mtgDeckSectionCount /'.r_section_count.'/'

" highlight in curly brackets
hi mtgCardName ctermfg=magenta
syn region mtgCardName matchgroup=Normal start='{\ze.*}' end='}' concealends

let b:current_syntax = "deck"

" vim: ts=4
