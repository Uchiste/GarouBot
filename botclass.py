"""
    define the class Role, Sorcière, Villageois, Loup, Cupidon, Voyante, Chasseur, Petite-fille, Soeur, Salvateur, Lover, Joueur, Game
"""


emoji=['🍜','🐙','🙉','🦑','🐨','🐶','🐱','🐭','🐼','🐰','🦄','🐔','🍗','🤡','💃','🍖']

import asyncio
import random as random
from termios import TIOCM_RNG

##TO (timeout) in seconde
TO_SORCIERE=20*60
TO_CUPIDON=20*60
TO_SALVATEUR=20*60
TO_VOYANTE=20*60
TO_CHASSEUR=10*60
TO_NEWMAYOR=60*60
TO_FVOTE=50*60
TO_SVOTE=10*60
TO_WOLF=20*60

class Role:
    """
    Role is representing all the different kind of possible Role
    (virtual class)
    Composed at least by
        name (String) : the name of the 'Role'
        channel (class discord.TextChannel) : channel links to the player
        side (int) : 1 if the role is for the village, 0 if not
    """
    def __init__(self) -> None:
        pass

class Sorcière(Role):
    """
    Represents the Witch 'Role'
    Composed by :
        name (String): the name of the 'Role'
        channel (class discord.TextChannel): channel links to the player
        side (int): 1 if the role is for the village, -1 if not, 0 if neutral
        heal (Boolean): True if the Witch steal has her heal potion
        kill (Boolean): True if the Witch steal has her death potion
    """
    
    def __init__(self,channel):
        """Initializes the Witch.
        The Witch starts with one heal and one death potions. She is with the Village

        Args:
            channel (class discord.TextChannel): channel links to the player
        """
        self.name="Sorcière"
        self.channel=channel
        self.heal=True
        self.kill=True
        self.side=1
        
    async def action(self,game,bot):
        """start the turn of the Witch.
        The Witcher has maximum 3 possibilities:
        -Use heal potion to save the wolf's dead  [Can be done one time]
        -Use death potion to kill someone (She chooses the Player) [Can be done one time]
        -Do nothing

        Args:
            game (class Game): The current game party
            bot (class Bot): The current bot
            
        return: Nothing
        """
        sorciere=None
        non_sorciere=[]
        mort_soso=[]
        players=game.players
        for player in players:
            if player.role.name=="Sorcière":
                sorciere=player
            elif player.is_alive():
                non_sorciere.append(player)
        
        if len(game.night_death)==1 and self.heal==True and self.kill==True:
            mort_loup=game.night_death[0].user
            mes=sorciere.user.mention+" Salut sorcière ! Cette nuit, quelqu'un va mourir. Il s'agit de "+mort_loup.name+" tu as le choix entre:\n    ⚕️ la ressuciter\n    💀 tuer quelqu'un\n    💤 ne rien faire"
            message_sorciere=await self.channel.send(mes)
            await message_sorciere.add_reaction('⚕️')
            await message_sorciere.add_reaction('💀')
            await message_sorciere.add_reaction('💤')
            await message_sorciere.add_reaction('✅')
            
            choix=[]
            def checkSosoAction(reaction,user):
                if user == sorciere.user and reaction.message.id == message_sorciere.id and str(reaction.emoji) == '✅' :
                    return(True)
                return(False)
            try:
                await bot.wait_for("reaction_add", timeout=TO_SORCIERE, check=checkSosoAction)
                cache_msg = await message_sorciere.channel.fetch_message(message_sorciere.id)
                i=-1
                for reactions in cache_msg.reactions:
                    i=i+1
                    user_list = [user async for user in reactions.users() if user != bot.user]
                    
                    for user in user_list:
                        if user==sorciere.user and i < 3:
                            choix.append(i)
            except asyncio.TimeoutError:
                await self.channel.send("Le temps est dépassé, le choix sera aléatoire")
                choix=[random.randint(0,2)]
            if len(choix) !=1:
                choix=[random.randint(0,2)]
                await self.channel.send("C'est interdit, le choix sera aléatoire")
            if choix[0]== 0:#on sauve
                game.night_death.pop(0)
                self.heal=False
                await self.channel.send("Tu es une personne bien, la victime survivra.")
            elif choix[0] == 1: #on tue
                message="Tu veux donc tuer quelqu'un, qui va devoir boire ta fameuse potion ??:\n"
                i=0
                for j in non_sorciere:
                    message=message+ emoji[i] + j.user.name+'\n'
                    i=i+1
                message_sorciere = await self.channel.send(message)
        
                for j in range(0,i):
                    await message_sorciere.add_reaction(emoji[j])
                await message_sorciere.add_reaction('✅')
                try:
                    await bot.wait_for("reaction_add", timeout=TO_SORCIERE, check=checkSosoAction)
                except asyncio.TimeoutError:
                    await self.channel.send("Le temps est dépassé, le choix sera aléatoire")
                    mort_soso.append(random.randint(0,len(non_sorciere)))
                cache_msg = await message_sorciere.channel.fetch_message(message_sorciere.id)
                i=-1
                for reactions in cache_msg.reactions:
                    i=i+1
                    user_list = [user async for user in reactions.users() if user != bot.user]
                    
                    for user in user_list:
                        if user == sorciere.user and i < len(non_sorciere):
                            mort_soso.append(i)
                if (len(mort_soso)!=1):
                    mort_soso.append(random.randint(0,len(non_sorciere)))
                mort_soso=non_sorciere[mort_soso[0]]
                await self.channel.send("Très bien, "+mort_soso.user.name+" va mourir")
                self.kill=False
        elif len(game.night_death)==1 and self.heal==True and self.kill==False:
            mort_loup=game.night_death[0].user
            mes=sorciere.user.mention+" Salut sorcière cette nuit, quelqu'un va mourir. Il s'agit de **"+mort_loup.name+"** tu as le choix entre:\n    ⚕️ la ressuciter\n    💤 ne rien faire"
            message_sorciere=await self.channel.send(mes)
            await message_sorciere.add_reaction('⚕️')
            await message_sorciere.add_reaction('💤')
            await message_sorciere.add_reaction('✅')
            
            choix=[]
            def checkSosoAction(reaction,user):
                if user == sorciere.user and reaction.message.id == message_sorciere.id and str(reaction.emoji) == '✅' :
                    return(True)
                return(False)
            try:
                await bot.wait_for("reaction_add", timeout=TO_SORCIERE, check=checkSosoAction)
                cache_msg = await message_sorciere.channel.fetch_message(message_sorciere.id)
                i=-1
                for reactions in cache_msg.reactions:
                    i=i+1
                    user_list = [user async for user in reactions.users() if user != bot.user]
                    
                    for user in user_list:
                        if user==sorciere.user and i < 2:
                            choix.append(i)
            except asyncio.TimeoutError:
                await self.channel.send("Le temps est dépassé, le choix sera aléatoire")
                choix=[random.randint(0,1)]
            if len(choix) !=1:
                choix=[random.randint(0,1)]
                await self.channel.send("C'est interdit, le choix sera aléatoire")
            if choix[0]== 0:#on sauve
                un_mort_loup=False
                await self.channel.send("Tu es une personne bien, la victime survivra.")
                self.heal=False
        elif self.kill == True:
            mes=sorciere.user.mention+" Salut sorcière, tu as le choix entre:\n    💀 tuer quelqu'un\n    💤 ne rien faire"
            message_sorciere=await self.channel.send(mes)
            await message_sorciere.add_reaction('💀')
            await message_sorciere.add_reaction('💤')
            await message_sorciere.add_reaction('✅')
            
            choix=[]
            def checkSosoAction(reaction,user):
                if user == sorciere.user and reaction.message.id == message_sorciere.id and str(reaction.emoji) == '✅' :
                    return(True)
                return(False)
            try:
                await bot.wait_for("reaction_add", timeout=TO_SORCIERE, check=checkSosoAction)
                cache_msg = await message_sorciere.channel.fetch_message(message_sorciere.id)
                i=-1
                for reactions in cache_msg.reactions:
                    i=i+1
                    user_list = [user async for user in reactions.users() if user != bot.user]
                    
                    for user in user_list:
                        if user==sorciere.user and i < 2:
                            choix.append(i)
            except asyncio.TimeoutError:
                await self.channel.send("Le temps est dépasser, le choix sera aléatoire")
                choix=[random.randint(0,1)]
            if len(choix) !=1:
                choix=[random.randint(0,1)]
                await self.channel.send("C'est interdit, le choix sera aléatoire")
            if choix[0] == 0: #on tue
                message="Tu veux donc tuer quelqu'un, qui va devoir boire ta fameuse potion ??:\n"
                i=0
                for j in non_sorciere:
                    message=message+ emoji[i] + j.user.name+'\n'
                    i=i+1
                message_sorciere = await self.channel.send(message)
        
                for j in range(0,i):
                    await message_sorciere.add_reaction(emoji[j])
                await message_sorciere.add_reaction('✅')
                
                try:
                    await bot.wait_for("reaction_add", timeout=TO_SORCIERE, check=checkSosoAction)
                except asyncio.TimeoutError:
                    await self.channel.send("Le temps est dépassé, le choix sera aléatoire")
                    mort_soso.append(random.randint(0,len(non_sorciere)))
                cache_msg = await message_sorciere.channel.fetch_message(message_sorciere.id)
                i=-1
                for reactions in cache_msg.reactions:
                    i=i+1
                    user_list = [user async for user in reactions.users() if user != bot.user]
                    
                    for user in user_list:
                        if user == sorciere.user and i < len(non_sorciere):
                            mort_soso.append(i)
                if (len(mort_soso)!=1):
                    mort_soso.append(random.randint(0,len(non_sorciere)))
                mort_soso=non_sorciere[mort_soso[0]]
                await self.channel.send("Très bien, "+mort_soso.user.name+" va mourir")
                self.kill=False
                game.night_death.append(mort_soso)
        await self.channel.send("Bonne nuit la sorcière")
    
    async def jour(self,channel_public_place,user):
        """set the role for the day
        The Witch can speak during the day in the public channel

        Args:
            channel_public_place (class discord.TextChannel): the public channel of the current game
            user (class discord.User): The user concerned
        """
        await channel_public_place.set_permissions(user,read_messages=True,send_messages=True)

