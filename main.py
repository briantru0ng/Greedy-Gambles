# Lead Coder: Brian Truong
from asyncio import constants
from distutils.log import error
from email import message
from multiprocessing.connection import Client

import asyncio
from operator import truediv
from unicodedata import name
import discord
from discord.ext import commands
import os

from matplotlib.style import context, use

from pymongo import MongoClient
import pymongo
from pyparsing import line


intents = discord.Intents.default()

lines=[]
with open("C:/Users/Brian/OneDrive/Documents/GitHub/Discord-Bots/Jepordary/important-info.txt") as skim:
    lines= skim.readlines()
token=lines[0]
client = discord.Client(intents=intents)
timeallowedAttempt=5.0
timeallowedAnswer=20.0
contestants_clean=[]


def configureDB():
    client=MongoClient(lines[1])
    return client.get_database("GreedyGambles")
    
db = configureDB()
db_collection=db["scoreboard"]
original_sb=[
    [":green_square:", ":green_square:", ":green_square:", ":green_square:", ":green_square:"],
    [":green_square:", ":green_square:", ":green_square:", ":green_square:", ":green_square:"],
    [":green_square:", ":green_square:", ":green_square:", ":green_square:", ":green_square:"],
    [":green_square:", ":green_square:", ":green_square:", ":green_square:", ":green_square:"],
    [":green_square:", ":green_square:", ":green_square:", ":green_square:", ":green_square:"],
]
sb=original_sb
@client.event
async def on_ready():
    print(f'We have logged in as {client.user.name}')

def is_me(message):
    try:
        if 'Game Master' in str(message.author.roles) or message.author.bot==True:
            return True
    except IndexError:
        pass
    return False
    

def find_username(line):
    listify=list(line)
    pointindex=line.rindex(' ')
    userindex=listify.index('@')+1
    username=listify[userindex:userindex+18]
    username=''.join(username)

    points=listify[pointindex:]
    points=''.join(points)
    return username, points
    

