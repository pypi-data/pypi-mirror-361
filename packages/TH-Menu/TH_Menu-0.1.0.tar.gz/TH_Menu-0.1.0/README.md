# 📦 TH-MENU

**TH-MENU** — это библиотека для Python, которая позволяет создавать вложенные меню в Discord-ботах с использованием [`nextcord`](https://github.com/nextcord/nextcord), включая автоматическую кнопку 🔙 "Назад" и поддержку неограниченной глубины подкатегорий.

---

## 🚀 Возможности

- 📋 Простое декларативное описание меню
- 🧭 Поддержка вложенности без ограничений
- 🔙 Автоматическая кнопка "Назад" на всех уровнях
- 🧼 Чистая и гибкая архитектура
- ⏱ Настраиваемый `timeout` и `ephemeral` (приватность сообщения)
- ✅ Поддержка `slash`-команд и обычных команд

---

## 📦 Установка

Установка из GitHub:

```bash
pip install 
```

## ⚙️ Пример использования
```py
from TH_Menu import SmartMenu
import nextcord
from nextcord.ext import commands

bot = commands.Bot(command_prefix="!")

menu = SmartMenu(
    title="📋 Главное меню",
    structure={
        "⚙ Настройки": {
            "🔒 Безопасность": {
                "🛡️ 2FA": lambda i, v: i.followup.send("Настройки 2FA", ephemeral=True),
                "🔑 Пароль": lambda i, v: i.followup.send("Смена пароля", ephemeral=True)
            },
            "🎨 Внешний вид": lambda i, v: i.followup.send("Выбор темы", ephemeral=True)
        },
        "📊 Статистика": lambda i, v: i.followup.send("Нет данных", ephemeral=True),
        "❓ Помощь": {
            "📬 Поддержка": lambda i, v: i.followup.send("Обратитесь к @Admin", ephemeral=True)
        }
    },
    timeout=120,
    ephemeral=True
)

@bot.slash_command(name="меню", description="Открыть главное меню")
async def меню(interaction: nextcord.Interaction):
    await menu.send(interaction)

bot.run("")
```

В случае если подкатегорий много

```py
from TH_Menu import SmartMenu
import nextcord
from nextcord.ext import commands

intents = nextcord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

menu = SmartMenu(
    title="📚 Энциклопедия Живой Природы",
    structure={
        "Животные": {
            "Млекопитающие": {
                "Хищные": {
                    "Кошачьи": {
                        "Лев": lambda i, v: i.followup.send("🦁 Лев — царь зверей", ephemeral=True),
                        "Тигр": lambda i, v: i.followup.send("🐯 Тигр — ночной охотник", ephemeral=True)
                    },
                    "Псовые": {
                        "Волк": lambda i, v: i.followup.send("🐺 Волк — социальный хищник", ephemeral=True),
                        "Лиса": lambda i, v: i.followup.send("🦊 Лиса — хитрая охотница", ephemeral=True)
                    }
                },
                "Приматы": {
                    "Обезьяны": {
                        "Шимпанзе": lambda i, v: i.followup.send("🐵 Шимпанзе — умный примат", ephemeral=True),
                        "Горилла": lambda i, v: i.followup.send("🦍 Горилла — могучий великан", ephemeral=True)
                    }
                }
            },
            "Птицы": {
                "Хищные птицы": {
                    "Орёл": lambda i, v: i.followup.send("🦅 Орёл — символ силы", ephemeral=True),
                    "Сова": lambda i, v: i.followup.send("🦉 Сова — ночной охотник", ephemeral=True)
                }
            }
        },
        "Растения": {
            "Цветы": {
                "Розы": lambda i, v: i.followup.send("🌹 Розы — символ любви", ephemeral=True),
                "Тюльпаны": lambda i, v: i.followup.send("🌷 Тюльпаны — весенние красавцы", ephemeral=True)
            },
            "Деревья": {
                "Хвойные": {
                    "Сосна": lambda i, v: i.followup.send("🌲 Сосна — символ вечности", ephemeral=True)
                },
                "Лиственные": {
                    "Дуб": lambda i, v: i.followup.send("🌳 Дуб — символ силы", ephemeral=True)
                }
            }
        }
    },
    timeout=180,
    ephemeral=True
)

@bot.slash_command(name="энциклопедия", description="Открыть вложенное меню с природой")
async def encyclopedia(interaction: nextcord.Interaction):
    await menu.send(interaction)

bot.run("")
```

## 🧠 Как это работает?
- Структура меню задаётся в виде обычного dict
- Если значение — это dict, оно воспринимается как подменю
- Если значение — это lambda или async def, это действие
- Меню можно вложить на любую глубину
- Переход назад осуществляется автоматически

## 📂 Структура меню
```py
{
    "Категория A": {
        "Подкатегория B": {
            "Действие C": callback
        }
    },
    "Категория D": callback
}
```

