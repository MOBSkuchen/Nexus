import colorama as colora

colora.init()

Fore = colora.Fore
Style = colora.Style
Back = colora.Back

Style.UNDERLINE = "\033[4m"
CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'


def format(ind):
    ground = colora.Fore
    ret = ind.replace("%red", ground.RED) \
             .replace("%blue", ground.BLUE) \
             .replace("%magenta", ground.MAGENTA) \
             .replace("%yellow", ground.YELLOW) \
             .replace("%black", ground.BLACK) \
             .replace("%cyan", ground.CYAN) \
             .replace("%green", ground.GREEN) \
             .replace("%white", ground.WHITE)
    ground = colora.Back
    ret = ret.replace("$red", ground.RED) \
             .replace("$blue", ground.BLUE) \
             .replace("$magenta", ground.MAGENTA) \
             .replace("$yellow", ground.YELLOW) \
             .replace("$black", ground.BLACK) \
             .replace("$cyan", ground.CYAN) \
             .replace("$green", ground.GREEN) \
             .replace("$white", ground.WHITE)
    ground = colora.Style
    ret = ret.replace("&bold", ground.BRIGHT) \
             .replace("&under", ground.UNDERLINE) \
             .replace("&reset", ground.RESET_ALL)

    return ret
