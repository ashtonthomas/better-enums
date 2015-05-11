#! /usr/bin/env python

# This file is part of Better Enums, released under the BSD 2-clause license.
# See LICENSE for details, or visit http://github.com/aantron/better-enums.

import os
import sys

class MultiLine(object):
    def __init__(self, stream, indent = 4, columns = 80, initial_column = 0):
        self._columns_left = columns - initial_column
        self._indent = indent
        self._columns = columns
        self._stream = stream

    def write(self, token, last = False):
        break_line = False
        if last:
            if len(token) > self._columns_left:
                break_line = True
        else:
            if len(token) > self._columns_left - 1:
                break_line = True

        if break_line:
            print >> self._stream, ' ' * (self._columns_left - 1) + '\\'
            self._stream.write(' ' * self._indent)
            self._columns_left = self._columns - self._indent
            token = token.lstrip()

        self._stream.write(token)
        self._columns_left -= len(token)

def generate(stream, filename, count, script):
    print >> stream, '/// @file ' + filename
    print >> stream, '/// @brief Preprocessor higher-order map macro.'
    print >> stream, '///'
    print >> stream, '/// This file was automatically generated by ' + script

    print >> stream, ''
    print >> stream, '#pragma once'
    print >> stream, ''
    print >> stream, '#ifndef _BETTER_ENUM_ENUM_PREPROCESSOR_MAP_H_'
    print >> stream, '#define _BETTER_ENUM_ENUM_PREPROCESSOR_MAP_H_'

    print >> stream, ''
    print >> stream, '#define _ENUM_PP_MAP(macro, data, ...) \\'
    print >> stream, '    _ENUM_PP_APPLY(_ENUM_PP_MAP_VAR_COUNT, ' + \
                     '_ENUM_PP_COUNT(__VA_ARGS__)) \\'
    print >> stream, '        (macro, data, __VA_ARGS__)'

    print >> stream, ''
    print >> stream, '#define _ENUM_PP_MAP_VAR_COUNT(count) ' + \
                     '_ENUM_PP_MAP_ ## count'

    print >> stream, ''
    print >> stream, '#define _ENUM_PP_APPLY(macro, ...) macro(__VA_ARGS__)'

    print >> stream, ''
    print >> stream, '#define _ENUM_PP_MAP_1(macro, data, x) ' + \
                     '_ENUM_PP_APPLY(macro, data, x)'
    for index in range(2, count + 1):
        print >> stream, '#define _ENUM_PP_MAP_' + str(index) + \
                         '(macro, data, x, ...) ' + \
                         '_ENUM_PP_APPLY(macro, data, x), \\'
        print >> stream, '    ' + \
                         '_ENUM_PP_MAP_' + str(index - 1) + \
                         '(macro, data, __VA_ARGS__)'

    print >> stream, ''
    pp_count_impl_prefix = '#define _ENUM_PP_COUNT_IMPL(_1,'
    stream.write(pp_count_impl_prefix)
    pp_count_impl = MultiLine(stream = stream, indent = 4,
                              initial_column = len(pp_count_impl_prefix))
    for index in range(2, count + 1):
        pp_count_impl.write(' _' + str(index) + ',')
    pp_count_impl.write(' count,')
    pp_count_impl.write(' ...)')
    pp_count_impl.write(' count', last = True)
    print >> stream, ''

    print >> stream, ''
    pp_count_prefix = \
        '#define _ENUM_PP_COUNT(...) _ENUM_PP_COUNT_IMPL(__VA_ARGS__,'
    stream.write(pp_count_prefix)
    pp_count = MultiLine(stream = stream, indent = 4,
                         initial_column = len(pp_count_prefix))
    for index in range(0, count - 1):
        pp_count.write(' ' + str(count - index) + ',')
    pp_count.write(' 1)', last = True)
    print >> stream, ''

    print >> stream, ''
    print >> stream, '#endif // #ifndef _BETTER_ENUM_ENUM_PREPROCESSOR_MAP_H_'

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print >> sys.stderr, 'Usage: ' + sys.argv[0] + ' FILE COUNT'
        print >> sys.stderr, ''
        print >> sys.stderr, 'Prints map macro definition to FILE.'
        sys.exit(1)

    output_file = open(sys.argv[1], "w")

    try:
        generate(output_file, sys.argv[1], int(sys.argv[2]),
                 os.path.basename(sys.argv[0]))
    finally:
        output_file.close()

    sys.exit(0)
