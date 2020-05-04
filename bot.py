# bot.py
import os

import discord
from dotenv import load_dotenv
import imap as imap
import asyncio as asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
setup_channel = None
setup_author = None
client = discord.Client()
grab_emails = None
@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break
    

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@client.event
async def on_message(message):


    def check_channel(resp):
        if resp.channel != setup_channel and resp.author != setup_author:
            return False
        else:

            try:
                int(resp.content)
            except ValueError as identifier:
                return False

            for channel in client.get_all_channels():
                if int(resp.content) == channel.id:
                    return True
            return False

    def check_email(resp):
        if resp.channel != setup_channel:
            return False
        else:
            if resp.content.endswith('@gmail.com'):
                return True
        return False

    def check_password(resp):
        return resp.channel == setup_channel

    def check_label(resp):
        return resp.channel == setup_channel


    if message.content.startswith('-yb'): 
        if message.author.guild_permissions.administrator:
            split = message.content.split(" ")
            
            
            if split[1] == "help":

                await message.channel.send('In Progress...')

            elif split[1] == "setup":

                output_channel = None
                os.environ['EMAIL'] = 'NotSet'
                os.environ['PASSWORD'] = 'NotSet'
                os.environ['LABEL'] = 'NotSet'

                setup_channel = message.channel
                setup_author = message.author
                
                
                #setup channel
                setup_message = await setup_instructions(setup_channel, 1)
                response = await client.wait_for('message', check=check_channel, timeout=60.0)
                os.environ['CHANNEL'] = response.content
                await response.delete()
                await setup_message.delete()
                
                #setup email
                setup_message = await setup_instructions(setup_channel, 2)
                response = await client.wait_for('message', check=check_email, timeout=60.0)
                os.environ['EMAIL'] = response.content
                await response.delete()
                await setup_message.delete()
                
                #setup password
                setup_message = await setup_instructions(setup_channel, 3)
                response = await client.wait_for('message', check=check_password, timeout=60.0)
                os.environ['PASSWORD'] = response.content
                await response.delete()
                await setup_message.delete()

                #setup label
                setup_message = await setup_instructions(setup_channel, 4)
                response = await client.wait_for('message', check=check_label, timeout=60.0)
                os.environ['LABEL'] = response.content
                await response.delete()
                await setup_message.delete()

                setup_author = None
                setup_channel = None

            elif split[1] == 'setchannel':

                setup_channel = message.channel
                setup_author = message.author
                
                setup_message = await setup_instructions(setup_channel, 1)
                response = await client.wait_for('message', check=check_channel, timeout=60.0)
                os.environ['CHANNEL'] = response.content

                await setup_message.delete()
                await response.delete()
                setup_author = None
                setup_channel = None

            elif split[1] == 'setemail':

                setup_channel = message.channel
                setup_author = message.author
                
                setup_message = await setup_instructions(setup_channel, 2)
                response = await client.wait_for('message', check=check_email, timeout=60.0)
                os.environ['EMAIL'] = response.content

                await setup_message.delete()
                await response.delete()
                setup_author = None
                setup_channel = None

            elif split[1] == 'setpassword':

                setup_channel = message.channel
                setup_author = message.author

                setup_message = await setup_instructions(setup_channel, 3)
                response = await client.wait_for('message', check=check_password, timeout=60.0)
                os.environ['PASSWORD'] = response.content

                await setup_message.delete()
                await response.delete()
                setup_author = None
                setup_channel = None

            elif split[1] == 'setlabel':

                setup_channel = message.channel
                setup_author = message.author

                setup_message = await setup_instructions(setup_channel, 4)
                response = await client.wait_for('message', check=check_label, timeout=60.0)
                os.environ['LABEL'] = response.content

                await setup_message.delete()
                await response.delete()
                setup_author = None
                setup_channel = None

            elif split[1] == 'checkconnection':
                
                imap.check_connection()

            elif split[1] == 'connect':
                if os.getenv('CHANNEL') == None:
                    await message.channel.send("Must connect a channel")
                    return
                global grab_emails
                grab_emails = asyncio.create_task(connect())
                await message.channel.send("connected")
            
            elif split[1] == 'disconnect':
               
                for task in asyncio.all_tasks():
                    if task != asyncio.current_task and task == grab_emails:
                        task.cancel()
                        await message.channel.send("disconnected")
            else:
                await message.channel.send("That's not a command! Do -yb help for a list of commands.")
            await message.delete()
    
            
async def connect():
    
    await client.wait_until_ready()
    while True:
        await asyncio.sleep(600)
        emails = imap.connect()
        bodies = emails['bodies']
        for body in bodies:
            await client.get_channel(int(os.getenv('CHANNEL'))).send(body)

        


async def setup_instructions(channel, step):
    if step == 1:
        embed = discord.Embed(title="Enter the ID for an output channel.", description="This is the channel that will send the emails in a Discord message.", color=0x00ff00)
        return await channel.send(embed=embed)
    elif step == 2:
        embed = discord.Embed(title="Enter an email account.", description="This must be a gmail account and you must allow IMAPing.", color=0x00ff00)
        return await channel.send(embed=embed)
    elif step == 3:
        embed = discord.Embed(title="Enter the password the email account.", description="We must have this to be able to read the emails. Duh.", color=0x00ff00)
        return await channel.send(embed=embed)
    elif step == 4:
        embed = discord.Embed(title="Enter the label.", description="This is the label that contains the emails to be sent to the Discord channel.", color=0x00ff00)
        return await channel.send(embed=embed)




client.run(TOKEN)