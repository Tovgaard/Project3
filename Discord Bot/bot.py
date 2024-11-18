import discord
from discord.ext import commands

TOKEN = 'MTE2NDU1NTMzMTIwNTA3NTA0NQ.GBsPvY.OQ1HVmvS552RCpAs8fLm1jDNP7aSATZMG6NMvk'
channel_id = 1164638908248764427
tech_help_channel_id = 1164600607269732433
prefix = '!'

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.dm_messages = True

bot = commands.Bot(command_prefix=prefix, intents=intents)

help_message_sent = False  # Variabel for at spore, om hjælpebeskeden allerede er blevet sendt
help_requests = []  # En liste til at spore hjælpeanmodninger

@bot.event
async def on_ready():
    print(f'Bot is ready as {bot.user.name}')
    tech_help_channel = bot.get_channel(tech_help_channel_id)
    await tech_help_channel.send(f"I'm now live!")
    global help_message_sent
    if not help_message_sent:
        await create_fixed_message()
        help_message_sent = True

async def create_fixed_message():
    channel = bot.get_channel(channel_id)

    if not channel:
        print("Cannot find channel.")
        return

    async for message in channel.history(limit=200):
        if message.content == "If you need help, type `!table [number]`. For example, `!table 5`.":
            print("Besked er skrevet")
            return  # Hvis beskeden allerede findes, afslut funktionen

    await channel.send("If you need help, type `!table [number]`. For example, `!table 5`.")


@bot.command(aliases=["Table"])
async def table(ctx, number: int):
    user = ctx.message.author
    tech_help_channel = bot.get_channel(tech_help_channel_id)

    if tech_help_channel:
        # Check if the user is already in the queue
        for index, request in enumerate(help_requests):
            if request["user"] == user:
                await user.send(f'{user.mention}, you are already in the help queue for table {request["table"]}. Your position in the queue is #{index + 1}.')
                return

        if 1 <= number <= 20:
            # Send message and save message ID
            message = await tech_help_channel.send(f'{user.mention} needs help at table {number} in Stream Studio and there is {len(help_requests)} in queue')
            message_id = message.id

            # Add user's request to the help requests list with message ID
            help_requests.append({"user": user, "table": number, "message_id": message_id})
            await user.send(f"You are now in queue for help. We will be with you soon. You are #{len(help_requests)} in queue. If you encounter a specific issue, please inform us here, and we will dispatch the appropriate person to assist you")
        else:
            await user.send("Invalid use of !table. Please choose a number between 1 and 20.")
    else:
        await ctx.send("Cannot find the tech-help channel.")

        
@bot.command()
async def done(ctx, number: int):
    if ctx.author == bot.user:
        return
    
    else:
        if ctx.channel.id == tech_help_channel_id:
            # Find og fjern brugerens anmodning fra hjælpeanmodningslisten
            for request in help_requests:
                if request["table"] == number:
                    user_to_notify = request["user"]
                    help_requests.remove(request)

                    if len(help_requests) > 0:
                        next_request = help_requests[0]
                        await ctx.send(f'Table {number} is marked as done for {user_to_notify.mention}. The next request is for table {next_request["table"]} by {next_request["user"].mention}.')
                    else:
                        await ctx.send(f'Table {number} is marked as done for {user_to_notify.mention}. The help queue is currently empty.')
                    return

            await ctx.send(f'No active request found for table {number}.')


@bot.event
async def on_message(message):
    ask_for_help_channel = channel_id
    if message.author == bot.user:
            return  # Ignorer beskeder fra botten selv
    if message.channel.id == ask_for_help_channel:
        print(f"Jeg har modtaget besked")
        if "!table" not in message.content and "!Table" not in message.content:
            # Hvis beskeden ikke indeholder !table, send en privat besked
            print("Beskeden indholde ikke !table så jeg skrev en privatbesked til dem")
            await message.author.send("In this chat you can only use !table and a number between 1 and 20 ")
        await message.delete()
    await bot.process_commands(message)
    
    # Check if the message is in a DM channel
    if isinstance(message.channel, discord.DMChannel):
        user = message.author

        # Find the user's request in the list based on the user's name
        for request in help_requests:
            if request["user"] == user:
                # Find the message ID and add the reply to the existing message
                message_id = request["message_id"]
                tech_help_channel = bot.get_channel(tech_help_channel_id)
                original_message = await tech_help_channel.fetch_message(message_id)

                # Add the reply to the existing message
                await original_message.edit(content=f'{original_message.content} and they need help with {message.content}')
                return
        # If the user is not in the queue
        try:
            await user.send("You are not currently in the help queue. Use !table to join the queue.")
        except discord.errors.HTTPException as e:
            # Handle exception if the bot cannot send a message to the user
            print(f"Failed to send message to {user}: {e}")

bot.run(TOKEN)