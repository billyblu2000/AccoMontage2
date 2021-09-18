import sys

sys.path.append('/Users/billyyi/PycharmProjects/Chorderator/chorderator')
import chorderator as cdt
from chorderator import Const

if __name__ == '__main__':
    cdt.set_meta(tonic='', mode=Const.Mode.MAJOR, meter=Const.Meter.FOUR_FOUR)
    cdt.generate()
