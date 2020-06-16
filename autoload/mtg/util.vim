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


function! mtg#util#prompt(name, keys, options, ...) abort
    let l:nr_rows = get(a:000, 0, 4)
    let l:prompt = ""
    let l:prompt .= "set ".a:name.":\n"

    " divide options into a list of l:nr_rows item lists
    if len(a:keys) > 0 && len(a:keys) == len(a:options)
        let l:opts = []
        " let l:keys = keys(a:options)
        let l:keys = []
        let l:max = 0
        for i in range(len(a:keys))
            let l:key = a:keys[i]
            let l:value = a:options[i]
            let l:max = max([len(l:value), l:max])
            if i % l:nr_rows == 0
                call add(l:keys, [])
                call add(l:opts, [])
            endif
            call add(l:keys[-1], l:key)
            call add(l:opts[-1], l:value)
        endfor
    else
        return 0
    endif

    " make prompt of l:nr_rows row columns
    for i in range(len(l:keys[0]))
        for j in range(len(l:keys))
            if exists('l:keys[j][i]')
                let key = l:keys[j][i]
                let opt = l:opts[j][i]
                if opt == ''
                    let opt = 'none'
                endif
                let l:prompt .= printf(" (%s) %-".(l:max+3)."s", key, opt)
            endif
        endfor
        let l:prompt .= "\n"
    endfor

    let l:result = 'invalid'
    let l:formats = {}
    for i in range(len(a:keys))
        let l:formats[char2nr(a:keys[i])] = a:options[i]
    endfor
    let l:formats[27] = 'esc'
    echo l:prompt
    while 1
        " let l:selection = nr2char(getchar())
        let l:selection = getchar()
        let l:selection = get(l:formats, l:selection, 'invalid')
        if l:selection ==# 'esc'
            break
        elseif l:selection !=# 'invalid'
            let l:result = l:selection
            break
        endif
    endwhile
    redraw!
    if result !=# 'invalid'
        echo a:name.": ".(l:result == '' ? 'none' : l:result)
    endif
    return l:result
endfunction