@client.event
async def on_message(message):
    global timeallowedAttempt, contestants_clean, db_collection, client, timeallowedAnswer, original_sb, sb
    ctx=message.channel
    is_GM= is_me(message)
    # Anyone can use these commands
    #makes a list of commands some plebs can use
    if '$help' in message.content.lower():
        await ctx.send("Here are some commands you plebs can use whenever. Commands are preceded by a '$':\nlb: See the current rankings of an active game\nego: Boost Brian's ego by liking his instagram post:)\nsup: Support the game show by giving Brian some money for the prizes")
        return

    #makes a leaderboard to see who's on top
    if '$lb' in message.content.lower():
        finalStr=("SCOREBOARD: \n------------------------------------------\n")
        placement=1
        for leaderboard in db_collection.find().sort("score",-1):
            if placement==1:
                lineplacement='1st'
            elif placement == 2:
                lineplacement='2nd'
            elif placement==3:
                lineplacement='3rd'
            else:
                lineplacement=str(placement)+'th'
            
            print(leaderboard)
            finalStr+=("{} is at {} place with {} points.\n".format(leaderboard['user_mention'], lineplacement, leaderboard['score']))
            placement+=1
        finalStr+="------------------------------------------"
        await ctx.send(finalStr)
        return

    if '$gb' in message.content.lower():
        contents=message.content.split(" ")
        get=['fucked']
        try:
            if is_GM==False:
                lol=get[1]
            if contents[1].lower()== "reset":
                sb=original_sb
                await ctx.send("I reset the game board")
                return
            row=int(contents[2])-1
            column=int(contents[3])-1
            if row>4 or row<0 or column>4 or column<0:
                return await ctx.send("Out of range ||can you not count?!||")
        except IndexError:
            await ctx.send("Current game board")
            colstr=''
            for colvalue in range (5): # prints out the gameboard
                rowstr=''
                for rowvalue in range (5):
                    rowstr+=sb[colvalue][rowvalue]
                colstr+=rowstr+'\n'
            await ctx.send(colstr)
            return
        except AttributeError:
            await ctx.send("Invalid type ||cmon man||")
            return
        # replaces the tile with either a red or green square 
        if contents[1].lower()=="r":
            sb[row][column]=":red_square:"
        elif contents[1].lower()=="g":
            sb[row][column]=":green_square:"

        colstr=''   #prints out the game board
        for colvalue in range (5):
            rowstr=''
            for rowvalue in range (5):
                rowstr+=sb[colvalue][rowvalue]
            colstr+=rowstr+'\n'
        await ctx.send(colstr)
        return

    if '$ego' in message.content.lower():
        await ctx.send("ahahahaha :hot_face: like my post if ur hot and sexy and smart :) \nhttps://www.instagram.com/briantru0ng/ ")
        return
    
    if '$sup' in message.content.lower():
        await ctx.send("support my dumbass by venmo-ing money. bigger prize pool= bigger stakes and bigger suprises")
        return
    
    # Only the Game Master can use these commands
    if is_GM ==True:
        # creates the database and inputs how many users are playing
        if '$create' in message.content.lower():
            contents=message.content.split(" ")
            
            try:
                countdown=int(contents[1])
                beginprobe= await ctx.send('Do you want to play Greedy Gamble$?')
                await beginprobe.add_reaction('💸')
                
                await ctx.send(f"You have {countdown} seconds to react to 💸 if you want to play")

            except ValueError:
                await ctx.send("Invalid input")

            except IndexError:
                await ctx.send("Create what now bitch? You're not even letting the players get the chance to play with fucking 0 time!")

            await asyncio.sleep(countdown) # waits for the people who want to join join

            
            cache_msg = await ctx.fetch_message(beginprobe.id)
            contestants_messy=[]
            for reaction in cache_msg.reactions:
                async for user in reaction.users():
                
                    try:
                        goodies=[] # contains a list of the user's name and string to tag them
                        player=await ctx.send(user.display_name+" has joined")
                        goodies.append(player.content) #dirty message containing the username
                        goodies.append(user.mention) #tag
                        print (user.mention)
                        contestants_messy.append(goodies)

                    except AttributeError:
                        pass
            endprobe=await ctx.send("\nWindow to join has closed. It's game time!\n")
            await beginprobe.add_reaction('❌') # put down here to not distract the program from recognizing another reaction

            await endprobe.add_reaction('✨')

            contestants_clean=contestants_messy[1:] # gets rid of the bot's reaction since the bot cannot play+ takes advantage of the fact that the reactions list goes from first to last claimed
            for player in contestants_clean: # puts in the user's data into the db
                details=player[0].split(' ') # grabs the dirty username
                finalplayer=' '.join(details[:-2]) #  cleans it up
                await ctx.send("Attempting to put "+finalplayer+" in the database.")
                playerinfo={ #creates the item to populate the db
                    "_id":finalplayer,
                    "score":0,
                    "user_mention":player[1]
                }
                try: #attempt to input into the mongodb db
                    db_collection.insert_one(playerinfo)
                    await ctx.send(finalplayer+" is in the database.\n")
                except pymongo.errors.DuplicateKeyError:
                    await ctx.send(finalplayer+" is already in the database\n")
            return
        
        # allows the chance to answer a question
        if '$q' in message.content.lower():
            # creates the opening interactable
            qualifier="Interact with ':tada:' to answer this question!!"
            new_mes= await ctx.send(qualifier)
            await new_mes.add_reaction('🎉')

            def check(reaction, user):
                return str(reaction.emoji) == '🎉' and user != client.user

            try: # checks to see who was the first one to react so they get the chance to answer
                reaction, user = await client.wait_for('reaction_add', timeout=timeallowedAttempt, check=check)
                didanswer=await ctx.send(f"{user.display_name} got it. You have {timeallowedAnswer} seconds to answer")
                await asyncio.sleep(timeallowedAnswer)
                try: # see if the player can answer the question
                    didanswer.reactions[1]
                except IndexError:
                    await didanswer.add_reaction('❌')
                    await ctx.send("Time's up! You didn't answer.")
            
            except asyncio.TimeoutError: # no one could answer the question
                await new_mes.add_reaction('❌')
                await ctx.send(f"Time's up! {timeallowedAttempt} seconds have passed and no one got it.")
            return
    
        # change the time to attempt a question
        if '$tcat' in message.content.lower():
            
            contents=message.content.split(" ")
            
            try:
                timeallowedAttempt=float(contents[1])
                await ctx.send(f"Question countdowns now last {timeallowedAttempt} seconds")

            except ValueError:
                await ctx.send("Invalid input")
            return

        # change the time to attempt a question
        if '$tcan' in message.content.lower():
            
            contents=message.content.split(" ")
            
            try:
                timeallowedAnswer=float(contents[1])
                await ctx.send(f"The time to answer a question now takes {timeallowedAnswer} seconds")

            except ValueError:
                await ctx.send("Invalid input")
            return
        
        # gives a player x amount of points to the db
        if '$give' in message.content.lower():
            message_content=message.content
            # attempt to find the player and the points based on the given line
            username, points= find_username(message_content)
            try:
                user_id=int(username)
                points=int(points)
            except ValueError:
                return await ctx.send("Invalid value to edit with")

            # gets username from user id
            username=await client.fetch_user(user_id)

            db_collection.update_one({'_id':str(username.name)}, {'$inc': {'score':points}}) # updates the mongodb db
            cell=list(db_collection.find({"_id": str(username.name)}))
            # print (cell)
            try:
                await ctx.send(f"Congrats on winning {points} points <@{user_id}>! (Score: {cell[0]['score']})")
            except IndexError:
                await ctx.send(f"I must be on something because <@{user_id}> isn't even in the game!")
            return

        # removes a player x amount of points from the db
        if '$yoink' in message.content.lower():
            message_content=message.content
            # attempt to find the player and the points based on the given line
            username, points= find_username(message_content)
            try:
                user_id=int(username)
                points=int(points)
            except ValueError:
                return await ctx.send("Invalid value to edit with")
            # gets username from user id
            username=await client.fetch_user(user_id)

            db_collection.update_one({'_id':str(username.name)}, {'$inc': {'score':-1*points}})
            cell=list(db_collection.find({"_id": str(username.name)}))
            print (cell)
            try:
                await ctx.send(f"Congrats on losing {points} points <@{user_id}>! _how cringe!_ (Score: {cell[0]['score']})")
            except IndexError:
                await ctx.send(f"I must be on something because <@{user_id}> isn't even in the game!")
            return

        # wipes the items from the collection
        if '$wipe' in message.content.lower():
            await ctx.send("Check VSCode to confirm")
            qualifier=input ("are you sure to wipe the items? ")
            
            if qualifier=="Y":
                db_collection.delete_many({})
                await ctx.send("I've wiped everything from the database!")
            else:
                await ctx.send("Could not wipe from database")
            
            return

        # gives another player a chance to answer if a previous player can't answer
        if '$chance' in message.content.lower():
            didanswer=await ctx.send(f"You have {timeallowedAnswer} seconds to answer")
            await asyncio.sleep(timeallowedAnswer)
            try: # see if the player can answer the question
                didanswer.reactions[1]
            except IndexError:
                await didanswer.add_reaction('❌')
                await ctx.send("Time's up! You didn't answer.")
            return
    
    elif is_GM==False and '$' in message.content:
        await ctx.send("testing me huh? ||bitch||")
client.run(token)