class Villageois(Role):
    """
    Represents the Villager 'Role'
    Composed by :
        name (String): the name of the 'Role'
        channel (class discord.TextChannel): channel links to the player
        side (int): 1 if the role is for the village, -1 if not, 0 if neutral
    """
    def __init__(self,channel):
        """Initializes the Villager.
        He is with the Village

        Args:
            channel (class discord.TextChannel): channel links to the player
        """
        self.name="Villageois"
        self.channel=channel
        self.side=1
    async def jour(self,channel_public_place,user):
        """set the role for the day
        The Villager can speak during the day in the public channel

        Args:
            channel_public_place (class discord.TextChannel): the public channel of the current game
            user (class discord.User): The user concerned
        """
        await channel_public_place.set_permissions(user,read_messages=True,send_messages=True)

class Loup(Role):
    """
    Represents the Wolf 'Role'
    Composed by :
        name (String): the name of the 'Role'
        channel (class discord.TextChannel): channel links to the player
        side (int): 1 if the role is for the village, -1 if not, 0 if neutral
    """
    def __init__(self,channel):
        """Initializes the Wolf.
        He is against the Village

        Args:
            channel (class discord.TextChannel): channel links to the player
        """
        self.name="Loup"
        self.channel=channel
        self.side=-1
    async def jour(self,channel_public_place,user):
        """set the role for the day
        The Wolf can speak during the day in the public channel. But I can't speak in his specific channel

        Args:
            channel_public_place (class discord.TextChannel): the public channel of the current game
            user (class discord.User): The user concerned
        """
        await self.channel.set_permissions(user,read_messages=True,send_messages=False)
        await channel_public_place.set_permissions(user,read_messages=True,send_messages=True)
      
