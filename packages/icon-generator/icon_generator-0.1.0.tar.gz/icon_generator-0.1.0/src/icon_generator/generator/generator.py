"""generator.py

アイデンティコンやユニーク画像生成用の抽象基底クラス (Generator) を定義します。
各生成器は UUID をベースに画像を生成する必要があります。
"""
# MIT License
# Copyright (c) 2025 kazuma tunomori
#
# Permission is hereby granted, free of charge, to any person obtaining a copy...

from abc import ABC, abstractmethod
from io import BytesIO
from uuid import UUID


class Generator(ABC):
    """画像生成器の抽象基底クラス。

    このクラスを継承するサブクラスは、
    UUID に基づく画像生成ロジックを実装する必要があります。
    """

    @abstractmethod
    def __init__(self, unique_uuid: UUID) -> None:
        """初期化メソッド。

        Args:
            unique_uuid (UUID): 画像生成に使用するユニークなUUID。

        """
        ...

    @abstractmethod
    def generate_on_memory(self, image_size: int = 600) -> BytesIO:
        """メモリ上で画像を生成し、BytesIO形式で返す。

        Args:
            image_size (int, optional):
                出力画像の一辺のサイズ(ピクセル)。デフォルトは600

        Returns:
            BytesIO: メモリ上に保存された画像のバイナリデータ。

        """
        ...
