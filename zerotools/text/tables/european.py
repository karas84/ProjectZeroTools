from .utils import make_table


_font_01 = """
 ABCDEFGHIJKLMNOPQRST
UVWXYZabcdefghijklmno
pqrstuvwxyz{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}
0123456789{!?}ÀÂÇ{È}ÉÊÎÔ{à}{è}
{é}êîô{ù}ûÄẞËÏÖÜäëïü¡¿Á{É1}Í
ÑÓÚá{é1}íñóú{À}È{É2}ÌÒÙàèéìòù
{Ë}{Ï}Œ{Ch}{LI}{rr}{Rune1}{Rune2}~{Rune3}{Rune4}{Rune5}\"'()-?/⸴⹁
;:,.!「」✓✗{pts}âç°#◯‷=ö#{○}{✕}
{△}{□}壱弐参肆伍陸漆捌玖œ#########
#####################
"""


_font_02 = """
 ABCDEFGHIJKLMNOPQRST
UVWXYZabcdefghijklmno
pqrstuvwxyz{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}
0123456789{!?}ÀÂÇ{È}ÉÊÎÔ{à}{è}
{é}êîô{ù}ûÄẞËÏÖÜäëïü¡¿Á{É1}Í
ÑÓÚá{é1}íñóú{À}È{É2}ÌÒÙàèéìòù
ËÏŒ{Ch}{LI}{rr}{Rune1}{Rune2}~{Rune3}{Rune4}{Rune5}\"'()-?/⸴⹁
;:,.!「」✓✗{pts}âç°#◯‷=ö#{○}{✕}
{△}{□}#########œ#########
#####################
"""


_font_03 = """
 ABCDEFGHIJKLMNOPQRST
UVWXYZabcdefghijklmno
pqrstuvwxyz{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}
0123456789{!?}ÀÂÇ{È}ÉÊÎÔ{à}{è}
{é}êîô{ù}ûÄẞËÏÖÜäëïü¡¿Á{É1}Í
ÑÓÚá{é1}íñóú{À}È{É2}ÌÒÙàèéìòù
ËÏŒ{Ch}{LI}{rr}###############
#####################
#####################
#####################
"""

from .japanese import _font_04


from .japanese import _font_05


table_eu = {
    "default": make_table(_font_01),
    0xF0: make_table(_font_02),
    0xF1: make_table(_font_03),
    0xF2: make_table(_font_04),
    0xF3: make_table(_font_05),
}
