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


function! mtg#card#ansi_paste() abort
    let l:clipboard = getreg(v:register, 1, 1)
    let l:l = line('.')
    for l:i in l:clipboard
        call setline(l:l, getline(l:l)." ".l:i)
        let l:l += 1
    endfor
endfunction

function! mtg#card#strip_ansi(string) abort
    let l:noansi = substitute(a:string, '\e\[[0-?]*[ -/]*[@-~]', '', 'g')
    return l:noansi
endfunction


function! mtg#card#charcol() abort
    let l:line_to_cur = getline('.')[0:col('.')-1]
    let l:line_to_cur = substitute(l:line_to_cur, '\e[^m]*m\=$', '', 'g')
    let l:noansi = mtg#card#strip_ansi(l:line_to_cur)
    let l:line_to_cur = substitute(l:noansi, '\v\p@!.', '', 'g')
    return strchars(noansi)
endfunction


function! mtg#card#single_row() abort
    " return 1 if top of visual area encompases whole line
    let l:top = min([line('.'),line('v')])
    let l:bot = max([line('.'),line('v')])
    let l:left = min([col('.'),col('v')])
    let l:right = max([col('.'),col('v')])
    if l:left == 1 && l:right == len(getline(l:top))-2 && l:right == len(getline(l:bot))-2
        return 1
    else
        return 0
    endif
endfunction


function! mtg#card#go_same_col(r, opts) abort
    " let icol = virtcol('.')
    let l:icol = mtg#card#charcol()
    let l:top = search('\%'.l:icol.'v'.a:r, 'W'.a:opts)
    if l:top | exe 'norm! '.l:icol.'|' | endif
endfunction


function! mtg#card#bot() abort
    return search('─*└', 'Wcnb', line('.'))
endfunction


function! mtg#card#top() abort
    return search('─*┌', 'Wcnb', line('.'))
endfunction


function! mtg#card#to_left()
    call mtg#card#go_same_col("[┌─┐]", "cb")
    call search("┌", "b")
endfunction


function! mtg#card#to_right()
    call mtg#card#go_same_col("[┌─┐]", "cb")
    call search("┌")
endfunction


function! mtg#card#to_up() abort
    if !mtg#card#top()
        call mtg#card#go_same_col('[┌─┐]', 'b')
    else
        call mtg#card#go_same_col('[┌─┐]', 'b')
    endif
endfunction


function! mtg#card#to_down() abort
    if !mtg#card#bot()
        call mtg#card#go_same_col('\v[└─┘]', '')
    endif
    call mtg#card#go_same_col('\v%(┌─*)@<=[─┐]|┌', 'c')
endfunction


function! mtg#card#column() abort
    let l:line_to_cur = getline('.')[0:col('.')+1]
    let l:curchar = matchstr(getline('.'), '.', col('.')-1)
    if l:curchar =~ '[┌┐└┘─]'
        let l:left_edges = substitute(l:line_to_cur, '[^└┌]', '', 'g')
        let l:count =  strchars(l:left_edges)
        return l:count
    else
        let l:left_edges = substitute(l:line_to_cur, '[^│]', '', 'g')
        let l:count =  strchars(l:left_edges)
        if l:count % 2 == 0
            if l:curchar != '│'
                " cursor not on a card
                return 0
            endif
        endif
        return float2nr(ceil(l:count/2.0))
    endif
endfunction


function! mtg#card#get_name() abort
    norm mz
    call mtg#card#go_same_col('[┌─┐]', 'cb')
    call search('┌', 'Wcb', line('.'))
    let l:cardcol = mtg#card#column()
    norm! j0
    let l:line = getline('.')
    let l:name = matchstr(l:line, '\v^'.repeat('│[^│]+│\s*', l:cardcol-1).'│\zs.{-}\ze  ')
    norm `z
    return l:name
endfunction
