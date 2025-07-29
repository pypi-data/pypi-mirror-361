from dataclasses import dataclass
from typing import Optional
import discord

@dataclass
class AuthorBlock:
    name: Optional[str] = None
    icon_url: Optional[str] = None
    url: Optional[str] = None

    @classmethod
    def from_string(cls, raw: str):
        parts = [p.strip() for p in raw.split("&&")]
        return cls(*parts[:3])

@dataclass
class FieldBlock:
    name: Optional[str] = None
    value: Optional[str] = None
    inline: bool = False

    @classmethod
    def from_string(cls, raw: str):
        parts = [p.strip() for p in raw.split("&&")]
        name, value = parts[:2] if len(parts) >= 2 else (None, None)
        inline = "inline" in raw
        return cls(name, value, inline)

@dataclass
class FooterBlock:
    text: Optional[str] = None
    icon_url: Optional[str] = None

    @classmethod
    def from_string(cls, raw: str):
        parts = [p.strip() for p in raw.split("&&")]
        return cls(*parts[:2])

@dataclass
class ButtonBlock:
    label: Optional[str] = None
    emoji: Optional[str] = None
    url: Optional[str] = None
    style: discord.ButtonStyle = discord.ButtonStyle.gray
    disabled: bool = False

    @classmethod
    def from_string(cls, raw: str):
        parts = [p.strip() for p in raw.split("&&")]
        label = parts[0] if len(parts) > 0 else None
        emoji = parts[1] if len(parts) > 1 else None
        url = parts[2] if len(parts) > 2 else None
        style_str = parts[3].lower() if len(parts) > 3 else "gray"
        disabled = "disabled" in raw.lower()

        style = {
            "gray": discord.ButtonStyle.gray,
            "green": discord.ButtonStyle.green,
            "red": discord.ButtonStyle.red,
            "blue": discord.ButtonStyle.blurple,
        }.get(style_str, discord.ButtonStyle.gray)

        return cls(label, emoji, url, style, disabled)
