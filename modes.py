#!/usr/bin/env python3
"""EXNIHILO generation modes.

These modes are intentionally independent experiments. None uses English
knowledge or a vocabulary.
"""

from exnihilo import LETTERS, uniform_index, random_byte_stream


def pure_char_stream(byte_stream, length: int) -> str:
    return ''.join(LETTERS[uniform_index(byte_stream, len(LETTERS))] for _ in range(length))


def spaced_char_stream(byte_stream, length: int) -> str:
    out = []
    for _ in range(length):
        # Space is just another random symbol; it has no linguistic meaning.
        index = uniform_index(byte_stream, len(LETTERS) + 1)
        out.append(' ' if index == len(LETTERS) else LETTERS[index])
    return ''.join(out)


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=('chars', 'spaces'), default='chars')
    parser.add_argument('--length', type=int, default=1000)
    args = parser.parse_args()
    if args.length < 1:
        parser.error('--length must be >= 1')
    source = random_byte_stream()
    if args.mode == 'chars':
        print(pure_char_stream(source, args.length))
    else:
        print(spaced_char_stream(source, args.length))


if __name__ == '__main__':
    main()
