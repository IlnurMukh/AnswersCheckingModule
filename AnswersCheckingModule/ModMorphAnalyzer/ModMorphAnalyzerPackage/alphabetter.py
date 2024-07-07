# Turkic Morpheme Model Library: Alphabetter Library
#
# Copyright (C) 2021-present ModMorph Project
# Author: Nikolai Prokopyev <nikolai.prokopyev@gmail.com>
# URL: <http://modmorph.turklang.net>
# For license information, see LICENSE.TXT

import re

from modmorph import ModMorph


class ModMorphAlphabetter:
    def __init__(self, language):
        """
        Основной класс алфавиттера.
        :param language: код языка алфавиттера
        """
        modmorph = ModMorph(language)
        self.__alphabet = [(alpha_letter["lower"], alpha_letter["upper"])
                           for alpha_letter in modmorph.get_alpha_letters()]
        self.__alphabet.append(("-", "-"))
        modmorph.close()

    def upper(self, word):
        result = []
        for char in word:
            found_alpha_letter = None
            for alpha_letter in self.__alphabet:
                if alpha_letter[1] == char:
                    found_alpha_letter = alpha_letter
                    break
            if found_alpha_letter is None:
                result.append(char)
                continue
            result.append(found_alpha_letter[0])
        return "".join(result)

    def lower(self, word):
        result = []
        for char in word:
            found_alpha_letter = None
            for alpha_letter in self.__alphabet:
                if alpha_letter[0] == char:
                    found_alpha_letter = alpha_letter
                    break
            if found_alpha_letter is None:
                result.append(char)
                continue
            result.append(found_alpha_letter[1])
        return "".join(result)

    def tokenize(self, text):
        return re.findall(r'([' + "".join(alpha_letter[0] for alpha_letter in self.__alphabet) + ']+)', text,
                          flags=re.IGNORECASE | re.UNICODE)
