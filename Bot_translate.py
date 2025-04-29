import discord
from discord.ext import commands
from discord import app_commands
from googletrans import Translator
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
translator = Translator()

# ID du rôle autorisé
ROLE_AUTORISE = 1362033895100387400

# Liste pour stocker les utilisateurs ayant activé la traduction automatique
auto_translate_users = set()

def est_autorise(interaction: discord.Interaction):
    return (
        interaction.user.guild_permissions.administrator or
        any(role.id == ROLE_AUTORISE for role in interaction.user.roles)
    )

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Commandes synchronisées : {len(synced)}")
    except Exception as e:
        print(e)

@bot.tree.command(name="traduire", description="Traduire un texte français/anglais")
@app_commands.describe(texte="Le texte à traduire")
async def traduire(interaction: discord.Interaction, texte: str):
    if not est_autorise(interaction):
        await interaction.response.send_message("❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        return

    detection = translator.detect(texte)
    source_lang = detection.lang

    if source_lang == 'fr':
        traduction = translator.translate(texte, src='fr', dest='en').text
        await interaction.response.send_message(f"**Traduction (FR → EN) :** {traduction}", ephemeral=True)
    elif source_lang == 'en':
        traduction = translator.translate(texte, src='en', dest='fr').text
        await interaction.response.send_message(f"**Traduction (EN → FR) :** {traduction}", ephemeral=True)
    else:
        await interaction.response.send_message("Langue non supportée. | Unsupported language.", ephemeral=True)

@bot.tree.command(name="auto_traduction", description="Activer ou désactiver la traduction automatique des messages")
@app_commands.describe(mode="Choisissez 'on' pour activer, 'off' pour désactiver")
@app_commands.choices(mode=[
    app_commands.Choice(name="on", value="on"),
    app_commands.Choice(name="off", value="off")
])
async def auto_traduction(interaction: discord.Interaction, mode: app_commands.Choice[str]):
    if not est_autorise(interaction):
        await interaction.response.send_message("❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        return

    if mode.value == "on":
        auto_translate_users.add(interaction.user.id)
        await interaction.response.send_message("✅ Traduction automatique activée. | Auto translation enabled.", ephemeral=True)
    else:
        auto_translate_users.discard(interaction.user.id)
        await interaction.response.send_message("❎ Traduction automatique désactivée. | Auto translation disabled.", ephemeral=True)

@bot.tree.context_menu(name="traduire_message")
async def traduire_message_context(interaction: discord.Interaction, message: discord.Message):
    if not est_autorise(interaction):
        await interaction.response.send_message("❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        return

    detection = translator.detect(message.content)
    source_lang = detection.lang

    if source_lang == 'fr':
        traduction = translator.translate(message.content, src='fr', dest='en').text
        await interaction.response.send_message(f"**Traduction (FR → EN) :** {traduction}", ephemeral=True)
    elif source_lang == 'en':
        traduction = translator.translate(message.content, src='en', dest='fr').text
        await interaction.response.send_message(f"**Traduction (EN → FR) :** {traduction}", ephemeral=True)
    else:
        await interaction.response.send_message("Langue non supportée pour la traduction.", ephemeral=True)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.author.id in auto_translate_users:
        detection = translator.detect(message.content)
        source_lang = detection.lang

        if source_lang == 'fr':
            traduction = translator.translate(message.content, src='fr', dest='en').text
        elif source_lang == 'en':
            traduction = translator.translate(message.content, src='en', dest='fr').text
        else:
            traduction = None

        if traduction:
            try:
                await message.author.send(f"**Traduction automatique | Auto Translation :**\n{traduction}")
            except:
                print(f"Impossible d'envoyer un DM à {message.author.name}")

    await bot.process_commands(message)

bot.run(os.getenv('TOKEN'))
