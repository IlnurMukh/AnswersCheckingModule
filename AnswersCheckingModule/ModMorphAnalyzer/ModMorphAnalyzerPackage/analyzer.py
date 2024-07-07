# Turkic Morpheme Model Library: Morph Analyzer Library
#
# Copyright (C) 2021-present ModMorph Project
# Author: Nikolai Prokopyev <nikolai.prokopyev@gmail.com>
# URL: <http://modmorph.turklang.net>
# For license information, see LICENSE.TXT

import os
import sys

from alphabetter import ModMorphAlphabetter
from modmorph import ModMorph
from utils import remove_prefix


class ModMorphAnalyzer:
    def __init__(self, language, verbose=False):
        """
        Основной класс морфоанализатора.
        :param language: код языка морфоанализа
        :param verbose: режим вывода промежуточной информации в консоль -
            False (не выводить), True (выводить)
        """
        self.__verbose = verbose
        self.__modmorph = ModMorph(language)
        self.__alphabetter = ModMorphAlphabetter(language)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """
        Освобождает занятые анализатором ресурсы
        Применяется в конце работы с анализатором
        """
        self.__modmorph.close()

    def process_text(self, text):
        """
        Производит морфоаналитическую обработку входного текста
        :param text: Входной текст (UNICODE)
        :return: Генератор результатов морфоаналитической обработки.
            Каждый элемент представляет собой кортеж пары вида
            "Исходное слово/словосочетание", "Дерево морфоанализа"
        """
        words = self.__alphabetter.tokenize(text)
        if self.__verbose:
            print(f"Got {len(words)} words")
        processing_results = self.process_words(words)
        return processing_results

    def process_words(self, words):
        """
        Производит морфоаналитическую обработку входного массива слов
        :param words: Массив слов
        :return: Генератор результатов морфоаналитической обработки
            Каждый элемент результатов представляет собой кортеж пары вида
            "Исходное слово/словосочетание", "Дерево морфоанализа"
        """
        processed_next_word = False
        for index, word in enumerate(words):
            if processed_next_word:
                processed_next_word = False
                continue
            word = self.__alphabetter.lower(word)
            if index < (len(words)-1):
                next_word = self.__alphabetter.lower(words[index+1])
                processing_result, processed_next_word = self.__process_word(word, next_word)
                if processed_next_word:
                    word += " " + next_word
            else:
                processing_result, processed_next_word = self.__process_word(word)
            if self.__verbose:
                print(f"{word} : {processing_result}")
            yield word, processing_result

    def process_pair(self, pair):
        word = self.__alphabetter.lower(pair[0])
        if pair[1] is not None:
            next_word = self.__alphabetter.lower(pair[1])
            processing_result, _ = self.__process_word(word, next_word)
        else:
            processing_result, _ = self.__process_word(word)
        if self.__verbose:
            print(f"{word} : {processing_result}")
        yield word, processing_result

    def __process_word(self, word, next_word=None):
        root_candidates = [word[:i] for i in range(1, len(word) + 1)]
        roots = self.__modmorph.get_root_morphemes_by_values(root_candidates)
        processing_result = []
        processed_next_words = []
        for root in roots:
            if root["type_id"] is None:
                continue
            if word != root["value_lower"]:
                root["morph"] = root["value_lower"][:len(root["value_lower"]) - root["strip"]]
            else:
                root["morph"] = root["value_lower"]
            rest = remove_prefix(word, root["morph"])
            if rest == "":
                analytical_result = self.__process_next_word(next_word, root, True)
                processing_result.append((root["id"], root["value"], root["pos"],  root["concept_id"],
                                          root["concept_en_name"] + " : " + root["concept_ru_name"],
                                          analytical_result))
                processed_next_words.append(len(analytical_result) > 0)
                continue
            else:
                allomorph_ids = self.__get_next_allomorph_ids("type", root["type_id"])
                if len(allomorph_ids) == 0:
                    continue
                allomorph_results, processed_next_word_temp = \
                    self.__process_allomorphs(rest, allomorph_ids, first=True, next_word=next_word)
                processed_next_words.append(processed_next_word_temp)
                if len(allomorph_results) == 0:
                    continue
                processing_result.append((root["id"], root["value"], root["pos"],  root["concept_id"],
                                          root["concept_en_name"] + " : " + root["concept_ru_name"],
                                          allomorph_results))
        processed_next_word = True in processed_next_words
        return (processing_result, processed_next_word) if len(processing_result) > 0 else (None, processed_next_word)

    def __get_next_allomorph_ids(self, prev_type, prev_id):
        if prev_type == "type":
            return self.__modmorph.get_allomorph_ids_by_type_id(prev_id)
        elif prev_type == "allomorph":
            return self.__modmorph.get_allomorph2_ids_by_allomoprh1_id(prev_id)
        elif prev_type == "particle":
            return self.__modmorph.get_allomorph_ids_by_particle_id(prev_id)

    def __process_allomorphs(self, rest_allomorphs, allomorph_ids, first=False, next_word=None):
        allomorph_candidates = [rest_allomorphs[:i] for i in range(1, len(rest_allomorphs) + 1)]
        if first:
            allomorphs = self.__modmorph.get_allomorphs_by_linked_ids_and_values(allomorph_ids, allomorph_candidates)
        else:
            allomorphs = self.__modmorph.get_allomorphs_by_ids_and_values(allomorph_ids, allomorph_candidates)
        processing_result = []
        processed_next_words = []
        for allomorph in allomorphs:
            if first:
                rest = remove_prefix(rest_allomorphs, allomorph["morph"])
            else:
                rest = remove_prefix(rest_allomorphs, allomorph["value"])
            if rest == "":
                if not allomorph["is_final"]:
                    continue
                analytical_result = self.__process_next_word(next_word, allomorph)
                processing_result.append((allomorph["id"], allomorph["value"],
                                          allomorph["gram_value_id"], allomorph["gram_value"],
                                          analytical_result))
                processed_next_words.append(len(analytical_result) > 0)
            else:
                allomorph_ids = self.__get_next_allomorph_ids("allomorph", allomorph["id"])
                if len(allomorph_ids) == 0:
                    continue
                allomorph_results, processed_next_word_temp = \
                    self.__process_allomorphs(rest, allomorph_ids, next_word=next_word)
                processed_next_words.append(processed_next_word_temp)
                if len(allomorph_results) == 0:
                    continue
                processing_result.append((allomorph["id"], allomorph["value"],
                                          allomorph["gram_value_id"], allomorph["gram_value"],
                                          allomorph_results))
        processed_next_word = True in processed_next_words
        return processing_result, processed_next_word

    def __process_next_word(self, next_word, prev_allomorph=None, is_root=False):
        processing_result = []
        if next_word is None:
            return processing_result
        if prev_allomorph is not None:
            if is_root:
                particle_allomorph_ids = self.__modmorph.get_particle_ids_by_type_id(prev_allomorph["type_id"])
            else:
                particle_allomorph_ids = self.__modmorph.get_particle2_ids_by_allomorph1_id(prev_allomorph["id"])
            particle_candidates = [next_word[:i] for i in range(1, len(next_word) + 1)]
            particle_allomorphs = self.__modmorph.get_particle_allomorphs_by_ids_and_values(particle_allomorph_ids, particle_candidates)
            if len(particle_allomorphs) > 0:
                for particle in particle_allomorphs:
                    if next_word != particle["value_lower"]:
                        particle["morph"] = particle["value_lower"][:len(particle["value_lower"])]
                    else:
                        particle["morph"] = particle["value_lower"]
                    rest = remove_prefix(next_word, particle["morph"])
                    if rest == "":
                        processing_result.append((particle["id"], particle["value"],
                                                  particle["gram_value_id"], particle["gram_value"],
                                                  []))
                    else:
                        allomorph_ids = self.__get_next_allomorph_ids("particle", particle["id"])
                        if len(allomorph_ids) == 0:
                            continue
                        allomorph_results, processed_next_word_temp = \
                            self.__process_allomorphs(rest, allomorph_ids)
                        if len(allomorph_results) == 0:
                            continue
                        processing_result.append((particle["id"], particle["value"],
                                                  particle["gram_value_id"], particle["gram_value"],
                                                  allomorph_results))
                return processing_result
        adpositions = self.__modmorph.get_adpositions_by_value(next_word)
        if len(adpositions) > 0:
            adposition = adpositions[0]
            processing_result.append((adposition["id"], adposition["value"],
                                      adposition["gram_value_id"], adposition["gram_value"],
                                      []))
            return processing_result
        auxilary_verbs = self.__modmorph.get_auxilary_verbs_by_value(next_word)
        if len(auxilary_verbs) > 0:
            auxilary_verb = auxilary_verbs[0]
            processing_result.append((auxilary_verb["id"], auxilary_verb["value"],
                                      auxilary_verb["gram_value_id"], auxilary_verb["gram_value"],
                                      []))
            return processing_result
        return processing_result


if __name__ == '__main__':
    if len(sys.argv) < 2:
        program_name = os.path.relpath(sys.argv[0])
        print(f"Usage: {program_name} language")
        exit()
    language = sys.argv[1]
    input_text = ""
    while True:
        try:
            input_text += input()
        except EOFError:
            break
    morph_analyzer = ModMorphAnalyzer(language)
    for result in morph_analyzer.process_text(input_text):
        print(result)
