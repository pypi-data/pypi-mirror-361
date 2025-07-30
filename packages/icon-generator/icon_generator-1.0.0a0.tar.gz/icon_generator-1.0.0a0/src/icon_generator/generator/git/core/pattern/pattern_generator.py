"""PatternGeneratorモジュール:

16進数文字列からアイデンティコン用の左右対称パターンを生成するクラスを提供します。
"""
# MIT License
# Copyright (c) 2025 kazuma tunomori
#
# Permission is hereby granted, free of charge, to any person obtaining a copy...

import numpy as np
from numpy.typing import NDArray

from src.icon_generator.errors import ErrorMessages


class PatternGenerator:
    """16進数の文字列からアイデンティコンのパターンを生成するクラス。

    Attributes:
        PATTERN_WIDTH (int): パターンの幅(固定値5)
        PATTERN_HEIGHT (int): パターンの高さ(固定値3)
        pattern (NDArray[np.int_]): 生成された2次元のバイナリパターン配列。
            1は色付き部分、0は白背景を表す。

    Methods:
        _create_pattern(hex_pattern: str) -> NDArray[np.int_]:
            16進数文字列を基に左右対称かつ90度回転したパターンを生成する。

        _mirror_pattern(pattern: NDArray[np.int_]) -> NDArray[np.int_]:
            入力パターンを左右対称にミラーリングする。

        apply_color(rgb_pattern: list[int]) -> NDArray[np.int_]:
            バイナリパターンにRGBカラーを適用し、カラー画像用の3次元配列を返す。

    """

    PATTERN_WIDTH = 5
    PATTERN_HEIGHT = 3
    WHITE_RGB = (255, 255, 255)
    RGB_PATTERN_LENGTH = 3
    RGB_VALUE_MIN = 0
    RGB_VALUE_MAX = 255

    def __init__(self, hex_pattern: str) -> None:
        """16進数の文字列からパターンを生成"""
        expected_len = self.PATTERN_WIDTH * self.PATTERN_HEIGHT
        if len(hex_pattern) != expected_len:
            message = ErrorMessages.INVALID_HEX_LENGTH.format(length=expected_len)
            raise ValueError(message)

        if not all(c in "0123456789abcdefABCDEF" for c in hex_pattern):
            message = ErrorMessages.INVALID_HEX_PATTERN.value
            raise ValueError(message)

        self.pattern = self._create_pattern(hex_pattern=hex_pattern)

    def _create_pattern(self, hex_pattern: str) -> NDArray[np.int_]:
        """16進数の文字列を基に2次元のパターンを作成"""
        binary_pattern = np.array(
            [(1 if int(x, 16) % 2 == 0 else 0) for x in hex_pattern],
        ).reshape(self.PATTERN_HEIGHT, self.PATTERN_WIDTH)

        # 左右対称にミラーリング
        mirrored_pattern = self._mirror_pattern(pattern=binary_pattern)

        # 90度回転して最終パターンを作成
        return np.rot90(m=mirrored_pattern, k=3)

    def _mirror_pattern(self, pattern: NDArray[np.int_]) -> NDArray[np.int_]:
        """左右対称のミラーリングを行う"""
        return pattern[[2, 1, 0, 1, 2]]

    def apply_color(self, rgb_pattern: list[int]) -> NDArray[np.int_]:
        """パターンにRGBカラーを適用した配列を返す"""
        if not (
            isinstance(rgb_pattern, list)  # type: ignore[reportUnnecessaryIsInstance]
            and len(rgb_pattern) == self.RGB_PATTERN_LENGTH
        ):
            message = ErrorMessages.RGB_PATTERN_LENGTH.value
            raise ValueError(message)

        if not all(
            isinstance(v, int)  # type: ignore[reportUnnecessaryIsInstance]
            and self.RGB_VALUE_MIN <= v <= self.RGB_VALUE_MIN
            for v in rgb_pattern
        ):
            message = ErrorMessages.RGB_VALUE_RANGE.value
            raise ValueError(message)

        color_pattern = np.zeros(shape=(*self.pattern.shape, 3), dtype=int)
        color_pattern[self.pattern == 0] = self.WHITE_RGB
        color_pattern[self.pattern == 1] = rgb_pattern
        return color_pattern


if __name__ == "__main__":
    example_hex = "0123456789abcde"
    pg = PatternGenerator(example_hex)
    print("binary_pattern (3x5):")
    print(
        np.array([(1 if int(x, 16) % 2 == 0 else 0) for x in example_hex]).reshape(
            pg.PATTERN_HEIGHT,
            pg.PATTERN_WIDTH,
        ),
    )
    print("\nfinal pattern after rotation (5x5):")
    print(pg.pattern)