class Cupidon(Role):
    """
    Represents the Cupidon 'Role'
    Composed by :
        name (String): the name of the 'Role'
        channel (class discord.TextChannel): channel links to the player
        side (int): 1 if the role is for the village, -1 if not, 0 if neutral
    """
    def __init__(self,channel):
        """Initializes Cupidon.
        He is with the Village

        Args:
            channel (class discord.TextChannel): channel links to the player
        """
        self.name="Cupidon"
        self.channel=channel
        self.power=True
        self.side=1
    async def action(self,cupidon,game,bot):
        """start the turn of Cupidon.
        He chooses a couple at the begining of the game
        Args:
            game (class Game): The current game party
            bot (class Bot): The current bot
            
        return: Nothing
        """
        if self.power==True:
            self.power=False
            players=game.players
            #on demande à cupidon qui mettre en couple
            message=""
            i=0
            for player in players:
                message=message+ emoji[i] + player.user.name+'\n'
                i=i+1
    
            message_cupidon=await self.channel.send(cupidon.user.mention+"! Salut Cupidon, tu dois choisir qui va être amoureux parmi:\n"+message)
            def checkCupidon(reaction,user):
                if user==cupidon.user and reaction.message.id == message_cupidon.id and (str(reaction.emoji) == '✅' or str(reaction.emoji) =='❌'):
                    return(True)
                return(False)

            for j in range(0,i):
                await message_cupidon.add_reaction(emoji[j])
            await message_cupidon.add_reaction('✅')
            couple=[]
            try:
                await bot.wait_for("reaction_add", timeout=TO_CUPIDON, check=checkCupidon)
                cache_msg = await message_cupidon.channel.fetch_message(message_cupidon.id)
                i=-1
                for reactions in cache_msg.reactions:
                    i=i+1
                    user_list = [user async for user in reactions.users() if user != bot.user]
                    
                    for user in user_list:
                        if user==cupidon.user and i < len(players):
                            couple.append(players[i])
            except asyncio.TimeoutError:
                await self.channel.send("Le temps est dépassé, le choix sera aléatoire")
                couple.append(players[random.randint(0,len(players)-1)])
                jalea=players[random.randint(0,len(players)-1)]
                while jalea.user == couple[0].user:
                    jalea=players[random.randint(0,len(players)-1)]
                couple.append(jalea)
            if len(couple) !=2:
                await self.channel.send("Erreur dans la saisie, le choix est aléatoire")
                couple.append(players[random.randint(0,len(players)-1)])
                jalea=players[random.randint(0,len(players)-1)]
                while jalea.user == couple[0].user:
                    jalea=players[random.randint(0,len(players)-1)]
                couple.append(jalea)
            mes="Le couple est composé de "+couple[0].user.name + " et "+ couple[1].user.name
            await self.channel.send(mes)
            print(couple)
            channel_lover=await game.category.create_text_channel("Amoureux")
            game.def_lover(Lover(couple[1],couple[0],channel_lover))
            await channel_lover.set_permissions(couple[1].user,read_messages=True,send_messages=True)
            await channel_lover.set_permissions(couple[0].user,read_messages=True,send_messages=True)
            await channel_lover.send("Salut "+couple[1].user.mention+" et "+couple[0].user.mention+" askip vous êtes en couple ;) !")

    async def jour(self,channel_public_place,user):
        """set the role for the day
        Cupidon can speak during the day in the public channel.

        Args:
            channel_public_place (class discord.TextChannel): the public channel of the current game
            user (class discord.User): The user concerned
        """
        await channel_public_place.set_permissions(user,read_messages=True,send_messages=True)

class Voyante(Role):
    """
    Represents the Clairvoyant 'Role'
    Composed by :
        name (String): the name of the 'Role'
        channel (class discord.TextChannel): channel links to the player
        side (int): 1 if the role is for the village, -1 if not, 0 if neutral
    """
    def __init__(self,channel):
        """Initializes Clairvoyant.
        He is with the Village

        Args:
            channel (class discord.TextChannel): channel links to the player
        """
        self.name="Voyante"
        self.channel=channel
        self.side=1
    async def action(self,voyante,game,bot):
        """start the turn of Clairvoyant.
        She can discover the role of one Player each nigth
        Args:
            game (class Game): The current game party
            bot (class Bot): The current bot
            
        return: Nothing
        """
        non_voyante=[]
        players=game.players
        for player in players:
            if player != voyante and player.is_alive:
                non_voyante.append(player)
    
        message=""
        i=0
        for player in non_voyante:
            message=message+ emoji[i] + player.user.name+'\n'
            i=i+1

        message_voyante=await self.channel.send(voyante.user.mention+"! Salut Voyante, tu dois choisir qui tu veux voir cette nuit:\n"+message)
        def checkVoyante(reaction,user):
            if user==voyante.user and reaction.message.id == message_voyante.id and (str(reaction.emoji) == '✅' or str(reaction.emoji) =='❌'):
                return(True)
            return(False)

        for j in range(0,i):
            await message_voyante.add_reaction(emoji[j])
        await message_voyante.add_reaction('✅')
        vision=[]
        try:
            await bot.wait_for("reaction_add", timeout=TO_VOYANTE, check=checkVoyante)
        except asyncio.TimeoutError:
            await self.channel.send("Le temps est dépassé ou le choix est erroné, le choix sera donc aléatoire")
        cache_msg = await message_voyante.channel.fetch_message(message_voyante.id)
        i=-1
        
        for reactions in cache_msg.reactions:
            i=i+1
            user_list = [user async for user in reactions.users() if user != bot.user]
            
            for user in user_list:
                if user==voyante.user and i < len(non_voyante):
                    vision.append(non_voyante[i])
        if len(vision) !=1:
            vision=[non_voyante[random.randint(0,len(non_voyante)-1)]]
        mes="Tu as décidé de voir "+vision[0].user.name+ " qui est "+vision[0].role.name

        await self.channel.send(mes)

    async def jour(self,channel_public_place,user):
        """set the role for the day
        Cupidon can speak during the day in the public channel.

        Args:
            channel_public_place (class discord.TextChannel): the public channel of the current game
            user (class discord.User): The user concerned
        """
        await channel_public_place.set_permissions(user,read_messages=True,send_messages=True)

