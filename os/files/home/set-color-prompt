# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# Set prompt and title (for interactive shells only)
if [ "$(expr $- : '.*i')" -ne 0 ]; then

  # this works for sh and bash
  if [ -z "$ZSH_VERSION" ]; then
      # first get exit code of last command, and set colors
      PS1="\$(\
      EXIT=\"\$?\" ; \
      BLUE=\"\[\e[38;5;39m\]\" ; \
      RED=\"\[\e[31m\]\" ; \
      ORANGE=\"\[\e[38;5;208m\]\" ; \
      WHITE=\"\[\e[0m\]\" ; "
      # endchar
      #   use # for root and $ for non-root users
      #   use white for default color, and red if last exit code is non-zero
      # username
      #   use red for root blue(39) for non-root users
      PS1+="\
      endchar=\"\\$\${WHITE}\" ; \
      username=\"\${BLUE}\u\${WHITE}\" ; \
      if [ \"\$UID\" = \"0\" ]; then
          username=\"\${RED}\u\${WHITE}\" ; \
      fi ; \
      if [ \"\$EXIT\" -eq 0 ]; then
          endchar=\"\${WHITE}\$endchar\" ; \
      else \
          endchar=\"\${RED}\$endchar\"
      fi ; "
      # hostname in orange
      PS1+="\
      host=\"\${ORANGE}\H\${WHITE}\" ; "
      # current directory in blue(39)
      PS1+="\
      dir=\"\${BLUE}\w\${WHITE}\" ; "
      # set prompt, and additionally set window title for xterm
      if [ "${TERM:0:5}" = "xterm" ]; then
          PS1+="echo \"\[\e]2;\u@\H :: \w\a\]\${username}@\${host}\${dir} \${endchar} \" )"
      else
          PS1+="echo \"\${username}@\${host} \${dir} \${endchar} \" )"
      fi

  else
    # this works for zsh
      # endchar
      # use red if last command has non-zero exit
      # use # for root and $ for non-root users
      local _root_endch="%(?.#.%F{red}#%f)"
      local _other_endch="%(?.$.%F{red}$%f)"
      local _endchar="%(#.${_root_endch}.${_other_endch})"
      # use red for root and blue(39) for non-root users
      local _username="%F{%(#.red.39)}%n%f"
      # hostname in orange
      local _host="%F{208}%m%f"
      # current directory in blue(39)
      local _dir="%F{39}%~%f"
      # set prompt
      PS1="${_username}@${_host} ${_dir} ${_endchar} "
      # additionally set window title for xterm
      __stateless_title () {    # for xterm, set window title
        if [ "${TERM:0:5}" = "xterm" ]; then
            print -Pn "\e]2;%n\@%m :: %~\a"
        fi
      }
      __stateless_title
      autoload -Uz add-zsh-hook
      add-zsh-hook chpwd __stateless_title
  fi
  export PS1
fi
