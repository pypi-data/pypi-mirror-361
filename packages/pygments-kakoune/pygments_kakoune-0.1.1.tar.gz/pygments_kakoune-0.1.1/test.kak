# This is a comment
define-command -params 0..1 foobar %{
    nop '"'
    map global user x ': foobar<ret>'
    evaluate-commands %sh{ # and another
        printf '%s\n' 'info "hi!"'
    }
}

map -docstring 'open debug buffer' global user d ':goto-debug<ret>'

declare-filetype-mode kak
# TODO: automatically add -override for overridable commands?
define-command exec-selection %{
    execute-keys ':<c-r>.<ret>'
}

map -docstring 'execute selection' global kak x ': exec-selection<ret>'

define-command repl %{
    new %{ edit -scratch; set buffer filetype kak }
}

# jumplist

map -docstring 'jump forward' global normal <c-f> <c-i>
map -docstring 'save to jumplist' global normal <c-v> <c-s>

