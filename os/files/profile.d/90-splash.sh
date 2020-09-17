
# Show splash screen(for interactive shells only)

# Bash shell sets special variable $- to include the letter "i"
# to indicate an interactive shell.

if [[ $- == *i* ]]; then

    # Bail if inside a TMUX session
    # as the splash/motd has already been shown
    [ -z $TMUX ] || return


    [ -e /usr/local/bin/splash ] && /usr/local/bin/splash
fi