class Chasseur(Role):
    """
    Represents the Hunter 'Role'
    Composed by :
        name (String): the name of the 'Role'
        channel (class discord.TextChannel): channel links to the player
        side (int): 1 if the role is for the village, -1 if not, 0 if neutral
    """
    def __init__(self,channel):
        """Initializes the Hunter.
        He is with the Village

        Args:
            channel (class discord.TextChannel): channel links to the player
        """
        self.name="Chasseur"
        self.channel=channel
        self.side=1
        self.power=True

    async def action(self,game,bot):
        """start the turn of the Hunter.
        When he dies, he can kill someone else or do nothing
        Args:
            game (class Game): The current game party
            bot (class Bot): The current bot
            
        return: Nothing
        """
        if self.power==True:
            self.power=False
            #je vais demander qui il veut tuer
            players=game.players
            chasseur=None
            targets=[]
            for player in players:
                if player.role.name!=self.name and player.is_alive():
                    targets.append(player)
                elif player.role.name=="Chasseur":
                    chasseur = player
            message="Salut "+chasseur.user.mention+",tu es mort, tu dois choisir qui va mourir ou ne rien faire:\n"
            i=0
            for target in targets:
                message=message+ emoji[i] +" "+ target.user.name+'\n'
                i=i+1
            message_chasseur=await chasseur.role.channel.send(message)
            await message_chasseur.pin()
            for j in range(0,i):
                await message_chasseur.add_reaction(emoji[j])
            await message_chasseur.add_reaction('💤')
            await message_chasseur.add_reaction('✅')
            
            choice=[]
            def checkChasseur(reaction,user):
                if user == chasseur.user and reaction.message.id == message_chasseur.id and str(reaction.emoji) == '✅' :
                    return(True)
                return(False)
            try:
                await bot.wait_for("reaction_add", timeout=TO_CHASSEUR, check=checkChasseur)
                cache_msg = await message_chasseur.channel.fetch_message(message_chasseur.id)
                i=-1
                for reactions in cache_msg.reactions:
                    i=i+1
                    user_list = [user async for user in reactions.users() if user != bot.user]
                    
                    for user in user_list:
                        if user.id ==chasseur.user.id and i < len(targets)+1:
                            choice.append(i)
            except asyncio.TimeoutError:
                await chasseur.role.channel.send("Le temps est dépassé, le choix sera aléatoire")
                choice=[random.randint(0,len(targets))]
            if len(choice) !=1:
                choice=[random.randint(0,len(targets))]
                await chasseur.role.channel.send("C'est impossible, le choix sera aléatoire")
            if choice[0] == len(targets):
                await chasseur.role.channel.send("Tu ne fais rien, tu es pacifiste.")
                return()
            mort=targets[choice[0]]
            #je tue
            await game.channel_public_place.send("Le chasseur a décidé de tirer sur "+mort.user.mention)
            await game.channel_recap.send("Le chasseur a décidé de tirer sur "+mort.user.mention)
            await mort.kill(game.channel_public_place,game.channel_graveyard,game.channel_recap,game.vivant_role,game.mort_role)
            await chasseur.role.channel.send("Tu as décidé de tuer "+mort.user.name)
            #check cupidon
            await game.check_lover()
    async def jour(self,channel_public_place,user):
        """set the role for the day
        Cupidon can speak during the day in the public channel.

        Args:
            channel_public_place (class discord.TextChannel): the public channel of the current game
            user (class discord.User): The user concerned
        """
        await channel_public_place.set_permissions(user,read_messages=True,send_messages=True)

class Petite_fille(Role):
    """
    Represents the Little girl 'Role'
    Composed by :
        name (String): the name of the 'Role'
        channel (class discord.TextChannel): channel links to the player
        side (int) : 1 if the role is for the village, -1 if not, 0 if neutral
        deja_lu (int) : the last message read from the wolf's channel
    """
    def __init__(self,channel):
        """Initializes the Little girl.
        She is with the Village

        Args:
            channel (class discord.TextChannel): channel links to the player
        """
        self.name="Petite Fille"
        self.channel=channel
        self.side=1
        self.deja_lu=0
        
    async def action(self,game):
        """start the turn of the Little girl.
        She can ask to know what the wolf are saying with the command '!ecoute'
        Args:
            game (class Game): The current game party
            
        return: Nothing
        """
        players=game.players
        chan_loup=None
        for player in players:
            if player.role.name=="Loup":
                chan_loup=player.role.channel
        if chan_loup==None:
            await self.channel.send("Il n'y a pas de loup à écouter")
        else:
            messages=await chan_loup.history(limit = 1000).flatten()
            messages.reverse()
            loup=None
            for message in messages:
                if message.author.name != "GarouBOT":
                    if message.id > self.deja_lu:
                        if loup != message.author:
                                loup=message.author
                                await self.channel.send("```    Un loup dit:```")
                        await self.channel.send(message.content)  
            self.deja_lu=message.id
            print("ecoute fin")
            await self.channel.send("```Tu as tout entendu pour l'instant```")

    async def jour(self,channel_public_place,user):
        """set the role for the day
        The Little girl can speak during the day in the public channel.

        Args:
            channel_public_place (class discord.TextChannel): the public channel of the current game
            user (class discord.User): The user concerned
        """
        await channel_public_place.set_permissions(user,read_messages=True,send_messages=True)

