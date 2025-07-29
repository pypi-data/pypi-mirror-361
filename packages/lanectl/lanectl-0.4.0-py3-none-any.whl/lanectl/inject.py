import discord

def inject_vars(text: str, member: discord.Member, target: discord.Member = None) -> str:
    if not text:
        return ""

    if target is None:
        target = member

    guild = member.guild
    replacements = {
        "{user}": member.mention,
        "{user.name}": member.name,
        "{user.id}": str(member.id),
        "{user.avatar}": member.display_avatar.url,
        "{user.joined_at}": discord.utils.format_dt(member.joined_at, style="R"),
        "{user.created_at}": discord.utils.format_dt(member.created_at, style="R"),

        "{target}": target.mention,
        "{target.name}": target.name,
        "{target.id}": str(target.id),
        "{target.avatar}": target.display_avatar.url,
        "{target.joined_at}": discord.utils.format_dt(target.joined_at, style="R"),
        "{target.created_at}": discord.utils.format_dt(target.created_at, style="R"),

        "{guild}": guild.name,
        "{guild.name}": guild.name,
        "{guild.id}": str(guild.id),
        "{guild.owner}": guild.owner.name,
        "{guild.owner.id}": str(guild.owner.id),
        "{guild.member_count}": str(guild.member_count),
        "{guild.created_at}": discord.utils.format_dt(guild.created_at, style="R"),
        "{guild.banner}": guild.banner.url if guild.banner else "",
        "{guild.vanity}": f"/{guild.vanity_url_code}" if guild.vanity_url_code else "none",
    }

    for key, val in replacements.items():
        text = text.replace(key, val or "")

    return text
