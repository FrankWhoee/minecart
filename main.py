import json
import subprocess
import yaml
import discord
import requests
import os
import sys

client = discord.Client()

if os.path.exists("minecart.config"):
    with open('minecart.config', 'r') as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
else:
    print("[WARN] No configuration file found.")
    with open('minecart.config', 'w') as file:
        config = {
            "memory": 1024,
            "channel": -1,
            "token": "REPLACE_WITH_YOUR_TOKEN"
        }
        yaml.dump(config)
    print("[WARN] A new configuration file has been created at minecart.config.")
    print("[WARN] Default memory is 1024M")

if config["channel"] == -1:
    print("[WARN] No channel found in minecart.config! This bot will not send a startup message to the discord server. If you would like a startup message, please put it in minecart.config under the property channel (ie. channel: 1234)")
if "token" not in config or config["token"] == "REPLACE_WITH_YOUR_TOKEN" or config["token"] == "":
    print("[FATAL] No bot token found! This will happen the first time you run this bot. Please configure a bot token at https://discord.com/developers and put it in minecart.config under the property token (ie. token: abcd)")
    quit()

memory = config["memory"] if "memory" in config else 1024


@client.event
async def on_ready():
    p = subprocess.Popen("exec java -Xmx"+str(memory)+"M -Xms"+str(memory)+"M -jar server.jar nogui", stdout=subprocess.PIPE, shell=True)

    channel = client.get_channel(config["channel"])
    startup_text = """
                    Server is online!\nPublic URL: {}
                    """.format(createNgrok())
    await channel.send(startup_text)
    print('We have logged in as {0.user}'.format(client))

def createNgrok():
    try:
        response = json.loads(requests.get('http://localhost:4040/api/tunnels').text)
        pub_url = response['tunnels'][0]['public_url']
    except:
        p = subprocess.Popen("exec " + "~/ngrok tcp 25565", stdout=subprocess.PIPE, shell=True)
        while (True):
            try:
                response = json.loads(requests.get('http://localhost:4040/api/tunnels').text)
                pub_url = response['tunnels'][0]['public_url']
                break
            except Exception as e:
                print("Attempting ngrok connection again...")
    return pub_url.replace("tcp://","")

@client.event
async def on_message(message):
    if message.author == client.user or ("channel" in config and message.channel.id != config["channel"]):
        return

    if message.content.startswith('!ngrok') or message.content.startswith('!ip'):
        response_text = """
                {0.author.mention}\nPublic URL: {1}
                """.format(message, createNgrok())
        await message.channel.send(response_text)

client.run(config["token"])