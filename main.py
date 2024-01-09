import asyncio
import json
import os
import random
from threading import Thread
import discord
from discord.ext import commands

component = discord.components.Component()
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix='/', intents=intents)


# Load user data from the JSON file
def load_user_data():
    if os.path.exists('user_data.json'):
        with open('user_data.json', 'r') as file:
            return json.load(file)
    else:
        return {}

# Save user data to the JSON file
def save_user_data():
    with open('user_data.json', 'w') as file:
        json.dump(user_data, file)

user_data = load_user_data()

# Dictionary to map level milestones to role IDs and perks
level_roles = {
    0: {"role_id": 1067823974228168728, "perks": []},  # No perks for level 0
    5: {"role_id": 1193505438021468190, "perks": ["Create discussions in the discussion hall", "#chat-2"]},
    10: {"role_id": 1193505892134555729, "perks": ["Add reactions"]},
    15: {"role_id": 1193506040755519518, "perks": ["No perks"]},
    20: {"role_id": 1193506297053573120, "perks": ["#chat-3"]},
    25: {"role_id": 1193506544462089226, "perks": ["Send Images in #chat"]},
    30: {"role_id": 1193506804764790814, "perks": ["No perks"]},
    35: {"role_id": 1193507009975304203, "perks": ["No perks"]},
    40: {"role_id": 1193507225830969345, "perks": ["No perks"]},
    45: {"role_id": 1193507509525286963, "perks": ["No perks"]},
    50: {"role_id": 1193507829596815390, "perks": ["#chat-x"]},
    55: {"role_id": 1193508162301603861, "perks": ["No perks"]},
    60: {"role_id": 1193508350860742656, "perks": ["No perks"]},
    65: {"role_id": 1193508799290548344, "perks": ["No perks"]},
    70: {"role_id": 1193509054379720734, "perks": ["No perks"]},
    75: {"role_id": 1193509451412545608, "perks": ["#chat-99"]},
    80: {"role_id": 1193509839515701309, "perks": ["No perks"]},
    85: {"role_id": 1193510047867744257, "perks": ["No perks"]},
    90: {"role_id": 1193510326537298023, "perks": ["No perks"]},
    95: {"role_id": 1193510562563358731, "perks": ["No perks"]},
    100: {"role_id": 1193511149887553587, "perks": ["You should consider touching grass."]},
}

# Shop items with their prices
shop_items = {
    "✨ XP Boost": {"name": "boost","price": 1000, "description": "Double XP gain for the next 5 messages."},
    "🔰 Wealthy Bandicoot Role": {"name": "role", "price": 100000, "description": "Unlock the special 'Wealthy Bandicoot' role."},
    "🪙 Lucky Coin": {"name": "coin", "price": 10000, "description": "A lucky coin! Double XP gain for the next 75 messages."},
    "🥚 Egg": {"name": "egg", "price": 1000000, "description": "Lay 3 eggs in #chat!"},
    "🗝️ Mystery Key": {"name": "mystery_key", "price": 666666, "description": "A mystery key that unlocks a new horizon!"}
}

mystery_shop_items = {
    "🌈 Embed Customizer": {"name": "embed_customizer", "price": 100000, "description": "Customize your level up embed with this tool! Say /customize to use!"},
    "🌳 Tree": {"name": "tree", "price": 500000, "description": "Plant a tree in the #chat channel! say /tree to use!"},
    "💎 Diamond": {"name": "diamond", "price": 1000000, "description": "A precious diamond! Permanent double XP!"},
    "🕯️ Hidden Candle Role": {"name": "candle_role", "price": 5000000, "description": "Light up the chat with a weird candle!"},
    "🖊️ Spoiler Pen": {"name": "pen", "price": 7500000, "description": "A pen used to write ||spoilers!||"},
    "🧀 Limburger Cheese": {"name": "cheese", "price": 10000000, "description": "This cheese is so stinky, it can mute a user for 1 hour! Say /cheese [user_id] to use!"},
    "📢 Announcement": {"name": "announcement", "price":500000000, "description": "Send any announcement in the #announcements channel! Say /announce [announcement] to use!"},
}

# Channel ID where the level-up messages will be sent
level_up_channel_id = 1193534083930792026  # Replace with the actual channel ID

