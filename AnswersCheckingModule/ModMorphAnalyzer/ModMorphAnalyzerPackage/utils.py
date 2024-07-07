# Turkic Morpheme Model Library: Utility Library
#
# Copyright (C) 2021-present ModMorph Project
# Author: Nikolai Prokopyev <nikolai.prokopyev@gmail.com>
# URL: <http://modmorph.turklang.net>
# For license information, see LICENSE.TXT

import os
import sqlite3
from io import StringIO


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def sqlite_connect_file_to_memory(file_path):
    conn = sqlite3.connect(file_path)
    tempfile = StringIO()
    for line in conn.iterdump():
        tempfile.write('%s\n' % line)
    conn.close()
    tempfile.seek(0)
    conn_memory = sqlite3.connect(":memory:")
    conn_memory.cursor().executescript(tempfile.read())
    conn_memory.commit()
    tempfile.close()
    return conn_memory


def sqlite_dump_connection_memory_to_file(conn, file_path):
    tempfile = StringIO()
    for line in conn.iterdump():
        tempfile.write('%s\n' % line)
    conn.close()
    tempfile.seek(0)
    if os.path.exists(file_path):
        os.remove(file_path)
    conn_file = sqlite3.connect(file_path)
    conn_file.cursor().executescript(tempfile.read())
    conn_file.commit()
    tempfile.close()
    conn_file.close()
