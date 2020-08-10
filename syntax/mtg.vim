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

hi W cterm=bold ctermfg=230 guifg=#FFFFD7
hi U cterm=bold ctermfg=153 guifg=#AFD7FF
hi B cterm=bold ctermfg=247 guifg=#9E9E9E
hi R cterm=bold ctermfg=216 guifg=#FFAF87
hi G cterm=bold ctermfg=115 guifg=#87D7AF
hi C cterm=bold ctermfg=253 guifg=#DADADA

hi MTGCommon       cterm=bold ctermfg=231 guifg=#FFFFFF
hi MTGUncommon     cterm=bold ctermfg=152 guifg=#AFD7D7
hi MTGRare         cterm=bold ctermfg=222 guifg=#FFD787
hi MTGMythic       cterm=bold ctermfg=208 guifg=#FF8700
hi MTGUncommonMid  cterm=bold ctermfg=110 guifg=#87AFD7
hi MTGRareMid      cterm=bold ctermfg=220 guifg=#FFD700
hi MTGMythicMid    cterm=bold ctermfg=166 guifg=#D75F00
hi MTGUncommonDark cterm=bold ctermfg=67  guifg=#5F87AF
hi MTGRareDark     cterm=bold ctermfg=136 guifg=#AF8700
hi MTGMythicDark   cterm=bold ctermfg=160 guifg=#D70000

hi MTGDark    cterm=bold ctermfg=243 guifg=#767676
hi MTGCoreExp cterm=bold ctermfg=146 guifg=#AFAFD7
hi MTGBlack              ctermfg=0   guifg=#585858

hi MTGLegal      ctermfg=28 guifg=#008700
hi MTGBanned     ctermfg=1  guifg=#626262
hi MTGRestricted ctermfg=25 guifg=#005FAF
hi MTGNotLegal   ctermfg=0  guifg=#585858

syn match Conceal '\e\[0m' conceal

syn region W matchgroup=Conceal start='\zs\e\[1;38;5;230m' end='\ze\e\[0m' concealends
syn region U matchgroup=Conceal start='\zs\e\[1;38;5;153m' end='\ze\e\[0m' concealends
syn region B matchgroup=Conceal start='\zs\e\[1;38;5;247m' end='\ze\e\[0m' concealends
syn region R matchgroup=Conceal start='\zs\e\[1;38;5;216m' end='\ze\e\[0m' concealends
syn region G matchgroup=Conceal start='\zs\e\[1;38;5;115m' end='\ze\e\[0m' concealends
syn region C matchgroup=Conceal start='\zs\e\[1;38;5;253m' end='\ze\e\[0m' concealends

syn region MTGCommon       matchgroup=Conceal start='\zs\e\[1;38;5;231m' end='\ze\e\[' concealends
syn region MTGUncommon     matchgroup=Conceal start='\zs\e\[1;38;5;152m' end='\ze\e\[' concealends
syn region MTGRare         matchgroup=Conceal start='\zs\e\[1;38;5;222m' end='\ze\e\[' concealends
syn region MTGMythic       matchgroup=Conceal start='\zs\e\[1;38;5;208m' end='\ze\e\[' concealends
syn region MTGUncommonMid  matchgroup=Conceal start='\zs\e\[1;38;5;110m' end='\ze\e\[' concealends
syn region MTGRareMid      matchgroup=Conceal start='\zs\e\[1;38;5;220m' end='\ze\e\[' concealends
syn region MTGMythicMid    matchgroup=Conceal start='\zs\e\[1;38;5;166m' end='\ze\e\[' concealends
syn region MTGUncommonDark matchgroup=Conceal start='\zs\e\[1;38;5;67m' end='\ze\e\[' concealends
syn region MTGRareDark     matchgroup=Conceal start='\zs\e\[1;38;5;136m' end='\ze\e\[' concealends
syn region MTGMythicDark   matchgroup=Conceal start='\zs\e\[1;38;5;160m' end='\ze\e\[' concealends

syn region MTGDark matchgroup=Conceal start='\zs\e\[1;38;5;243m' end='\ze\e\[' concealends
syn region MTGCoreExp matchgroup=Conceal start='\zs\e\[1;38;5;146m' end='\ze\e\[' concealends
syn region MTGBlack matchgroup=Conceal start='\zs\e\[0;38;5;0m' end='\ze\e\[' concealends

syn region MTGLegal matchgroup=Conceal start='\zs\e\[0;38;5;28m' end='\ze\e\[' concealends
syn region MTGBanned matchgroup=Conceal start='\zs\e\[0;38;5;1m' end='\ze\e\[' concealends
syn region MTGRestricted matchgroup=Conceal start='\zs\e\[0;38;5;25m' end='\ze\e\[' concealends
syn region MTGNotLegal matchgroup=Conceal start='\zs\e\[0;38;5;0m' end='\ze\e\[' concealends

let b:current_syntax = "mtg"

" vim: ts=4