class Soeur(Role):
    """
    Represents the Sister 'Role'
    Composed by :
        name (String): the name of the 'Role'
        channel (class discord.TextChannel): channel links to the player
        side (int) : 1 if the role is for the village, -1 if not, 0 if neutral
    """
    def __init__(self,channel):
        """Initializes the Sister.
        She is with the Village
        She can speak to her Sister during the night

        Args:
            channel (class discord.TextChannel): channel links to the player
        """
        self.name="Soeur"
        self.channel=channel
        self.side=1
        
    async def jour(self,channel_public_place,user):
        """set the role for the day
        The Sister can speak during the day in the public channel.
        She can speak to her Sister during the night
    
        Args:
            channel_public_place (class discord.TextChannel): the public channel of the current game
            user (class discord.User): The user concerned
        """
        await self.channel.set_permissions(user,read_messages=True,send_messages=False)
        await channel_public_place.set_permissions(user,read_messages=True,send_messages=True)

class Salvateur(Role):
    """
    Represents the Salvateur'
    Composed by :
        name (String): the name of the 'Role'
        channel (class discord.TextChannel): channel links to the player
        side (int) : 1 if the role is for the village, -1 if not, 0 if neutral
        self.previous_night (class discord.user) : last personn he protected
    """
    def __init__(self,channel):
        """Initializes the Salvateur.
        He is with the Village
        He can protect every nigth someone (can't be the same personn two following night)

        Args:
            channel (class discord.TextChannel): channel links to the player
        """
        self.name="Salvateur"
        self.channel=channel
        self.side=1
        self.previous_night=None
        
    async def jour(self,channel_public_place,user):
        """set the role for the day
        The Salvateur can speak during the day in the public channel.
        She can speak to her Sister during the night
    
        Args:
            channel_public_place (class discord.TextChannel): the public channel of the current game
            user (class discord.User): The user concerned
        """
        await channel_public_place.set_permissions(user,read_messages=True,send_messages=True)
        
    async def action(self,game,bot):
        """start the turn of the Salvateur.
        Choose someone to protect.
        
        Args:
            game (class Game): The current game party
            
        return: Nothing
        """
        players_alive=[]
        salvateur=None
        players=game.players
        for player in players:
            if player.is_alive():
                if  player.role.name=="Salvateur":
                    salvateur=player
                players_alive.append(player)
    
        message=""
        i=0
        for player in players_alive:
            message=message+ emoji[i] + player.user.name+'\n'
            i=i+1

        message_voyante=await self.channel.send(salvateur.user.mention+"! Salut Salvateur, tu dois choisir qui proteger cette nuit (pas deux fois de suite la même personne):\n"+message)
        def checkVoyante(reaction,user):
            if user==salvateur.user and reaction.message.id == message_voyante.id and (str(reaction.emoji) == '✅' or str(reaction.emoji) =='❌'):
                return(True)
            return(False)

        for j in range(0,i):
            await message_voyante.add_reaction(emoji[j])
        await message_voyante.add_reaction('✅')
        protect=[]
        try:
            await bot.wait_for("reaction_add", timeout=TO_SALVATEUR, check=checkVoyante)
        except asyncio.TimeoutError:
            await self.channel.send("Le temps est dépassé ou le choix est erroné, le choix sera donc aléatoire")
        cache_msg = await message_voyante.channel.fetch_message(message_voyante.id)
        i=-1
        
        for reactions in cache_msg.reactions:
            i=i+1
            user_list = [user async for user in reactions.users() if user != bot.user]
            
            for user in user_list:
                if user==salvateur.user and i < len(players_alive):
                    protect.append(players_alive[i])
        if len(protect) !=1:
            protect=[players_alive[random.randint(0,len(players_alive)-1)]]
        while protect[0] == self.previous_night: #on regarde si c'est la meme personne que la nuit précedente
            await self.channel.send("Le choix est identique à la nuit précedente, on fait aléatoirement")
            protect=[players_alive[random.randint(0,len(players_alive)-1)]]
        
        #si il a proteger le mort alors on enleve le mort
        j=0
        print("protect =",protect[0])
        print("death =",game.night_death)
        for i in range (0,len(game.night_death)):
            if game.night_death[i-j] == protect[0]:
                game.night_death.pop(i-j)
                j+=1

        self.previous_night=protect[0]
        await self.channel.send(protect[0].user.name+" va être protèger cette nuit !")