# Function to send a level-up message
async def level_up_message(channel, user, level, perks):
    default_description = "Congratulations on leveling up!"

    embed_color = user_data.get("hex_color", "#00FF00")  # Default color if not available
    description = user_data.get("description", default_description)

    embed = discord.Embed(
        title=f"🚀 {user.name} has leveled up to level {level}!",
        description=description or default_description,
        color=int(embed_color, 16)  # Convert hex color to decimal
    )

    embed.set_thumbnail(url=user.avatar.url)

    if perks:
        embed.add_field(name="Perks Unlocked", value="/n * ".join(perks), inline=False)

    await channel.send(embed=embed)




# Command to handle messages
@bot.event
async def on_message(message):
    # Ignore messages from the bot itself to prevent infinite loops
    if message.author == bot.user:
        return

    # Get the user ID as a string
    user_id_str = str(message.author.id)

    # Check if the user is in the user_data dictionary, if not, add them
    if user_id_str not in user_data:
        user_data[user_id_str] = {"xp": 0, "level": 1, "max_xp": 100, "total_messages": 0, "credits": 0, "items": [], "xp_multiplier": 1, "double_xp_messages": 0, "hex_color": "#00FF00", "description": ""}

    # Give XP, credits, and check for level up
    user_data[user_id_str]["xp"] += (5 + round(len(message.content) / 10)) * user_data[user_id_str]["xp_multiplier"] * (user_data[user_id_str]["double_xp_messages"] > 0 * 2)
    user_data[user_id_str]["total_messages"] += 1
    user_data[user_id_str]["double_xp_messages"] -= 1 if not user_data[user_id_str]['double_xp_messages'] == 0 else 0
    user_data[user_id_str]["credits"] += 1 + round(len(message.content) / 3)

    while user_data[user_id_str]["level"] > 0 and user_data[user_id_str]["xp"] >= user_data[user_id_str]["max_xp"]:
        user_data[user_id_str]["level"] += 1
        user_data[user_id_str]["xp"] -= user_data[user_id_str]["max_xp"]
        user_data[user_id_str]["max_xp"] = round(int(user_data[user_id_str]["max_xp"] * 1.1) + user_data[user_id_str]["total_messages"])
        user_data[user_id_str]['credits'] += user_data[user_id_str]['level'] * user_data[user_id_str]['total_messages'] / user_data[user_id_str][level] * 1.2

        channel = bot.get_channel(level_up_channel_id)

        if user_id_str in user_data and 'level' in user_data[user_id_str]:
            await level_up_message(channel, message.author, user_data[user_id_str]['level'], level_roles.get(user_data[user_id_str]['level'], {}).get("perks", []))
            if user_id_str in user_data and 'level' in user_data[user_id_str] and user_data[user_id_str]['level'] in level_roles:
                role_id = level_roles[user_data[user_id_str]['level']]["role_id"]
                if role_id:
                    role = discord.utils.get(message.guild.roles, id=role_id)
                    if role:
                        await message.author.add_roles(role)

    # Save user data to the JSON file
    save_user_data()

    # Continue processing other commands and events
    await bot.process_commands(message)

tips = ["Chat more to gain lots of XP!", "Use /shop to buy items!", "Buy items from /shop to gain more XP!", "Hype up the chat with chat events to gain more popularity!"]

# Event to handle member join
@bot.event
async def on_member_join(member):
    # Get the user ID as a string
    user_id_str = str(member.id)

    # Assign the level 0 role to the new member
    role = discord.utils.get(member.guild.roles, id=1067823974228168728)
    if role:
        await member.add_roles(role)
        user_data[user_id_str] = {"xp": 0, "level": 1, "max_xp": 100, "total_messages": 0, "credits": 0, "items": [], "xp_multiplier": 1, "double_xp_messages": 0, "hex_color": "#00FF00", "description": ""}

    # Save user data to the JSON file
    save_user_data()

