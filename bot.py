import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

DB_NAME = "notes.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            user_id INTEGER NOT NULL,
            note TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# bot init wooooooooooooo
intents = discord.Intents.default()
intents.members = True  # Needed to fetch member details
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# Slash commands
class Notes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="create", description="Create a new note.")
    async def add_note(self, interaction: discord.Interaction, note: str):
        user_id = interaction.user.id
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (user_id, note) VALUES (?, ?)", (user_id, note))
        conn.commit()
        conn.close()
        await interaction.response.send_message(f"Note added: {note}", ephemeral=True)

    @app_commands.command(name="list", description="List all your notes.")
    async def list_notes(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT note FROM notes WHERE user_id = ?", (user_id,))
        notes = cursor.fetchall()
        conn.close()

        if notes:
            notes_list = "\n".join(f"- {note[0]}" for note in notes)
            await interaction.response.send_message(f"Your notes:\n{notes_list}", ephemeral=True)
        else:
            await interaction.response.send_message("You have no notes.", ephemeral=True)

    @app_commands.command(name="delete_all", description="Delete all your notes.")
    async def delete_notes(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        await interaction.response.send_message("All your notes have been deleted.", ephemeral=True)

    @app_commands.command(name="list_all", description="View all notes by all users of note-bot.")
    async def view_all(self, interaction: discord.Interaction):
        if interaction.user.id == ID:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, note FROM notes")
            notes = cursor.fetchall()
            conn.close()

            if notes:
                note_details = []
                for user_id, note in notes:
                    user = interaction.guild.get_member(user_id)
                    username = user.name if user else f"Unknown User ({user_id})"
                    note_details.append(f"{username}: {note}")

                notes_list = "\n".join(note_details)
                await interaction.response.send_message(f"All notes:\n{notes_list}", ephemeral=True)
            else:
                await interaction.response.send_message("No notes found.", ephemeral=True)
        else:
            await interaction.response.send_message("You do not have the required permissions.", ephemeral=True)

    @app_commands.command(name="clear_db", description="Clear all notes by all users of note-bot.")
    async def clear_all(self, interaction: discord.Interaction):
        if interaction.user.id == ID:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes")
            conn.commit()
            conn.close()
            await interaction.response.send_message("All notes have been cleared.", ephemeral=True)
        else:
            await interaction.response.send_message("You do not have the required permissions.", ephemeral=True)

bot.tree.add_command(Notes(bot).add_note)
bot.tree.add_command(Notes(bot).list_notes)
bot.tree.add_command(Notes(bot).delete_notes)
bot.tree.add_command(Notes(bot).view_all)
bot.tree.add_command(Notes(bot).clear_all)

# Set 'TOKEN' to your bot's token.
# Set 'ID' to the owner's Discord user ID.

TOKEN = "token"
ID = "id"
bot.run(TOKEN)
