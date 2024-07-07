# Turkic Morpheme Model Library: Modmorph Language Model Library
#
# Copyright (C) 2021-present ModMorph Project
# Author: Nikolai Prokopyev <nikolai.prokopyev@gmail.com>
# URL: <http://modmorph.turklang.net>
# For license information, see LICENSE.TXT

import os
import sqlite3

from config import LANGUAGE_DIRECTORY
from utils import remove_prefix, sqlite_connect_file_to_memory

modmorph_sql = {
    "select_metadata": """
        SELECT "language", "version", "build", "size" 
        FROM "metadata" 
        LIMIT 1
    """,
    "select_alpha_letters": """
        SELECT "id", "lower", "upper", "ordering"
        FROM "alpha_letter" 
        ORDER BY "ordering"
    """,
    "select_root_morphemes_by_values": """
        SELECT "root_morpheme"."id" as "id", "root_morpheme"."code" as "code", 
            "root_morpheme"."value" as "value", "root_morpheme"."value_lower" as "value_lower", 
            "root_morpheme"."pos" as "pos", "root_morpheme"."type_id" as "type_id", 
            "root_morpheme"."concept_id" as "concept_id", 
            "root_morpheme"."concept_en_name" as "concept_en_name", 
            "root_morpheme"."concept_ru_name" as "concept_ru_name", 
            "morphonological_type"."strip" as "strip" 
        FROM "root_morpheme" 
        INNER JOIN "morphonological_type" ON "root_morpheme"."type_id" = "morphonological_type"."id" 
        WHERE "root_morpheme"."value_strip" IN (%s)
    """,
    "select_allomorphs_by_id_and_values": """
        SELECT "affixal_allomorph"."id" as "id", "affixal_allomorph"."code" as "code", 
            "affixal_allomorph"."value" as "value", "affixal_allomorph"."is_final" as "is_final", 
            "gram_value"."id" as "gram_value_id", "gram_value"."tag" as "gram_value" 
        FROM "affixal_allomorph" 
        INNER JOIN "affixal_morpheme" ON "affixal_allomorph"."affixal_morpheme_id" = "affixal_morpheme"."id" 
        INNER JOIN "gram_value" ON "affixal_morpheme"."gram_value_id" = "gram_value"."id" 
        WHERE "affixal_allomorph"."id" = %s AND "affixal_allomorph"."value" IN (%s)
    """,
    "select_allomorphs_by_ids_and_values": """
        SELECT "affixal_allomorph"."id" as "id", "affixal_allomorph"."code" as "code", 
            "affixal_allomorph"."value" as "value", "affixal_allomorph"."is_final" as "is_final", 
            "gram_value"."id" as "gram_value_id", "gram_value"."tag" as "gram_value" 
        FROM "affixal_allomorph" 
        INNER JOIN "affixal_morpheme" ON "affixal_allomorph"."affixal_morpheme_id" = "affixal_morpheme"."id" 
        INNER JOIN "gram_value" ON "affixal_morpheme"."gram_value_id" = "gram_value"."id" 
        WHERE "affixal_allomorph"."id" IN (%s) AND "affixal_allomorph"."value" IN (%s)
    """,
    "select_particle_allomorphs_by_ids_and_values": """
        SELECT "particle_allomorph"."id" as "id", "particle_allomorph"."code" as "code", 
            "particle_allomorph"."value" as "value", "particle_allomorph"."value_lower" as "value_lower", 
            "gram_value"."id" as "gram_value_id", "gram_value"."tag" as "gram_value" 
        FROM "particle_allomorph" 
        INNER JOIN "particle" ON "particle_allomorph"."particle_id" = "particle"."id" 
        INNER JOIN "gram_value" ON "particle"."gram_value_id" = "gram_value"."id" 
        WHERE "particle_allomorph"."id" IN (%s) AND "particle_allomorph"."value" IN (%s)
    """,
    "select_adpositions_by_value": """
        SELECT "adposition"."id" as "id", "adposition"."code" as "code", 
            "adposition"."value" as "value",
            "gram_value"."id" as "gram_value_id", "gram_value"."tag" as "gram_value" 
        FROM "adposition" 
        INNER JOIN "gram_value" ON "adposition"."gram_value_id" = "gram_value"."id" 
        WHERE "adposition"."value" = ?
    """,
    "select_auxilary_verbs_by_value": """
        SELECT "auxilary_verb"."id" as "id", "auxilary_verb"."code" as "code", 
            "auxilary_verb"."value" as "value",
            "gram_value"."id" as "gram_value_id", "gram_value"."tag" as "gram_value" 
        FROM "auxilary_verb" 
        INNER JOIN "gram_value" ON "auxilary_verb"."gram_value_id" = "gram_value"."id" 
        WHERE "auxilary_verb"."value" = ?
    """,
    "select_allomorph_ids_by_type_id": """
        SELECT "affixal_allomorph_id", "link_chars" 
        FROM "morphotactics_t2a" 
        WHERE "morphonological_type_id" = ?
    """,
    "select_allomorph2_ids_by_allomorph1_id": """
        SELECT "affixal_allomorph2_id" 
        FROM "morphotactics_a2a" 
        WHERE "affixal_allomorph1_id" = ?
    """,
    "select_allomorph_ids_by_particle_id": """
        SELECT "affixal_allomorph2_id" 
        FROM "morphotactics_p2a" 
        WHERE "particle_allomorph1_id" = ?
    """,
    "select_particle_ids_by_type_id": """
        SELECT "particle_allomorph_id" 
        FROM "morphotactics_t2p" 
        WHERE "morphonological_type_id" = ?
    """,
    "select_particle2_ids_by_allomorph1_id": """
        SELECT "particle_allomorph2_id" 
        FROM "morphotactics_a2p" 
        WHERE "affixal_allomorph1_id" = ?
    """,
    "select_root_morphemes_by_concept_id": """
        SELECT "root_morpheme"."id" as "id", "root_morpheme"."code" as "code", 
            "root_morpheme"."value" as "value", "root_morpheme"."value_lower" as "value_lower", 
            "root_morpheme"."pos" as "pos", "root_morpheme"."type_id" as "type_id", 
            "root_morpheme"."concept_id" as "concept_id", 
            "root_morpheme"."concept_en_name" as "concept_en_name", 
            "root_morpheme"."concept_ru_name" as "concept_ru_name", 
            "morphonological_type"."strip" as "strip" 
        FROM "root_morpheme" 
        INNER JOIN "morphonological_type" ON "root_morpheme"."type_id" = "morphonological_type"."id" 
        WHERE "root_morpheme"."concept_id" = ?
    """,
    "select_object_concept_by_concept_id": """
        SELECT "object_concept_taxonomy"."id" as "id", 
            "object_concept_taxonomy"."taxonomical_code" as "taxonomical_code"
        FROM "object_concept_taxonomy" 
        WHERE "object_concept_taxonomy"."id" = ?
    """,
    "select_allomorphs_by_gram_value_and_type_id": """
        SELECT "affixal_allomorph"."id" as "id", "affixal_allomorph"."code" as "code", 
            "affixal_allomorph"."value" as "value", "affixal_allomorph"."is_final" as "is_final", 
            "gram_value"."id" as "gram_value_id", "gram_value"."tag" as "gram_value", 
            "morphotactics_t2a"."link_chars" as "link_chars" 
        FROM "affixal_allomorph" 
        INNER JOIN "affixal_morpheme" ON "affixal_allomorph"."affixal_morpheme_id" = "affixal_morpheme"."id" 
        INNER JOIN "gram_value" ON "affixal_morpheme"."gram_value_id" = "gram_value"."id" 
        INNER JOIN "morphotactics_t2a" ON "affixal_allomorph"."id" = "morphotactics_t2a"."affixal_allomorph_id"
        WHERE "gram_value"."id" = ? AND "morphotactics_t2a"."morphonological_type_id" = ?
    """,
    "select_allomorphs2_by_gram_value_and_allomoprh1_id": """
       SELECT "affixal_allomorph"."id" as "id", "affixal_allomorph"."code" as "code", 
           "affixal_allomorph"."value" as "value", "affixal_allomorph"."is_final" as "is_final", 
           "gram_value"."id" as "gram_value_id", "gram_value"."tag" as "gram_value" 
       FROM "affixal_allomorph" 
       INNER JOIN "affixal_morpheme" ON "affixal_allomorph"."affixal_morpheme_id" = "affixal_morpheme"."id" 
       INNER JOIN "gram_value" ON "affixal_morpheme"."gram_value_id" = "gram_value"."id" 
       INNER JOIN "morphotactics_a2a" ON "affixal_allomorph"."id" = "morphotactics_a2a"."affixal_allomorph2_id"
       WHERE "gram_value"."id" = ? AND "morphotactics_a2a"."affixal_allomorph1_id" = ?
    """,
    "select_particle_allomorphs2_by_gram_value_and_allomorph1_id": """
       SELECT "particle_allomorph"."id" as "id", "particle_allomorph"."code" as "code", 
           "particle_allomorph"."value" as "value", 
           "gram_value"."id" as "gram_value_id", "gram_value"."tag" as "gram_value" 
       FROM "particle_allomorph" 
       INNER JOIN "particle" ON "particle_allomorph"."particle_id" = "particle"."id" 
       INNER JOIN "gram_value" ON "particle"."gram_value_id" = "gram_value"."id" 
       INNER JOIN "morphotactics_a2p" ON "particle_allomorph"."id" = "morphotactics_a2p"."particle_allomorph2_id"
       WHERE "gram_value"."id" = ? AND "morphotactics_a2p"."affixal_allomorph1_id" = ?
    """,
    "select_adpositions_by_gram_value": """
        SELECT "adposition"."id" as "id", "adposition"."code" as "code", 
            "adposition"."value" as "value",
            "gram_value"."id" as "gram_value_id", "gram_value"."tag" as "gram_value" 
        FROM "adposition" 
        INNER JOIN "gram_value" ON "adposition"."gram_value_id" = "gram_value"."id" 
        WHERE "gram_value"."id" = ?
    """,
    "select_auxilary_verbs_by_gram_value": """
        SELECT "auxilary_verb"."id" as "id", "auxilary_verb"."code" as "code", 
            "auxilary_verb"."value" as "value",
            "gram_value"."id" as "gram_value_id", "gram_value"."tag" as "gram_value" 
        FROM "auxilary_verb" 
        INNER JOIN "gram_value" ON "auxilary_verb"."gram_value_id" = "gram_value"."id" 
        WHERE "gram_value"."id" = ?
    """,
}