# Command to handle level view
@bot.command(name='level')
async def view_level(ctx, member=None):
    member = member or ctx.author
    user_id = str(member.id)

    # Load user data from the JSON file
    user_data[user_id] = {"xp": 0, "level": 1, "max_xp": 100, "total_messages": 0, "credits": 0, "items": [], "xp_multiplier": 1, "double_xp_messages": 0, "hex_color": "#00FF00", "description": ""}

    embed_color = user_data.get("hex_color", "#00FF00")  # Default color if not available
    description = user_data.get("description", None)
    items = user_data.get("items", [])

    embed = discord.Embed(
        title=f"📊 {member.mention}'s Level Information",
        description=random.choice(tips),
        color=int(embed_color, 16)  # Convert hex color to decimal
    )
    embed.set_thumbnail(url=member.avatar.url)

    embed.add_field(name="Statistics", value=f"""
    **Level** {user_data["level"]}
    **XP** {user_data["xp"]}/{user_data["max_xp"]}
    **Credits** {user_data["credits"]}
    """, inline=True)

    if items:
        embed.add_field(name="Inventory", value=", ".join(items), inline=False)

    if description:
        embed.description = description

    await ctx.send(embed=embed)

@bot.command(name='egg')
async def egg_command(ctx):
    user_id = str(ctx.author.id)
    guild = ctx.guild
    channel = guild.get_channel(name='chat')
    
    if 'egg' in user_data[user_id]['items']:
        user_data[user_id]['items'].remove('egg')
        await channel.send("egg", file=discord.File("data:image/jpeg;base64,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"))
    else:
        await ctx.send("You don't have an egg.")
@commands.group(name='shop', invoke_without_command=True)
async def shop(ctx):
    await ctx.send("Use /shop regular to view the Regular Shop or /shop mystery to view the Mystery Shop.")

# Function to handle item purchase for a specific user
async def handle_item_purchase(ctx, item_name, user_data):
    str(ctx.author.id)

    shop_item = shop_items.get(item_name) or mystery_shop_items.get(item_name)

    if not shop_item:
        await ctx.send("Invalid item. Use `/shop` to see available items.")
        return

    price = shop_item["price"]

    if user_data["credits"] < price:
        await ctx.send(f"You don't have enough credits to buy {item_name}.")
        return

    # Check if the user has the Mystery Key to purchase items from the Mystery Shop
    if item_name in mystery_shop_items and "Mystery Key" not in user_data.get("items", []):
        await ctx.send("You need the Mystery Key to purchase items from the Mystery Shop.")
        return

    # Deduct the price from the user's credits
    user_data["credits"] -= price

    # Add the purchased item to the user's "items" list
    user_data.setdefault("items", []).append(item_name)

    # Check if the purchased item grants a role
    if "role" in shop_item:
        role_name = shop_item["role"]
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            await ctx.author.add_roles(role)
            await ctx.send(f"You have successfully bought {item_name} and received the {role_name} role!")

    await ctx.send(f"You have successfully bought {item_name}!")


# Command to handle item purchase
@shop.command(name='buy')
async def handle_item_purchase_command(ctx, item_name):
    user_id = str(ctx.author.id)

    # Load user data from the JSON file
    user_data = load_user_data().get(user_id, {"credits": 0, "items": []})

    # Handle item purchase
    await handle_item_purchase(ctx, item_name, user_data)

    # Save user data to the JSON file
    save_user_data()

# Command to customize embed
@bot.command(name='customize')
async def customize_embed(ctx):
    user_id = str(ctx.author.id)

    # Load user data from the JSON file
    user_data = load_user_data().get(user_id, ("hex_color", "description"))

    # Ask the user to provide customization details
    await ctx.send("Please provide a hex color for the level up embed. You have 60 seconds to respond.")

    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel

    try:
        hex_color_message = await bot.wait_for('message', check=check, timeout=60)
        hex_color = hex_color_message.content
    except TimeoutError:
        await ctx.send("Customization process timed out. Please try again.")
        return

    await ctx.send("Please provide a description for the level up embed. You have 60 seconds.")

    try:
        description_message = await bot.wait_for('message', check=check, timeout=60)
        description = description_message.content
    except TimeoutError:
        await ctx.send("Customization process timed out. Please try again.")
        return

    # Update user data with customization details
    user_data[user_id]['hex_color'] = hex_color
    user_data[user_id]['description'] = description

    # Save user data to the JSON file
    save_user_data()

@shop.command(name='regular')
async def view_regular_shop(ctx):
    embed = discord.Embed(
        title="🏪 Big Supermarket",
        color=0xe6e200  # Change color as desired
    )

    for item_name, item_info in shop_items.items():
        embed.add_field(name=item_name, value=f"Price: {item_info['price']} credits\nDescription: {item_info['description']}", inline=True)
        embed.add_field(name=":arrow_up:", value=f"To buy this, say /shop buy {item_info['name']} and you'll buy it!", inline=True)
    await ctx.send(embed=embed)

