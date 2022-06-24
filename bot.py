from gameManager import *

import asyncio
from asyncio import tasks
import discord
from discord.utils import async_all,get
from discord.ext import commands, tasks
import random as random
import datetime

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', description= "Salut ! Je suis GarouBOT, j'ai pour but de créer et gérer une game de Loup Garou !", intents=intents)

ftoken=open("GarouBot_TOKEN")
TOKEN=ftoken.read()
ftoken.close()


ROLE_multiple=[1,3]

T = 6

gameManager=GameManager()

@bot.event
async def on_ready():
    print("Ready !")

async def random_attribution(ctx,players,comp,GAME):
    category = await ctx.guild.create_category_channel("Game")
    members=ctx.guild.members
    members.pop(0)
    for member in members:
        await category.set_permissions(member, read_messages=False,send_messages=False)
    
    i=0
    list_player=[]
    channel_plublic_place=await category.create_text_channel("Place Publique") 
    channel_graveyard=await category.create_text_channel("Cimetière") 
    channel_polling=await category.create_text_channel("vote")
    channel_recap=await category.create_text_channel("recap")
    channel_loup=await category.create_text_channel("Loup") #il faut un channel spécial car commun aux loups
    channel_soeur=await category.create_text_channel("Soeurs") #il faut un channel spécial car commun aux soeurs
    while len(comp) != 0:
        rand=random.randint(0,len(comp)-1)
        role=comp.pop(rand)
        mid=players[i].split('@')[1]
        mid=mid[:-1]
        user=await bot.fetch_user(mid)
        member=await ctx.guild.fetch_member(mid)
        await channel_polling.set_permissions(user,read_messages=True,send_messages=False)
        await channel_recap.set_permissions(user,read_messages=True,send_messages=False)
        await member.add_roles(GAME.vivant_role,reason=None)
        if role==0:         #c'est une sorcière
            channel=await category.create_text_channel("Sorcière")
            await channel.send(user.mention+ " tu es Sorcière")
            list_player.append(Joueur(user,Sorcière(channel)))
        elif role == 1:     #c'est un loup
            await channel_loup.send(user.mention+ " tu es loup")
            list_player.append(Joueur(user,Loup(channel_loup)))
        elif role == 2:     #c'est le chasseur
            channel=await category.create_text_channel("Chasseur")
            await channel.send(user.mention+ " tu es Chasseur")
            list_player.append(Joueur(user,Chasseur(channel)))        
        elif role == 3:     #c'est Villageois
            channel=await category.create_text_channel("Villageois")
            await channel.send(user.mention+ " tu es Villageois")
            list_player.append(Joueur(user,Villageois(channel)))
        elif role == 4:     #c'est Petite fille
            channel=await category.create_text_channel("Petite fille")
            await channel.send(user.mention+", tu peux écouter les loups en tapant ```!ecoute```\n Mais attention tu ne sais pas quel est le loup qui parle")
            list_player.append(Joueur(user,Petite_fille(channel)))
        elif role == 5:     #c'est voyante
            channel=await category.create_text_channel("Voyante")
            await channel.send(user.mention+ " tu es Voyante")
            list_player.append(Joueur(user,Voyante(channel)))
        elif role == 6:     #c'est cupidon
            channel=await category.create_text_channel("Cupidon")
            list_player.append(Joueur(user,Cupidon(channel)))
        elif role == 7:     #c'est une soeur
            list_player.append(Joueur(user,Soeur(channel_soeur)))
        elif role == 8:     #c'est le salvateur
            channel=await category.create_text_channel("Salvateur")
            list_player.append(Joueur(user,Salvateur(channel)))
        i+=1
    GAME.initialize(category,channel_plublic_place,channel_graveyard,channel_polling,channel_recap,list_player)

