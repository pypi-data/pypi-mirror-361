"""GitIconGeneratorモジュール:

UUIDを元にアイデンティコン画像を生成する機能を提供します。
"""
# git_icon_generator.py

# MIT License
# Copyright (c) 2025 kazuma tunomori
#
# Permission is hereby granted, free of charge, to any person obtaining a copy...

import uuid
from io import BytesIO

from PIL import Image, UnidentifiedImageError
from PIL.Image import Resampling

from src.icon_generator.errors import ErrorMessages
from src.icon_generator.generator import Generator

from .core.color import RGBGenerator
from .core.pattern import PatternGenerator


class GitIconGenerator(Generator):
    """UUIDを元にアイデンティコンを生成するクラス。

    Attributes:
        _identicon_pattern (PatternGenerator):
            UUIDの一部から生成したパターンジェネレータ。
        _color (RGBGenerator): UUIDの一部から生成したRGBカラー。

    Methods:
        generate_on_memory() -> BytesIO:
            メモリ上にPNG形式のアイデンティコン画像を生成し、BytesIOオブジェクトで返す。

    """

    def __init__(self, unique_uuid: uuid.UUID) -> None:
        """GitIconGeneratorのコンストラクタ。

        Args:
            unique_uuid (uuid.UUID): アイデンティコン生成の元となるUUID。

        """
        self._identicon_pattern = PatternGenerator(unique_uuid.hex[:15])
        self._color = RGBGenerator(unique_uuid.hex[25:])

    def generate_on_memory(self, image_size: int = 600) -> BytesIO:
        """UUIDに基づくパターンとカラーを適用したアイデンティコン画像を生成し、メモリ上にPNG形式で保持したBytesIOオブジェクトを返す。

        Returns:
            BytesIO: PNG画像のバイナリデータを保持したメモリオブジェクト。

        """
        colored_pattern = self._identicon_pattern.apply_color(
            rgb_pattern=self._color.rgb,
        )

        try:
            # 画像作成
            img = Image.fromarray(colored_pattern.astype("uint8"))
            img = img.resize((image_size, image_size), resample=Resampling.NEAREST)

            # メモリに保存
            img_io = BytesIO()
            img.save(img_io, "PNG")
            img_io.seek(0)

        except (ValueError, OSError, UnidentifiedImageError) as e:
            message = ErrorMessages.IDENTICON_GENERATION_FAILED.value
            raise RuntimeError(message) from e

        else:
            return img_io
