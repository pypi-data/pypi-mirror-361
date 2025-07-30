"""HSLConverterモジュール:

16進数で表現されたカラーパターン文字列から、
Hue、Saturation、Luminance (HSL) の各値を算出する機能を提供します。
"""
# hsl_converter.py

# MIT License
# Copyright (c) 2025 kazuma tunomori
#
# Permission is hereby granted, free of charge, to any person obtaining a copy...


class HSLConverter:
    """Color pattern から HSL (Hue, Saturation, Luminance) 値を生成するクラス。

    定数に基づき、16進数で表現されたカラーパターンの各パーツから
    HSLの各値を計算し、スケール変換を行う。

    Attributes:
        MAX_HUE (int): 最大の色相 (Hue) 値 (360度)
        MAX_SATURATION (int): 最大の彩度 (Saturation) 値 (65%)
        MAX_LUMINANCE (int): 最大の輝度 (Luminance) 値 (75%)
        HUE_SCALE (float): Hueの16進数値から360度へのスケール係数。
        SATURATION_SCALE (float): Saturationの16進数値から彩度へのスケール係数。
        LUMINANCE_SCALE (float): Luminanceの16進数値から輝度へのスケール係数。

    Methods:
        from_pattern(color_pattern: str) -> tuple[float, float, float]:
            16進数カラーパターン文字列からHSL値を計算して返す。

        _calculate_hue(hue_hex: str) -> float:
            色相を16進数からスケール変換して計算。

        _calculate_saturation(sat_hex: str) -> float:
            彩度を16進数からスケール変換して計算。

        _calculate_luminance(lum_hex: str) -> float:
            輝度を16進数からスケール変換して計算。

    """

    MAX_HUE = 360
    MAX_SATURATION = 65
    MAX_LUMINANCE = 75

    HUE_SCALE = MAX_HUE / 0x0FFF  # 0x0FFF (4095) を 360 にスケール
    SATURATION_SCALE = 20 / 0x00FF  # 255 を 20 にスケール
    LUMINANCE_SCALE = 20 / 0x00FF  # 255 を 20 にスケール

    @classmethod
    def from_pattern(cls, color_pattern: str) -> tuple[float, float, float]:
        """color_pattern から H, S, L を取得"""
        hue = cls._calculate_hue(color_pattern[:3])
        saturation = cls._calculate_saturation(color_pattern[3:5])
        luminance = cls._calculate_luminance(color_pattern[5:7])
        return hue, saturation, luminance

    @classmethod
    def _calculate_hue(cls, hue_hex: str) -> float:
        """16進数の hue を 0-360 に変換"""
        return round(int(hue_hex, 16) * cls.HUE_SCALE)

    @classmethod
    def _calculate_saturation(cls, sat_hex: str) -> float:
        """16進数の saturation を 0-100 に変換"""
        return round(cls.MAX_SATURATION - int(sat_hex, 16) * cls.SATURATION_SCALE)

    @classmethod
    def _calculate_luminance(cls, lum_hex: str) -> float:
        """16進数の luminance を 0-100 に変換"""
        return round(cls.MAX_LUMINANCE - int(lum_hex, 16) * cls.LUMINANCE_SCALE)