@bot.command(pass_context = True)
async def test_lancer(ctx, *texte):

    ##
    if (gameManager.findGame(ctx,State.RUNNING) != None):
        #Une partie est déja en cours sur ce serveur
        await ctx.send("Une partie est deja en cours sur ce serveur")
    GAME=gameManager.findGame(ctx,State.UNUSED)
    if GAME==None:
        GAME=gameManager.newGame(ctx)
    ##
    
    ok = False
    for r in ctx.message.author.roles:
        if r == GAME.MDJ :
            ok=True
    if ok == False:
        await ctx.send(" tu n'as pas les droits de lancer une partie\n")
        return()
    
    if GAME.MDJ == None or GAME.vivant_role == None or GAME.mort_role == None or GAME.spectateur == None:
        await ctx.send("Les roles MDJ/Vivant/Mort/Spectateur ne sont pas crée")
        return
    
    if GAME.is_started():
        await ctx.send("Une partie est déjà en cours ou se crée")
        return()
    if len(texte)==0:
        await ctx.send("Vous ne pouvez pas créer une partie avec zero joueur")
        return
    GAME.start()
    emo=['🧙‍♀️', '🐺', '🔫', '🧑‍🌾', '👧', '🔮', '💘','👭','🛡️']
    role=["Sorcière","Loup","Chasseur","Villageois","Petite fille", "Voyante", "Cupidon", "Soeur (compte pour deux)","Salavateur"]

    message="Salut, tu souhaites lancer une partie, pour cela tu vas devoir choisir la compo parmi:\n"
    for i in range (0,len(emo)):
        message=message+emo[i]+" "+role[i]+"\n"
    message=message+"\nUne fois sûr des rôles que tu veux, utilise l'émote :white_check_mark: pour lancer. Tu peux annuler avec l'émote :x:"
    message = await ctx.send(message)
    for e in emo:
        await message.add_reaction(e)
    await message.add_reaction('✅')
    await message.add_reaction('❌')

    def checkEmoji(reaction,user):
        if ctx.message.author == user and reaction.message.id == message.id and (str(reaction.emoji) == '✅' or str(reaction.emoji) =='❌'):
            return(True)
        return(False)
    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=2*60, check=checkEmoji)
        if reaction.emoji=='❌':
            GAME.finish()
            await ctx.send("La création est annulée ! A la prochaine !! ;)")
            return()
    except:
        await ctx.send("Le temps est dépassé, la création est annulée")
        GAME.finish()
        return()
    # #on va regarder les reactions de l'utilisateur sur le message du bot
    comp=[]
    cache_msg = await ctx.channel.fetch_message(message.id)
    i=-1
    for reactions in cache_msg.reactions:
        i=i+1
        user_list = [user async for user in reactions.users() if user != bot.user]
        for user in user_list:
            if user.id==ctx.author.id and i<len(role):
                comp.append(i)
                if i==7:
                    comp.append(i)

    newcomp=comp.copy()
    for c in comp:
        if c in ROLE_multiple:
            message="Vous voulez rajouter le rôle : "+role[c]+". Combien en voulez-vous ?"
            message = await ctx.send(message)
            await message.add_reaction('1️⃣')
            await message.add_reaction('2️⃣')
            await message.add_reaction('3️⃣')
            await message.add_reaction('4️⃣')
            await message.add_reaction('5️⃣')
            await message.add_reaction('✅')
            await message.add_reaction('❌')
            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=2*60, check=checkEmoji)
                if reaction.emoji=='❌':
                    GAME.finish()
                    await ctx.send("La création est annulée ! A la prochaine !! ;)")
                    return()
            except:
                await ctx.send("Le temps est dépassé, la création est annulée")
                GAME.finish()
                return()
            cache_msg = await ctx.channel.fetch_message(message.id)
            i=-1
            for reactions in cache_msg.reactions:
                i=i+1
                user_list = [user async for user in reactions.users() if user != bot.user]
                
                for user in user_list:
                    if user.id==ctx.author.id and i<5:
                        for j in range(0,i):
                            newcomp.append(c)
                        break

    if len(newcomp) != len(texte):
        await ctx.send("Attention le nombre de joueurs ne correspond pas au nombre de rôles.\n La partie doit être annulée.")
        await ctx.send("Partie annulée ! A plus !")
        GAME.finish()
        return()

    # message="Veux-tu qu'il y ai un maire ?\n"
    # message = await ctx.send(message)
    # await message.add_reaction('✅')
    # await message.add_reaction('❌')
    # def checkEmoji(reaction,user):
    #     if ctx.message.author == user and reaction.message.id == message.id and (str(reaction.emoji) == '✅' or str(reaction.emoji) =='❌'):
    #         return(True)
    #     return(False)
    # try:
    #     reaction, user = await bot.wait_for("reaction_add", timeout=1*60, check=checkEmoji)
    #     if reaction.emoji=='❌':
    #         await ctx.send("Il n'y aura pas de maire !! ;)")
    #         GAME.whitout_mayor()
    # except:
    #     await ctx.send("Le temps est dépassé, il y aura un maire par défaut")

    await random_attribution(ctx,texte,newcomp,GAME) #create channels and adds role
    
    await ctx.send("Partie créée!")
    
    gameManager.runningGame(GAME)
    
    date = datetime.datetime.now()
    h,m,s=18,00,00
    if (date.hour>=h and date.minute>m or (date.minute==m and date.second>s)):
        t=-date.hour*3600-date.minute*60-date.second+h*3600+m*60+s+24*3600
    else:
        t=h*3600-date.hour*3600+(m-date.minute)*60-date.second+s
    await asyncio.sleep(t)
    
    while GAME.is_started():
        if (gameManager.findGame(ctx,State.RUNNING)==None or gameManager.findGame(ctx,State.RUNNING).id!=GAME.id):
            print("erreur, la partie id=", GAME.id," sur le serveur ", GAME.server_id, "ne correspond pas à la partie id=",id)
            return
        if (await nuit(ctx,GAME) == -1):return
        
        date = datetime.datetime.now()
        h,m,s=8,00,00
        if (date.hour>=h and date.minute>m or (date.minute==m and date.second>s)):
            t=-date.hour*3600-date.minute*60-date.second+h*3600+m*60+s+24*3600
        else:
            t=h*3600-date.hour*3600+(m-date.minute)*60-date.second+s
        await asyncio.sleep(t)
        
        if (gameManager.findGame(ctx,State.RUNNING)==None or gameManager.findGame(ctx,State.RUNNING).id!=GAME.id):
            print("erreur, la partie id=", GAME.id," sur le serveur ", GAME.server_id, "ne correspond pas à la partie id=",id)
            return
        if (await jour(ctx,GAME) == -1):return
        
    return

        
