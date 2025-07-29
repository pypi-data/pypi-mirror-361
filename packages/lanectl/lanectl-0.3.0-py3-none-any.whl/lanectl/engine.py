import discord
from typing import Optional, List
import datetime

from .blocks import AuthorBlock, FieldBlock, FooterBlock, ButtonBlock
from .inject import inject_vars
from .utils import extract_blocks

class Lane:
    def __init__(self, script: str, member: discord.Member, target: Optional[discord.Member] = None):
        self.member = member
        self.target = target or member
        self.script = inject_vars(script, self.member, self.target)

        self.content = None
        self.title = None
        self.description = None
        self.color = None
        self.timestamp = None
        self.image = None
        self.thumbnail = None
        self.author: Optional[AuthorBlock] = None
        self.footer: Optional[FooterBlock] = None
        self.fields: List[FieldBlock] = []
        self.buttons: List[ButtonBlock] = []

        self._parse()

    def _parse(self):
        blocks = extract_blocks(self.script)
        for raw in blocks:
            if raw.startswith("content:"):
                self.content = raw[8:].strip()
            elif raw.startswith("title:"):
                self.title = raw[6:].strip()
            elif raw.startswith("description:"):
                self.description = raw[12:].strip()
            elif raw.startswith("color:"):
                try:
                    self.color = int(raw[6:].replace("#", ""), 16)
                except ValueError:
                    self.color = None
            elif raw.startswith("timestamp"):
                self.timestamp = datetime.datetime.now()
            elif raw.startswith("image:"):
                self.image = raw[6:].strip()
            elif raw.startswith("thumbnail:"):
                self.thumbnail = raw[10:].strip()
            elif raw.startswith("author:"):
                self.author = AuthorBlock.from_string(raw[7:].strip())
            elif raw.startswith("footer:"):
                self.footer = FooterBlock.from_string(raw[7:].strip())
            elif raw.startswith("field:"):
                self.fields.append(FieldBlock.from_string(raw[6:].strip()))
            elif raw.startswith("button:"):
                self.buttons.append(ButtonBlock.from_string(raw[7:].strip()))

    def render(self) -> Optional[discord.Embed]:
        if not any([self.title, self.description, self.fields]):
            return None

        embed = discord.Embed(
            title=self.title,
            description=self.description,
            color=self.color or 0x020000,
            timestamp=self.timestamp,
        )

        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)
        if self.image:
            embed.set_image(url=self.image)
        if self.author and self.author.name:
            embed.set_author(name=self.author.name, icon_url=self.author.icon_url, url=self.author.url)
        if self.footer and self.footer.text:
            embed.set_footer(text=self.footer.text, icon_url=self.footer.icon_url)
        for f in self.fields:
            embed.add_field(name=f.name or "\u200b", value=f.value or "\u200b", inline=f.inline)

        return embed

    def view(self) -> Optional[discord.ui.View]:
        if not self.buttons:
            return None

        view = discord.ui.View()
        for b in self.buttons:
            view.add_item(discord.ui.Button(
                label=b.label,
                url=b.url,
                style=b.style,
                emoji=b.emoji,
                disabled=b.disabled
            ))
        return view
