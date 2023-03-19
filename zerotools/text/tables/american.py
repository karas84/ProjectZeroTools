from .utils import make_table


_font_01 = """
 ABCDEFGHIJKLMNOPQRST
UVWXYZabcdefghijklmno
pqrstuvwxyz{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}
0123456789あいうえおかきくけこさ
しすせそたちつてとなにぬねのはひふへほまみ
むめもやゆよらりるれろわをんアイウエオカキ
クケコサシスセソタチツテトナニヌネノハヒフ
ヘホマミムメモヤユヨラリルレロワヲンぁ{○}{✕}
{△}{□}ゃゅょっァィゥェォャュョッがぎぐげござ
じずぜぞだ終づでどばびぶべぼぱぴ序充攻ガギ
"""


_font_02 = """
グゲゴザジズゼゾダ溜貯デドバビブベボパピプ
ぺ"'()-?/·{,};:,.!「」✓✗{pts}　
零一二三四五六七八九十百千万上下前後左右扉
固閉咮面掛屏風向编集霊取材手入階段動棚冬雑
然人形並止押中何不気者廊犠影輿消鏡見返振美
琴音閒夭井粱兄…写鳥居古牲常敗化除効果低用
感度良高暗遠撮钵力少回復薬葉書容器參精神全
香料強肆静作持位槽清水異{常}黑石付伍带性壊電
灯方闇照出母深雪遺思議械目映鍵地銀製小飾赤
鲭塚式陸丸月漆御捌玫射機＝範纳戸足欠仏像金
"""


from .japanese import _font_03


from .japanese import _font_04


from .japanese import _font_05


table_us = {
    "default": make_table(_font_01),
    0xF0: make_table(_font_02),
    0xF1: make_table(_font_03),
    0xF2: make_table(_font_04),
    0xF3: make_table(_font_05),
}
