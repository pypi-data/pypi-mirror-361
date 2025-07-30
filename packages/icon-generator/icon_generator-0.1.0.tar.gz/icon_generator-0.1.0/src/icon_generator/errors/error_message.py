"""例外メッセージを管理するEnumを定義するモジュール。

このモジュールは、例外メッセージのテンプレートをEnumで一元管理し、
動的なメッセージ生成をサポートします。
"""
# error_message.py

# MIT License
# Copyright (c) 2025 kazuma tunomori
#
# Permission is hereby granted, free of charge, to any person obtaining a copy...
from enum import Enum


class ErrorMessages(Enum):
    """例外で使用するメッセージテンプレートを定義するEnumクラス。

    各メッセージはformatメソッドで動的に値を埋め込むことが可能です。
    """

    # GitIconGenerator.generate_on_memory but common?
    IDENTICON_GENERATION_FAILED = "Identicon image generation failed"

    # PatternGenerator.__init__
    INVALID_HEX_LENGTH = "hex_pattern must be exactly {length} characters long."
    INVALID_HEX_PATTERN = (
        "hex_pattern must only contain hexadecimal characters (0-9, a-f)."
    )

    # PatternGenerator.apply_color
    RGB_PATTERN_LENGTH = "rgb_pattern must be a list of 3 integers (R, G, B)."
    RGB_VALUE_RANGE = "Each RGB value must be an integer between 0 and 255."

    def format(self, **kwargs: str | int) -> str:
        """メッセージテンプレートにキーワード引数を埋め込み、フォーマット済みの文字列を返す。

        キーが不足している場合は、フォーマットエラーを示す文字列を返します。

        Args:
            **kwargs: メッセージ内のプレースホルダーに埋め込む値。

        Returns:
            フォーマット済みメッセージ文字列。

        """
        try:
            return self.value.format(**kwargs)
        except KeyError as e:
            return f"[FORMAT ERROR] Missing key: {e.args[0]} in message template"
