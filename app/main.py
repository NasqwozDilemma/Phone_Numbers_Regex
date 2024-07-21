'''
Copyright 2024 NasqwozDilemma
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import argparse
import re
from collections import defaultdict

from icecream import ic

# ic.configureOutput(includeContext=True)
ic.disable()


def group_numbers(numbers, separator, use_dot):
    """
    Группирует последовательные номера.
    Возвращает список кортежей, представляющих диапазоны.
    """
    numbers = sorted(list(map(int, set(numbers))))
    groups = []
    start = numbers[0]
    prev = start

    for num in numbers[1:]:
        if (
            num == prev + 1
            and len(str(num)) == len(str(prev))
            and str(num)[0] == str(prev)[0]
        ):
            prev = num
        else:
            groups.append((str(start), str(prev)))
            start = num
            prev = start
    groups.append((str(start), str(prev)))
    ic(groups)
    return pools_to_regex(groups, separator, use_dot)


def split_to_pools(pools, separator, use_dot):
    """
    Разделяет последовательность пулов на диапазоны.
    Возвращает список кортежей, представляющих диапазоны.
    """
    groups = []
    if len(pools) % 2 == 0:
        for i in range(0, len(pools), 2):
            groups.append((pools[i], pools[i + 1]))
    else:
        raise ValueError('Введите четное количество элементов!')
    ic(groups)
    return pools_to_regex(groups, separator, use_dot)


def range_to_regex(start, end, separator):
    """Преобразует диапазон номеров в регулярное выражение."""
    start_suffix_all_nulls = False
    internal_start_suffix_all_nulls = False
    internal_start_suffix_all_nines = False
    internal_end_suffix_all_nulls = False
    internal_end_suffix_all_nines = False
    end_suffix_all_nines = False
    all_internal_suffix_all_nulls = False
    two_character_number = False

    if start == end:
        ic()
        return f'^{re.escape(start)}$'

    regex_parts = []
    common_prefix = ''
    start = str(start)
    end = str(end)
    for i in range(len(start)):
        if start[i] == end[i]:
            common_prefix += start[i]
        else:
            break

    ic(common_prefix)
    start_suffix = start[len(common_prefix):]
    ic(start_suffix)
    end_suffix = end[len(common_prefix):]
    ic(end_suffix)

    # 'start_suffix_all_nulls'
    for i in start_suffix:
        if int(i) == 0:
            start_suffix_all_nulls = True
        else:
            start_suffix_all_nulls = False
            break
        ic(start_suffix_all_nulls)

    # 'internal_start_suffix_all_nulls'
    for i in start_suffix[1:]:
        if int(i) == 0:
            internal_start_suffix_all_nulls = True
        else:
            internal_start_suffix_all_nulls = False
            break
        ic(internal_start_suffix_all_nulls)

    # 'internal_start_suffix_all_nines'
    for i in start_suffix[1:]:
        if int(i) == 9:
            internal_start_suffix_all_nines = True
        else:
            internal_start_suffix_all_nines = False
            break
        ic(internal_start_suffix_all_nines)

    # 'end_suffix_all_nines'
    for i in end_suffix:
        if int(i) == 9:
            end_suffix_all_nines = True
        else:
            end_suffix_all_nines = False
            break
        ic(end_suffix_all_nines)

    # 'internal_end_suffix_all_nulls'
    for i in end_suffix[1:]:
        if int(i) == 0:
            internal_end_suffix_all_nulls = True
        else:
            internal_end_suffix_all_nulls = False
            break
        ic(internal_end_suffix_all_nulls)

    # 'internal_end_suffix_all_nines'
    for i in end_suffix[1:]:
        if int(i) == 9:
            internal_end_suffix_all_nines = True
        else:
            internal_end_suffix_all_nines = False
            break
        ic(internal_end_suffix_all_nines)

    # 'all_internal_suffix_all_nulls'
    if start_suffix[1:] == end_suffix[1:]:
        for i in start_suffix[1:]:
            if int(i) == 0:
                all_internal_suffix_all_nulls = True
            else:
                all_internal_suffix_all_nulls = False
                break
            ic(all_internal_suffix_all_nulls)

    # 'two_character_number'
    if len(start) == 2:
        two_character_number = True
        ic(two_character_number)

    # 'two_character_number'
    if two_character_number:
        ic('two_character_number')
        regex_parts.append(
            f'^{re.escape(common_prefix)}'
            f'[{int(start_suffix[0])}-{int(end_suffix[0])}]$'
        )
        return f'{separator}'.join(regex_parts)

    # '000 000'
    if all_internal_suffix_all_nulls:
        ic('000 000')
        digits_count = int(end_suffix[0]) - int(start_suffix[0])
        for i in range(digits_count):
            regex_parts.append(
                f'^{re.escape(common_prefix)}{str(int(start_suffix[0]) + i)}'
                f'[0-9]{{{len(start_suffix[1:])}}}$'
            )
        regex_parts.append(
            f'^{re.escape(common_prefix)}{end_suffix[0]}{start_suffix[1:]}$'
        )
        return f'{separator}'.join(regex_parts)

    # '000 999'
    if start_suffix_all_nulls and end_suffix_all_nines:
        ic('000 999')
        regex_parts.append(
            f'^{re.escape(common_prefix)}[0-9]{{{len(start_suffix)}}}$'
        )
        return f'{separator}'.join(regex_parts)

    # '000 ___'
    if start_suffix_all_nulls or internal_start_suffix_all_nulls:
        ic('000 ___')
        regex_parts.extend(
            regex_from_all_nulls(common_prefix, start_suffix, end_suffix)
        )
        return f'{separator}'.join(regex_parts)

    # '999 000'
    if internal_start_suffix_all_nines and internal_end_suffix_all_nulls:
        ic('999 000')
        regex_parts.append(
            f'^{re.escape(common_prefix)}{start_suffix[0]}{start_suffix[1:]}$'
        )
        new_common_prefix = f'{common_prefix}' f'{end_suffix[0]}'
        new_start_suffix = f'{"0" * len(start_suffix[1:])}'
        new_end_suffix = f'{end_suffix[1:]}'
        digits_count = int(end_suffix[0]) - int(start_suffix[0]) - 1
        for i in range(digits_count):
            regex_parts.append(
                f'^{re.escape(common_prefix)}'
                f'{str(int(start_suffix[0]) + i + 1)}'
                f'[0-9]{{{len(start_suffix[1:])}}}$'
            )
        regex_parts.append(
            f'^{re.escape(common_prefix)}{end_suffix[0]}{end_suffix[1:]}$'
        )
        return f'{separator}'.join(regex_parts)

    # '999 999'
    if internal_start_suffix_all_nines and internal_end_suffix_all_nines:
        ic('999 999')
        regex_parts.append(
            f'^{re.escape(common_prefix)}{start_suffix[0]}{start_suffix[1:]}$'
        )
        new_common_prefix = f'{common_prefix}' f'{end_suffix[0]}'
        new_start_suffix = f'{"0" * len(start_suffix[1:])}'
        new_end_suffix = f'{end_suffix[1:]}'
        digits_count = int(end_suffix[0]) - int(start_suffix[0])
        for i in range(digits_count):
            regex_parts.append(
                f'^{re.escape(common_prefix)}'
                f'{str(int(start_suffix[0]) + i + 1)}'
                f'[0-9]{{{len(end_suffix[1:])}}}$'
            )
        return f'{separator}'.join(regex_parts)

    # '999 ___'
    if internal_start_suffix_all_nines:
        ic('999 ___')
        regex_parts.append(
            f'^{re.escape(common_prefix)}{start_suffix[0]}{start_suffix[1:]}$'
        )
        new_common_prefix = f'{common_prefix}' f'{end_suffix[0]}'
        new_start_suffix = f'{"0" * len(start_suffix[1:])}'
        new_end_suffix = f'{end_suffix[1:]}'
        regex_parts.extend(
            regex_from_all_nulls(
                new_common_prefix, new_start_suffix, new_end_suffix
            )
        )
        return f'{separator}'.join(regex_parts)

    # '___ 000'
    if not start_suffix_all_nulls and internal_end_suffix_all_nulls:
        ic('___ 000')
        regex_parts.extend(
            regex_to_all_nines(common_prefix, start_suffix, end_suffix)
        )
        regex_parts.append(
            f'^{re.escape(common_prefix)}{end_suffix[0]}'
            f'{"0" * (len(end_suffix[1:]))}$'
        )
        return f'{separator}'.join(regex_parts)

    # '___ 999'
    if (
        not internal_start_suffix_all_nulls
        and not internal_start_suffix_all_nines
        and internal_end_suffix_all_nines
    ):
        ic('___ 999')
        regex_parts = []
        for i in range(len(start_suffix) - 1, -1, -1):
            if len(start_suffix[i:]) == 1:
                regex_parts.append(
                    f'^{re.escape(common_prefix)}'
                    f'{start_suffix[0:i]}'
                    f'[{int(start_suffix[i])}-9]$'
                )
            elif len(start_suffix[i:]) - 1 == 1:
                regex_parts.append(
                    f'^{re.escape(common_prefix)}'
                    f'{start_suffix[0:i]}'
                    f'[{int(start_suffix[i + 1])}-9][0-9]$'
                )
            else:
                regex_parts.append(
                    f'^{re.escape(common_prefix)}'
                    f'{start_suffix[0:i]}'
                    f'[{int(start_suffix[i]) + 1}-'
                    f'{int(end_suffix[i])}]'
                    f'[0-9]{{{len(start_suffix) - i - 1}}}$'
                )
        return f'{separator}'.join(regex_parts)

    # '___ ___'
    if not start_suffix_all_nulls:
        ic('___ ___')
        for i in range(len(start_suffix) - 1, -1, -1):
            if len(start_suffix[i:]) == 1:
                regex_parts.append(
                    f'^{re.escape(common_prefix)}'
                    f'{start_suffix[0:i]}'
                    f'[{int(start_suffix[i])}-9]$'
                )
            elif len(start_suffix[i:]) - 1 == 1:
                regex_parts.append(
                    f'^{re.escape(common_prefix)}'
                    f'{start_suffix[0:i]}'
                    f'[{int(start_suffix[i]) + 1}-9][0-9]$'
                )
            elif len(start_suffix[i:]) < len(start_suffix):
                regex_parts.append(
                    f'^{re.escape(common_prefix)}'
                    f'{start_suffix[0:i]}'
                    f'[{int(start_suffix[0]) + 1}-9]'
                    f'[0-9]{{{len(start_suffix) - i - 1}}}$'
                )
            else:
                regex_parts.append(
                    f'^{re.escape(common_prefix)}'
                    f'{start_suffix[0:i]}'
                    f'[{int(start_suffix[0]) + 1}-'
                    f'{int(end_suffix[i]) - 1}]'
                    f'[0-9]{{{len(start_suffix) - i - 1}}}$'
                )
                new_start = (
                    f'{common_prefix}{end_suffix[0]}'
                    f'{"0" * (len(end_suffix[1:]))}'
                )
                new_end = f'{common_prefix}{end_suffix}'
                regex_parts.append(
                    range_to_regex(new_start, new_end, separator)
                )
    return f'{separator}'.join(regex_parts)


def regex_from_all_nulls(common_prefix, start_suffix, end_suffix):
    """Преобразует диапазон номеров, начинающийся с нулей,
    в регулярное выражение."""
    regex_parts = []
    for i in range(len(end_suffix)):
        if len(end_suffix[i:]) == 1:
            regex_parts.append(
                f'^{re.escape(common_prefix)}'
                f'{end_suffix[0:i]}'
                f'[{int(start_suffix[i])}-{int(end_suffix[i])}]$'
            )
        elif len(end_suffix[i:]) - 1 == 1:
            regex_parts.append(
                f'^{re.escape(common_prefix)}'
                f'{end_suffix[0:i]}'
                f'[{int(start_suffix[i])}-{int(end_suffix[i]) - 1}][0-9]$'
            )
        elif int(start_suffix[i]) == int(end_suffix[i]) - 1:
            regex_parts.append(
                f'^{re.escape(common_prefix)}'
                f'{end_suffix[0:i]}'
                f'{int(start_suffix[i])}'
                f'[0-9]{{{len(end_suffix[i:]) - 1}}}$'
            )
        else:
            regex_parts.append(
                f'^{re.escape(common_prefix)}'
                f'{end_suffix[0:i]}'
                f'[{int(start_suffix[i])}-{int(end_suffix[i]) - 1}]'
                f'[0-9]{{{len(end_suffix[i:]) - 1}}}$'
            )
    return regex_parts


def regex_to_all_nines(common_prefix, start_suffix, end_suffix):
    """Преобразует диапазон номеров, заканчивающийся на девятки,
    в регулярное выражение."""
    new_common_prefix = f'{common_prefix}' f'{start_suffix[0]}'
    new_start_suffix = f'{start_suffix[1:]}'
    new_end_suffix = f'{"9" * (len(end_suffix[1:]))}'
    regex_parts = []
    for i in range(len(new_start_suffix) - 1, -1, -1):
        if len(new_start_suffix[i:]) == 1:
            regex_parts.append(
                f'^{re.escape(new_common_prefix)}'
                f'{new_start_suffix[0:i]}'
                f'[{int(new_start_suffix[i])}-9]$'
            )
        elif len(new_start_suffix[i:]) - 1 == 1:
            regex_parts.append(
                f'^{re.escape(new_common_prefix)}'
                f'{new_start_suffix[0:i]}'
                f'[{int(new_start_suffix[i]) + 1}-9][0-9]$'
            )
        else:
            regex_parts.append(
                f'^{re.escape(common_prefix)}'
                f'{str(int(start_suffix[0]) + i)}'
                f'[{int(new_start_suffix[0]) + 1}-'
                f'{int(new_end_suffix[i])}]'
                f'[0-9]{{{len(new_start_suffix) - 1}}}$'
            )
            digits_count = int(end_suffix[0]) - int(start_suffix[0])
            for i in range(digits_count - 1):
                regex_parts.append(
                    f'^{re.escape(common_prefix)}'
                    f'{str(int(start_suffix[0]) + i + 1)}'
                    f'[0-9]{{{len(end_suffix[1:])}}}$'
                )
    return regex_parts


def find_groups_with_one_char_diff(strings):
    """Нахождение регулярных выражений, отличающихся одним символом."""
    masks = defaultdict(list)

    for s in strings:
        for i in range(len(s)):
            mask = s[:i] + '*' + s[i + 1:]
            masks[mask].append(s)

    result = []
    seen = set()

    for s in strings:
        added = False
        for i in range(len(s)):
            mask = s[:i] + '*' + s[i + 1:]
            group = masks[mask]
            if len(group) > 1 and group[0] not in seen:
                result.append(group)
                seen.update(group)
                added = True
                break
        if not added and s not in seen:
            result.append([s])
            seen.add(s)

    return result


def find_common_pattern(patterns):
    """Нахождение общих паттернов в списке регулярных выражений."""
    common_pattern = []
    for chars in zip(*patterns):
        if all(char == chars[0] for char in chars):
            common_pattern.append(chars[0])
        else:
            unique_chars = sorted(list(set(chars)))
            if len(unique_chars) > 1 and (
                ord(unique_chars[-1]) - ord(unique_chars[0])
                == len(unique_chars) - 1
            ):
                common_pattern.append(
                    f'[{unique_chars[0]}-{unique_chars[-1]}]'
                )
            else:
                common_pattern.append('[' + ''.join(unique_chars) + ']')
    return ''.join(common_pattern)


def optimize_regex_patterns(regex_list, use_dot):
    """Оптимизация регулярных выражений."""
    # Замена `[a-a]`, где `a` - цифра, на 'a' и `[0-9]` на символ `.`
    regex_list = [
        re.sub(
            r'\[([0-9])-([0-9])\]',
            lambda m: ic(m.group(1))
            if (ic(m.group(1)) == ic(m.group(2)))
            else ic(m.group(0)),
            regex,
        )
        for regex in regex_list
    ]
    if use_dot:
        regex_list = [re.sub(r'\[0-9\]', r'.', regex) for regex in regex_list]
    ic('start optimization')
    ic(regex_list)

    # Регулярное выражение для разбора частей регулярных выражений
    regex_pattern = re.compile(r'\^([^\$]+)\$')
    ic(regex_pattern)

    # Разбираем все регулярные выражения и сохраняем их части
    parsed_patterns = []
    for regex in regex_list:
        parts = regex_pattern.findall(regex)
        ic(parts)
        parsed_patterns.append(parts)
        ic(parsed_patterns)

    # Определяем общие части среди всех паттернов
    common_patterns = []
    for parts in zip(*parsed_patterns):
        common_patterns.append(find_common_pattern(parts))
        ic(common_patterns)

    # Объединяем общие паттерны в одно оптимизированное регулярное выражение
    optimized_regex = '^' + ''.join(common_patterns) + '$'
    ic(optimized_regex)
    ic('end optimization')

    return [optimized_regex]


def pools_to_regex(groups, separator, use_dot):
    """
    Основная функция для преобразования пулов телефонных номеров
    в строку регулярного выражения.
    """
    regex_list = [
        range_to_regex(start, end, separator) for start, end in groups
    ]
    ic(regex_list)
    split_regex_list = []
    for element in regex_list:
        split_regex_list.extend(element.split(separator))
    ic(split_regex_list)
    optimized_list = []
    list_similar_strings = find_groups_with_one_char_diff(split_regex_list)
    for similar_strings in list_similar_strings:
        optimized_result = optimize_regex_patterns(similar_strings, use_dot)
        ic(optimized_result)
        optimized_list.extend(optimized_result)
    ic(optimized_list)
    return f'{separator}'.join(optimized_list)


def main():
    parser = argparse.ArgumentParser(
        description=(
            'Преобразование массивов и пулов телефонных номеров '
            'в регулярное выражение.'
        )
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-n',
        '--numbers',
        dest='numbers',
        nargs='+',
        help=(
            'Массив телефонных номеров. '
            'Номера указываются через пробел. '
            'Например: 10 11 12 13 14 15.'
        ),
    )
    group.add_argument(
        '-p',
        '--pools',
        dest='pools',
        nargs='+',
        help=(
            'Пулы телефонных номеров. '
            'Пулы указываются через пробел. '
            'Например: 100 199 45000 46123.'
        ),
    )
    group.add_argument(
        '-fn',
        '--file_numbers',
        dest='filename_numbers',
        help=(
            'Имя txt-файла с массивом номеров в директории с exe-файлом или '
            'путь до txt-файла. Номера в файле указываются через пробел. '
            'Например: 10 11 12 13 14 15.'
        ),
    )
    group.add_argument(
        '-fp',
        '--file_pools',
        dest='filename_pools',
        help=(
            'Имя txt-файла с массивом пулов номеров в директории с exe-файлом '
            'или путь до txt-файла. Номера в файле указываются через пробел. '
            'Например: 100 199 45000 46123.'
        ),
    )
    parser.add_argument(
        '-s',
        '--separator',
        dest='separator',
        default='|',
        help=(
            'Разделитель регулярных выражений. '
            'Указывается в кавычках. Например: ";" '
            '(по умолчанию "|").'
        ),
    )
    parser.add_argument(
        '-d',
        '--dot',
        dest='dot',
        action='store_true',
        help=('Использовать символ "." вместо [0-9].'),
    )
    args = parser.parse_args()

    if args.numbers:
        result = group_numbers(args.numbers, args.separator, args.dot)
    elif args.pools:
        result = split_to_pools(args.pools, args.separator, args.dot)
    elif args.filename_numbers:
        with open(args.filename_numbers) as f:
            file_numbers = f.read().split()
        result = group_numbers(file_numbers, args.separator, args.dot)
    elif args.filename_pools:
        with open(args.filename_pools) as f:
            file_pools = f.read().split()
        result = split_to_pools(file_pools, args.separator, args.dot)
    print(result)


if __name__ == '__main__':
    main()