class Lover():
    """
    Represents a couple 
    Composed by :
        channel (class discord.TextChannel): channel links to the couple
        player1 & player2 (class discord.member) : which are the two member of the couple
    """
    def __init__(self,player1,player2,channel):
        """initializes the couple
        
        Args:
            channel (class discord.TextChannel): channel links to the couple
            player1 & player2 (class discord.member) : which are the two member of the couple
        return: Nothing
        """
        self.player1=player1
        self.player2=player2
        self.channel=channel
        
    async def check_death(self,channel_public_place,channel_graveyard,channel_recap,vivant,mort):
        """This function check if one member of the couple is dead or not. If he is, the other member die too.

        Args:
            channel_public_place
            channel_graveyard
            channel_recap
            vivant : discord role (living person)
            mort : discord role (dead person)
        """
        if not(self.player1.is_alive()) and self.player2.is_alive():
            await channel_public_place.send(self.player2.user.mention+" était amoureux de "+self.player1.user.mention)
            await channel_recap.send(self.player2.user.mention+" était amoureux de "+self.player1.user.mention)
            await self.player2.kill(channel_public_place,channel_graveyard,channel_recap,vivant,mort)
        elif self.player1.is_alive() and not(self.player2.is_alive()):
            await channel_public_place.send(self.player1.user.mention+" était amoureux de "+self.player2.user.mention)
            await channel_recap.send(self.player1.user.mention+" était amoureux de "+self.player2.user.mention)
            await self.player1.kill(channel_public_place,channel_graveyard,channel_recap,vivant,mort)
            
    async def nuit(self):
        """set the couple for the night
        The couple can speak during the night in their own channel
        """
        if self.player1.is_alive() and self.player2.is_alive():
            await self.channel.set_permissions(self.player1.user,read_messages=True, send_messages=True)
            await self.channel.set_permissions(self.player2.user,read_messages=True, send_messages=True)
            
    async def jour(self):
        """set the couple for the night
        The couple can speak during the night in their own channel
        """
        await self.channel.set_permissions(self.player1.user,read_messages=True, send_messages=False)
        await self.channel.set_permissions(self.player2.user,read_messages=True, send_messages=False)


        
class Joueur:
    """represents a Player
    """
    def __init__(self,user,role):
        """sets the class with is role and the discord user
        The player start alive.

        Args:
            user
            role
        """
        self.alive=True
        self.user=user
        self.role=role

    def is_alive(self):
        """sets the class with is role and the discord user
        The player start alive.

        Args:
            user
            role
        """
        return self.alive

    async def kill(self,channel_public_place,channel_graveyard,channel_recap,vivant,mort):
        """Kill the player and uptodate his rigths

        Args:
            channel_public_place
            channel_graveyard
            channel_recap
            vivant : discord role 
            mort : discord role
        """
        self.alive=False
        await channel_public_place.set_permissions(self.user, read_messages=True, send_messages=False)
        await self.role.channel.set_permissions(self.user, read_messages=True, send_messages=False)
        await channel_graveyard.set_permissions(self.user, read_messages=True, send_messages=True)
        await channel_public_place.send(self.user.mention+ "est mort, iel était "+self.role.name)
        await channel_recap.send(self.user.mention+ "est mort, iel était "+self.role.name)
        member=await channel_public_place.guild.fetch_member(self.user.id)
        await member.remove_roles(vivant,reason=None)
        await member.add_roles(mort,reason=None)

    async def nuit(self,channel_public_place):
        """starts the nigth for the player

        Args:
            channel_public_place
        """
        if self.alive==True:
            await self.role.channel.set_permissions(self.user,read_messages=True,send_messages=True)
            await channel_public_place.set_permissions(self.user,read_messages=True,send_messages=False)