async def jour(ctx,GAME):
    await GAME.jour()
    #on tue les morts
    night_death=GAME.night_death
    for death in night_death:
        await death.kill(GAME.channel_public_place,GAME.channel_graveyard,GAME.channel_recap,GAME.vivant_role,GAME.mort_role)
    #si un du couple est mort, on le tue
    await GAME.check_lover()
    #on regarde si le chasseur est mort et qu'il a encore son pouvoir
    players=GAME.players
    for player in players:
        if player.role.name=="Chasseur" and not(player.is_alive()):
            await player.role.action(GAME,bot)

    #on vérifie que la game est pas déja fini
    if await GAME.check_end():
        gameManager.endedGame(GAME)
        return -1

    #maire election si premier round
    await GAME.define_mayor(bot)

    #check si le maire est mort
    await GAME.check_mayor(bot)

    

    #on laisse du temps entre le matin est le vote du soir
    date = datetime.datetime.now()
    h,m,s=18,00,00
    if (date.hour>=h and date.minute>m or (date.minute==m and date.second>s)):
        t=-date.hour*3600-date.minute*60-date.second+h*3600+m*60+s+24*3600
    else:
        t=h*3600-date.hour*3600+(m-date.minute)*60-date.second+s
    await asyncio.sleep(t)
    await ctx.send("Il est "+str(h)+"h"+str(m)+"m"+str(s)+"s !!!!")

    if (gameManager.findGame(ctx,State.RUNNING)==None or gameManager.findGame(ctx,State.RUNNING).id!=GAME.id):
        print("erreur, la partie id=", GAME.id," sur le serveur ", GAME.server_id, "ne correspond pas à la partie id=",id)
        return
    
    #vote
    await GAME.vote(bot)

    #si un du couple est mort, on le tue
    await GAME.check_lover()

    #on regarde si le chasseur est mort et qu'il a encore son pouvoir
    for player in players:
        if player.role.name=="Chasseur" and not(player.is_alive()):
            await player.role.action(GAME,bot)

    #on vérifie que la game est pas déja fini
    if await GAME.check_end():
        gameManager.endedGame(GAME)
        return -1
    #fin du jour
    return 0

async def nuit(ctx,GAME):
    await GAME.nuit()

    #DEBUT CUPIDON
    
    players=GAME.players
    for player in players:
        if player.role.name=="Cupidon" and player.is_alive():
            await player.role.action(player,GAME,bot)
    
    #FIN DE CUPIDON
    

    #DEBUT VOYANTE
    for player in players:
            if player.role.name=="Voyante" and player.is_alive():
                await player.role.action(player,GAME,bot)

    #FIN VOYANTE
    


    #DEBUT LOUP
    await GAME.loups(bot)
    #FIN LOUP

    #DEBUT SALVATEUR
    for player in players:
            if player.role.name=="Salvateur" and player.is_alive():
                await player.role.action(GAME,bot)
    #FIN SALVATEUR

    #DEBUT SORCIERE
    for player in players:
        if player.role.name=="Sorcière" and player.is_alive():
                await player.role.action(GAME,bot)
    #FIN SORCIERE

    #fin de la nuit
    return 0

@bot.command(pass_context = True)
async def clean(ctx):
    GAME = gameManager.findGame(ctx,State.RUNNING)
    if GAME==None:
        GAME = gameManager.findGame(ctx,State.ENDED)
    if GAME==None:
        return
    ok=False
    for r in ctx.message.author.roles:
        if r == GAME.MDJ :
            ok=True
            break
    if ok == False:
        await ctx.send(" tu n'as pas les droits pour cela\n")
        return()
    category=GAME.category
    if category != None:
        channels=category.channels
        for channel in channels:
            await channel.delete()
        await category.delete()
        GAME.finish()
        role_vivant=GAME.vivant_role
        role_mort=GAME.mort_role
        for member in role_vivant.members:
            await member.remove_roles(role_vivant,reason=None,atomic=True)
        for member in role_mort.members:
            await member.remove_roles(role_mort,reason=None,atomic=True)
        GAME.category=None
    gameManager.endedGame(GAME)
    await ctx.channel.send("clean done")

@bot.command(pass_context = True)
async def ecoute(ctx):
    GAME =  gameManager.findGame(ctx)
    players=GAME.players
    for player in players:
        if player.user == ctx.author and player.role.name=="Petite Fille" and ctx.channel == player.role.channel:
            await player.role.action(GAME)

@bot.command(pass_context = True)
async def clean_chan(ctx, text):
    
    category=ctx.guild.get_channel((int) (text))
    print(text)
    if category != None:
        channels=category.channels
        for channel in channels:
            await channel.delete()
        await category.delete()
        await ctx.channel.send("clean done")


bot.run(TOKEN)