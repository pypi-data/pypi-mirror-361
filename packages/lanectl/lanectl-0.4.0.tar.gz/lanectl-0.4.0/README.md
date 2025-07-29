# 🧱 lanectl

**lanectl** is the embed scripting engine for infrared.

It parses a block of text, replaces variables, and turns it into an embed with an optional `discord.ui.View`.  
No GUI. No builder. Just script → message.

---

## ▶ Example

```
{content:welcome, {user.name}}
{title:infrared online}
{description:this server runs cold}
{color:#ED1C24}
{author:Pusha && https://i.imgur.com/pusha.png}
{field:Rank && King && inline}
{footer:real bars only && https://i.imgur.com/footer.png}
{button:enter && 🚪 && https://infrared.something && red}
{timestamp}
```

---

## ✅ Supported Fields

All fields are optional. Missing values are ignored.

| Field         | Format                                    |
|---------------|-------------------------------------------|
| `content`     | `{content:text}`                          |
| `title`       | `{title:text}`                            |
| `description` | `{description:text}`                      |
| `color`       | `{color:#hex}`                            |
| `author`      | `{author:Name && Icon && URL}`            |
| `footer`      | `{footer:Text && Icon}`                   |
| `field`       | `{field:Name && Value && inline}`         |
| `button`      | `{button:Label && Emoji && URL && Style}` |
| `timestamp`   | `{timestamp}`                             |

---

## 🔀 Variables

Variables are replaced in any field.

```
{user}, {user.name}, {user.id}, {user.avatar}, {user.created_at}, {user.joined_at}
{guild}, {guild.name}, {guild.id}, {guild.owner}, {guild.member_count}, {guild.created_at}
{target}, {target.name}, {target.id}, {target.avatar}, ...
```

---

## 🧪 Bot Usage

```py
from lanectl import Lane

@bot.command()
async def createembed(ctx, *, script: str):
    r = Lane(script, ctx.author)

    await ctx.send(
        content=r.content,
        embed=r.render(),
        view=r.view()
    )
```

If the script defines nothing, `r.content`, `r.render()`, and `r.view()` all return `None`.

---

## ⚙️ Install

```bash
pip install lanectl
```

Or just copy the `lanectl/` folder into your project, i dont really care.

---