class Game:
    """represents a Game
    """
    def __init__(self,ctx,ID):
        self.id=ID
        self.server_id=ctx.guild.id
        self.started=False
        self.category=None
        self.channel_public_place=None
        self.channel_graveyard=None
        self.channel_polling=None
        self.MDJ=None
        self.vivant_role=None
        self.mort_role=None
        self.spectateur=None
        for role in ctx.guild.roles:
            if role.name == "Vivant":
                self.vivant_role = role
            elif role.name == "Mort":
                self.mort_role = role
            elif role.name == "MDJ":
                self.MDJ = role
            elif role.name == "Spectateur":
                self.spectateur = role
        
        self.players=None
        self.night_death=[]
        self.lover=None
        self.with_mayor=True
        self.mayor=None
        self.day=0

    def initialize(self,category,public_place,graveyard,polling,recap,players):
        """set all the parameters (specific to the discord's server)
        
        needs :
            category: class discord.CategoryChannel
            public_place: class discord.TextChannel
            graveyard: class discord.TextChannel
            polling: class discord.TextChannel
            recap: class discord.TextChannel
            players: list of players
            vivant: class discord.Role
            mort: class discord.Role
        """
        self.category=category
        self.channel_public_place=public_place
        self.channel_graveyard=graveyard
        self.channel_polling=polling
        self.channel_recap=recap
        self.players=players
        
    def is_started(self):
        """returns 'true' if the game is already started / 'false' if not
        """
        return(self.started)
    
    def start(self):
        """set started paramaters to true (the game is started)
        """
        self.started=True
        
    def finish(self):
        """uses at the end of the game
        """
        print("PARTIE FINI id ",self.id)
        self.started=False
        self.channel_public_place=None
        self.channel_graveyard=None
        self.channel_polling=None
        self.players=None
        self.night_death=[]
        self.lover=None
        self.with_mayor=True
        self.mayor=None
        
    def def_lover(self,lover):
        """set the couple
        """
        self.lover=lover
        
    async def check_lover(self):
        """checks if one member of the couple is dead or not
        """
        if self.lover!=None:
            await self.lover.check_death(self.channel_public_place,self.channel_graveyard,self.channel_recap,self.vivant_role,self.mort_role)
    
    def without_mayor(self):
        """does the election of the mayor

        Args:
            bot:  class discord.ClientUser
        """
        self.with_mayor=False

    async def define_mayor(self,bot):
        """does the election of the mayor

        Args:
            bot:  class discord.ClientUser
        """
        if self.mayor == None and self.with_mayor==True:
            players_alive=[]
            users_alive=[]
            
            for player in self.players:
                if player.is_alive():
                    players_alive.append(player)
                    users_alive.append(player.user)
            await self.channel_public_place.send("Le vote pour le maire va commencer !!")
            message=""
            i=0
            
            for player in players_alive:
                message=message+ emoji[i] + player.user.name+'\n'
                i=i+1
            message_place_publique=await self.channel_polling.send("la personne qui aura le plus grand nombre de vote sera maire, parmi:\n"+message)
            for j in range(0,i):
                await message_place_publique.add_reaction(emoji[j])
            election=[0 for z in range(0,len(players_alive))]
            await asyncio.sleep(TO_NEWMAYOR)
            cache_msg = await self.channel_polling.fetch_message(message_place_publique.id)
            i=-1
            for reactions in cache_msg.reactions:
                i=i+1
                user_list = [user async for user in reactions.users() if user != bot.user]
                for user in user_list:
                    if user in users_alive and i < len(users_alive):
                        election[i]+=1
            imax=[-1]
            vmax=0
            print(election)
            for z in range (0,len(players_alive)):
                if vmax == election[z]:
                    imax.append(z)
                elif vmax < election[z]:
                    vmax=election[z]
                    imax=[z]
            mes=""
            if imax[0]==-1:
                mes="Vous n'avez choisi personne, le vote se fera aléatoirement\n"
                rand=random.randint(0,len(players_alive)-1)
                maire=players_alive[rand]
                mes=mes+"C'est donc "+maire.user.mention+" qui sera maire"
            elif len(imax) != 1:
                mes="Il y a égalité, le vote se fera aléatoirement parmi les heureux élus\n"
                rand=random.randint(0,len(imax)-1)
                maire=players_alive[rand]
                mes=mes+"C'est donc "+maire.user.mention+" qui sera maire"
            else:
                maire=players_alive[imax[0]]
                mes="Vous avez décidé d'élire "+maire.user.mention
            await self.channel_public_place.send(mes)
            await self.channel_polling.send(mes)
            await self.channel_recap.send(mes)
            self.mayor=maire

    async def check_mayor(self,bot):
        """checks if the mayor is dead or not.
        If the mayor is dead, he will choose the next mayor. If he doesn't choose, the choice is random.

        Args:
            bot: class discord.ClientUser
        """
        if self.mayor!= None and self.with_mayor==True:
            if self.mayor.is_alive()==False:
                players_alive=[]
                users_alive=[]
                for player in self.players:
                    if player.is_alive():
                        players_alive.append(player)
                        users_alive.append(player.user)
                await self.channel_public_place.send("Le maire est mort, un nouveau maire doit être choisi!")
                message=""
                for j in range(0,len(players_alive)):
                    message=message+emoji[j]+users_alive[j].name+"\n"
                message_perso=await self.channel_polling.send(self.mayor.user.mention+" choisis qui sera maire à ta place, parmi:\n"+message)
                for j in range(0,len(players_alive)):
                    await message_perso.add_reaction(emoji[j])
                await message_perso.add_reaction('✅')
                fmaire=[]
                def checkMaire(reaction,user):
                    if reaction.message.id == message_perso.id and (str(reaction.emoji) == '✅') and user.id==self.mayor.user.id:
                        return(True)
                    return(False)
                try:
                    await bot.wait_for("reaction_add", timeout=TO_NEWMAYOR, check=checkMaire)
                    cache_msg = await self.channel_polling.fetch_message(message_perso.id)
                    i=-1
                    for reactions in cache_msg.reactions:
                        i=i+1
                        user_list = [user async for user in reactions.users() if user != bot.user]
                        for user in user_list:
                            if user == self.mayor.user and i<len(players_alive):
                                fmaire.append(players_alive[i])
                except asyncio.TimeoutError:
                    await message_perso.channel.send("Le temps est dépassé, le choix sera aléatoire")
                    fmaire=[players_alive[random.randint(0,len(players_alive)-1)]]
                if len(fmaire) !=1:
                    await message_perso.channel.send("Erreur dans la saisie, le choix est aléatoire")
                    fmaire=[players_alive[random.randint(0,len(players_alive)-1)]]
                maire=fmaire[0]
                mes="Le nouveau maire est "+maire.user.mention
                await self.channel_polling.send(mes)
                await self.channel_public_place.send(mes)
                self.mayor=maire

    async def vote(self,bot):
        """does the vote to select the player which will die.
        
        Args:
            bot: class discord.ClientUser
        """
        players_alive=[]
        users_alive=[]
        for player in self.players:
            if player.is_alive():
                players_alive.append(player)
                users_alive.append(player.user)
        await self.channel_public_place.send(self.vivant_role.mention+",vous allez voter pour la mort d'un membre du village!")
        await self.channel_polling.send(self.vivant_role.mention+",vous allez voter pour la mort d'un membre du village!")
        message=""
        for j in range(0,len(players_alive)):
            message=message+emoji[j]+users_alive[j].name+"\n"
        message_vote=await self.channel_polling.send("Votez pour les personnes qui doivent mourir, parmi:\n"+message)
        for j in range(0,len(players_alive)):
            await message_vote.add_reaction(emoji[j])
        vote=[0 for z in range(0,len(players_alive))]
        await asyncio.sleep(TO_FVOTE)
        cache_msg = await self.channel_polling.fetch_message(message_vote.id)
        i=-1
        for reactions in cache_msg.reactions:
            i=i+1
            user_list = [user async for user in reactions.users() if user != bot.user]
            for user in user_list:
                if user in users_alive and i < len(players_alive):
                    vote[i]+=1
                    if self.with_mayor == True and user == self.mayor.user:
                        vote[i]+=1
        
        m=max(vote)
        im=[a for a, j in enumerate(vote) if j == m]
        if len(im) != 1:
            message="Egalité, c'est le second round entre\n"
            for j in range (0,len(im)):
                message=message+emoji[j]+users_alive[im[j]].name+"\n"
            message_vote=await self.channel_polling.send(message)
            for j in range (0,len(im)):
                await message_vote.add_reaction(emoji[j])
            vote=[0 for z in range(0,len(im))]
            await asyncio.sleep(TO_SVOTE)
            i=-1
            for reactions in cache_msg.reactions:
                i=i+1
                user_list = [user async for user in reactions.users() if user != bot.user]
                for user in user_list:
                    if user in users_alive and i < len(im):
                        vote[i]+=1
                        if self.with_mayor == True and user.id == self.mayor.user.id:
                            vote[i]+=1
            m=max(vote)
            print("vote = ",vote)
            temp=[a for a, j in enumerate(vote) if j == m]
            im2=[]
            for t in temp:
                im2.append(im[t])
            im=im2
        if len(im) ==1:
            message="Vous avez décidé de pendre "+users_alive[im[0]].name+" !!"
            await self.channel_polling.send(message)
            await self.channel_public_place.send(message)
            im=im[0]
            await players_alive[im].kill(self.channel_public_place,self.channel_graveyard,self.channel_recap,self.vivant_role,self.mort_role)
        else:
            message = "Il y a encore égalité, personne ne va mourir."
            await self.channel_polling.send(message)
            await self.channel_public_place.send(message)

    async def nuit(self):
        """starts the nigth
        """
        self.night_death=[]
        await self.channel_public_place.send("C'est la nuit, le village s'endort! "+self.vivant_role.mention)
        await self.channel_recap.send("Nuit "+str(self.day)+":")
        self.day+=1
        for player in self.players:
            await player.nuit(self.channel_public_place)
        if self.lover!=None:
            await self.lover.nuit()
    
    async def jour(self):
        """starts the day
        """
        await self.channel_public_place.send("C'est le jour, le village se reveille! "+self.vivant_role.mention)
        await self.channel_recap.send("Jour "+str(self.day)+":")
        for player in self.players:
            if player.is_alive():
                await player.role.jour(self.channel_public_place,player.user)
        if self.lover!=None:
            await self.lover.jour()
    
    async def loups(self,bot):
        """starts the round of the wolf(s)

        Args:
            bot: _description_
        """
        players=self.players
        loups=[]
        non_loups=[]
        for player in players:
            if player.is_alive():
                if player.role.name=="Loup":
                    loups.append(player)
                else:
                    non_loups.append(player)
        if len(loups) != 0:
            smention=""
            for loup in loups:
                smention=smention+loup.user.mention
            chan_loup=loups[0].role.channel
            message=""
            i=0
            for non_loup in non_loups:
                message=message+ emoji[i] + non_loup.user.name+'\n'
                i=i+1

            if len(loups) == 1:
                message_loup=await chan_loup.send(smention+" Salut le loup, tu dois choisir qui tu veux tuer cette nuit:\n"+message)
            else:
                message_loup=await chan_loup.send(smention+" Salut les loups, vous devez choisir qui vous voulez tuer cette nuit:\n"+message)
            await message_loup.pin()
            for j in range(0,i):
                await message_loup.add_reaction(emoji[j])
            meurtre=[0 for z in range(0,len(non_loups))]
            await asyncio.sleep(TO_WOLF)
            def is_wolf(user):
                for w in loups:
                    if w.user==user:
                        return(True)
                return(False)
            cache_msg = await message_loup.channel.fetch_message(message_loup.id)
            i=-1
            for reactions in cache_msg.reactions:
                i=i+1
                user_list = [user async for user in reactions.users() if user != bot.user]
                
                for user in user_list:
                    if is_wolf(user) and i < len(non_loups):
                        meurtre[i]+=1
            
            imax=[-1]
            vmax=0
            for z in range (0,len(non_loups)):
                if vmax == meurtre[z]:
                    imax.append(z)
                elif vmax < meurtre[z]:
                    vmax=meurtre[z]
                    imax=[z]
            mes=""
            mort_loup=None
            if imax[0]==-1:
                mes="Vous n'avez choisi personne, le vote se fera aléatoirement\n"
                rand=random.randint(0,len(non_loups)-1)
                mort_loup=non_loups[rand]
                mes=mes+"C'est donc "+mort_loup.user.name+" qui va mourir"
            elif len(imax) != 1:
                mes="Il y a égalité, le vote se fera aléatoirement parmi les heureux élus\n"
                rand=random.randint(0,len(imax)-1)
                mort_loup=non_loups[imax[rand]]
                mes=mes+"C'est donc "+mort_loup.user.name+" qui va mourir"
            else:
                mort_loup=non_loups[imax[0]]
                mes="Vous avez décidé de tuer "+mort_loup.user.name
            await chan_loup.send(mes)
            self.night_death.append(mort_loup)

    async def check_end(self):
        """return true if the game is ended, false if not

        Returns:
            bool
        """
        gentil=0
        mechant=0
        players_alive=[]
        for player in self.players:
            if player.is_alive():
                players_alive.append(player)
        for player in players_alive:
            if player.role.side == 1:
                gentil+=1
                if player==self.mayor:
                    gentil+=1
            else:
                mechant+=1
                if player==self.mayor:
                    mechant+=1
        print("gentil = ",gentil, "   méchant =", mechant)
        if gentil==0 and mechant == 0:
            await self.channel_public_place.send("La partie est fini ! c'est une égalité ! GG à tous le monde")
            self.finish()
            return(True)
        elif gentil ==0:
            await self.channel_public_place.send("Les villageois ont perdu !! GG aux autre !!")
            self.finish()
            return True
        elif mechant ==0:
            await self.channel_public_place.send("Les villageois ont gagné !! GG à eux !!")
            self.finish()
            return True
        elif gentil==1 and mechant ==1 and len(players_alive)==2:
            if self.lover !=None and (self.lover.player1 == players_alive[0] or self.lover.player1 == players_alive[1]):
                await self.channel_public_place.send("Les amoureux ont gagné !! GG à eux !!")
                self.finish()
                return True
        return False