@shop.command(name='mystery')
async def view_mystery_shop(ctx):
    embed = discord.Embed(
        title="🗝️ Mystery Shop",
        description="Congratulations! You've unlocked the mystery shop! Now gander at these **expensive** items.",
        color=0x6a3d7d  # Change color as desired
    )

    for item_name, item_info in mystery_shop_items.items():
        embed.add_field(name=item_name, value=f"Price: {item_info['price']} credits\nDescription: {item_info['description']}", inline=True)
        embed.add_field(name=":arrow_up:", value=f"To buy this, say /shop buy {item_info['name']} and you'll buy it!", inline=True)

    await ctx.send(embed=embed)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


async def update_status():
    while True:
        latency_ms = round(bot.latency * 1000)  # Latency in milliseconds
        custom_status = discord.Game(name=f'Latency: {latency_ms}ms')
        await bot.change_presence(activity=custom_status)
        await asyncio.sleep(10)  # Sleep for 10 seconds before updating again

            # Function to handle cheese for a specific user
# Function to handle cheese for a specific user
async def handle_cheese(ctx, selected_user):
    # Assign the Muted role to the selected user
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")  # Replace with your muted role name
    if muted_role:
        await selected_user.add_roles(muted_role)
        await ctx.send(f"{selected_user.mention} has been muted with Limburger Cheese!")

        # Schedule the removal of the Muted role after 1 hour
        await asyncio.sleep(3600)  # 3600 seconds = 1 hour

        # Remove the Muted role from the selected user
        await selected_user.remove_roles(muted_role)
        await ctx.send(f"{selected_user.mention}'s mute with Limburger Cheese has expired.")
    else:
        await ctx.send("Muted role not found. Please set up a Muted role with the correct permissions.")

    # Remove the Limburger Cheese item from the user's inventory
    user_id = str(ctx.author.id)
    if user_id in user_data and 'items' in user_data[user_id]:
        user_data[user_id]['items'].remove('cheese')
        save_user_data()

# Command to use the cheese item on a specific user
@bot.command(name='cheese')
async def cheese_command(ctx, user_id: int):
    user_id_str = str(ctx.author.id)

    if user_id_str not in user_data:
        await ctx.send("You are not in the user database. Please start chatting to be able to use items.")
        return

    # Check if the user has the "cheese" item in their inventory
    if 'cheese' not in user_data[user_id_str].get("items", []):
        await ctx.send("You don't have the Limburger Cheese item.")
        return

    # Check if the selected user is in the server
    selected_user = ctx.guild.get_member(user_id)
    if not selected_user:
        await ctx.send("User not found in the server.")
        return

    # Create a thread to handle cheese for the selected user
    thread = asyncio.create_task(handle_cheese(ctx, selected_user))
    await thread




# Command to plant a tree
@bot.command(name='tree')
async def plant_tree(ctx):
    user_id_str = str(ctx.author.id)

    if user_id_str not in user_data:
        await ctx.send("You are not in the user database. Please start chatting to be able to use items.")
        return

    # Check if the user has a "tree" item in their inventory
    if 'tree' not in user_data[user_id_str].get("items", []):
        await ctx.send("You don't have a tree item to plant.")
        return

    # Remove one "tree" item from the user's inventory
    user_data[user_id_str]["items"].remove("tree")

    # Send an image of a tree in the "chat" channel
    channel = discord.utils.get(ctx.guild.channels, name='chat')  # Replace with the actual channel name
    if channel:
        tree_image_url = "https://img.freepik.com/free-vector/tree-transparent-background_1308-74201.jpg"  # Replace with the actual URL of the tree image
        await channel.send(f"{ctx.author.mention} has planted a tree!", file=discord.File(tree_image_url))

        # Save user data to the JSON file
        save_user_data()
    else:
        await ctx.send("Error finding the 'chat' channel. Please contact the server administrator.")







def run():
    bot.run(os.environ['BOT_TOKEN'])

t = Thread(target=run)
t2 = Thread(target=update_status)

t.start()
t2.start()

t.join()
t2.join()
