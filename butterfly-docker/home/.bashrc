alias ls="ls --color"
reset=$(tput sgr0)
bold=$(tput bold)
black=$(tput setaf 0)
red=$(tput setaf 1)
green=$(tput setaf 2)
yellow=$(tput setaf 3)
blue=$(tput setaf 4)
magenta=$(tput setaf 5)
cyan=$(tput setaf 6)
white=$(tput setaf 7)
user_color=$green
[ "$UID" -eq 0 ] && { user_color=$red; }

export PS1="\[$reset\]\[$bold\]\[$green\]\u\[$reset\]\[$bold\]\[$white\]@\[$reset\]\[$bold\]\[$yellow\]\h\[$reset\]\[$bold\]:\[$blue\]\w\\$\[$(tput sgr0)\]\[$reset\]\[$bold\] "
