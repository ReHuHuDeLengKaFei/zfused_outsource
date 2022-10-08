# coding:utf-8
# --author-- lanhua.zhou

import os
import json
import logging

__all__ = ["component_color", "LetterColor"]

logger = logging.getLogger(__name__)


CATEGORY_COLOR = {
    "not started": "#f65b5b",
    "in progress": "#ffa32e",
    "done": "#31d6bc",
    "freeze": "#000000"
}

class LetterColor(object):
    _color_dict = {
            "a":"#E5A3B4",
            "b":"#EDC89A",
            "c":"#FCB400",
            "d":"#E0E67A",
            "e":"#BBDB97",
            "f":"#ACD9BA",
            "g":"#A1DAE1",
            "h":"#C19FCA",
            "i":"#CF2027",
            "j":"#D96927",
            "k":"#ECDA42",
            "l":"#A5C33B",
            "m":"#77C258",
            "n":"#54958C",
            "o":"#486EB6",
            "p":"#77449A",
            "q":"#7F7E80",
            "r":"#7C1214",
            "s":"#83421B",
            "t":"#86792F",
            "u":"#587232",
            "v":"#417135",
            "w":"#3D6C4C",
            "x":"#253676",
            "y":"#462165",
            "z":"#1D1D1D",
            "0":"#000000",
            "1":"#111111"
        }

    @classmethod
    def color(cls, letter):
        return cls._color_dict[letter]