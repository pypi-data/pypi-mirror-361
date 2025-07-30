# Pygments Kakoune Lexer

This project implements a Kakoune lexer for the Pygments library. Because
Kakoune syntax is very similar to POSIX, the lexer is implemented as a subclass
of the `BashLexer`. The keywords, values, attributes, and types are taken
directly from
[Kakoune's own highlighting definitions](https://github.com/mawww/kakoune/blob/master/rc/filetype/kakrc.kak).
The lexer is available as the package `pygments-kakoune`. You can add it to your
project with `uv add pygments-kakoune`.