class ModMorph:
    def __init__(self, language):
        self.__conn = sqlite_connect_file_to_memory(os.path.join(LANGUAGE_DIRECTORY, f"modmorph_{language}.sqlite"))
        self.__conn.row_factory = sqlite3.Row
        self.__cur = self.__conn.cursor()

    def close(self):
        self.__conn.close()

    def get_metadata(self):
        metadata = {
            "language": "LANGUAGE_NONE",
            "version": 0,
            "build": 0,
            "size": 0
        }
        self.__cur.execute(modmorph_sql["select_metadata"])
        row = self.__cur.fetchone()
        if row is not None:
            row = dict(row)
            metadata["language"] = row["language"]
            metadata["version"] = row["version"]
            metadata["build"] = row["build"]
            metadata["size"] = row["size"]
        return metadata

    def get_alpha_letters(self):
        self.__cur.execute(modmorph_sql["select_alpha_letters"])
        return tuple(dict(row) for row in self.__cur.fetchall())

    def get_root_morphemes_by_values(self, values):
        escaped_values = []
        for value in values:
            escaped_values.append(value.replace(r"'", r"''"))
        self.__cur.execute(modmorph_sql["select_root_morphemes_by_values"]
                           % ", ".join(f"'{value}'" for value in escaped_values))
        return tuple(dict(row) for row in self.__cur.fetchall())

    def get_object_concept_taxonomical_code_by_id(self, object_concept_id):
        self.__cur.execute(modmorph_sql["select_object_concept_by_concept_id"], (object_concept_id,))
        concept = self.__cur.fetchone()
        if concept is None:
            return ""
        return concept["taxonomical_code"]

    def get_allomorphs_by_linked_ids_and_values(self, linked_ids, values):
        result = []
        for linked_id in linked_ids:
            id = linked_id[0]
            link = linked_id[1] if linked_id[1] is not None else ""
            escaped_values = [remove_prefix(value, link).replace(r"'", r"''") for value in values]
            self.__cur.execute(modmorph_sql["select_allomorphs_by_id_and_values"]
                               % (id,
                                  ", ".join(f"'{value}'" for value in escaped_values)))
            for row in self.__cur.fetchall():
                row_dict = dict(row)
                row_dict["morph"] = link + row_dict["value"]
                result.append(row_dict)
        return tuple(result)

    def get_allomorphs_by_ids_and_values(self, ids, values):
        escaped_values = []
        for value in values:
            escaped_values.append(value.replace(r"'", r"''"))
        self.__cur.execute(modmorph_sql["select_allomorphs_by_ids_and_values"]
                           % (", ".join(f"'{id}'" for id in ids),
                           ", ".join(f"'{value}'" for value in escaped_values)))
        return tuple(dict(row) for row in self.__cur.fetchall())

    def get_particle_allomorphs_by_ids_and_values(self, ids, values):
        escaped_values = []
        for value in values:
            escaped_values.append(value.replace(r"'", r"''"))
        self.__cur.execute(modmorph_sql["select_particle_allomorphs_by_ids_and_values"]
                           % (", ".join(f"'{id}'" for id in ids),
                              ", ".join(f"'{value}'" for value in escaped_values)))
        return tuple(dict(row) for row in self.__cur.fetchall())

    def get_adpositions_by_value(self, value):
        self.__cur.execute(modmorph_sql["select_adpositions_by_value"], (value, ))
        return tuple(dict(row) for row in self.__cur.fetchall())

    def get_auxilary_verbs_by_value(self, value):
        self.__cur.execute(modmorph_sql["select_auxilary_verbs_by_value"], (value,))
        return tuple(dict(row) for row in self.__cur.fetchall())

    def get_allomorph_ids_by_type_id(self, type_id):
        self.__cur.execute(modmorph_sql["select_allomorph_ids_by_type_id"], (type_id, ))
        return tuple((row[0], row[1]) for row in self.__cur.fetchall())

    def get_allomorph2_ids_by_allomoprh1_id(self, allomorph1_id):
        self.__cur.execute(modmorph_sql["select_allomorph2_ids_by_allomorph1_id"], (allomorph1_id, ))
        return tuple(row[0] for row in self.__cur.fetchall())

    def get_allomorph_ids_by_particle_id(self, particle_id):
        self.__cur.execute(modmorph_sql["select_allomorph_ids_by_particle_id"], (particle_id,))
        return tuple(row[0] for row in self.__cur.fetchall())

    def get_particle_ids_by_type_id(self, type_id):
        self.__cur.execute(modmorph_sql["select_particle_ids_by_type_id"], (type_id, ))
        return tuple(row[0] for row in self.__cur.fetchall())

    def get_particle2_ids_by_allomorph1_id(self, allomorph1_id):
        self.__cur.execute(modmorph_sql["select_particle2_ids_by_allomorph1_id"], (allomorph1_id,))
        return tuple(row[0] for row in self.__cur.fetchall())

    def get_root_morphemes_by_concept_id(self, concept_id):
        self.__cur.execute(modmorph_sql["select_root_morphemes_by_concept_id"], (concept_id,))
        return tuple(dict(row) for row in self.__cur.fetchall())

    def get_allomorphs_by_gram_value_and_type_id(self, gram_value_id, type_id):
        self.__cur.execute(modmorph_sql["select_allomorphs_by_gram_value_and_type_id"], (gram_value_id, type_id))
        return tuple(dict(row) for row in self.__cur.fetchall())

    def get_allomorphs2_by_gram_value_and_allomoprh1_id(self, gram_value_id, allomorph1_id):
        self.__cur.execute(modmorph_sql["select_allomorphs2_by_gram_value_and_allomoprh1_id"], (gram_value_id, allomorph1_id))
        return tuple(dict(row) for row in self.__cur.fetchall())

    def get_particle_allomorphs2_by_gram_value_and_allomorph1_id(self, gram_value_id, allomorph1_id):
        self.__cur.execute(modmorph_sql["select_particle_allomorphs2_by_gram_value_and_allomorph1_id"], (gram_value_id, allomorph1_id))
        return tuple(dict(row) for row in self.__cur.fetchall())

    def get_adpositions_by_gram_value(self, gram_value_id):
        self.__cur.execute(modmorph_sql["select_adpositions_by_gram_value"], (gram_value_id, ))
        return tuple(dict(row) for row in self.__cur.fetchall())

    def get_auxilary_verbs_by_gram_value(self, gram_value_id):
        self.__cur.execute(modmorph_sql["select_auxilary_verbs_by_gram_value"], (gram_value_id,))
        return tuple(dict(row) for row in self.__cur.fetchall())
