#---------------------------------------
#	Import Libraries
#---------------------------------------
import clr, sys, json, os, codecs
clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")
import time

#---------------------------------------
#	[Required]	Script Information
#---------------------------------------
ScriptName = "Boop"
Website = ""
Creator = "Yaz12321"
Version = "1.0.1"
Description = "Viewer can boop another viewers through whispering the bot, the booped viewere has to guess who is the booper."

settingsFile = os.path.join(os.path.dirname(__file__), "settings.json")

#---------------------------------------
#   Version Information
#---------------------------------------

# Version:

# > 1.0.1 <
    #Fixed bugs
# > 1.0 < 
    # Official Release

class Settings:
    # Tries to load settings from file if given 
    # The 'default' variable names need to match UI_Config
    def __init__(self, settingsFile = None):
        if settingsFile is not None and os.path.isfile(settingsFile):
            with codecs.open(settingsFile, encoding='utf-8-sig',mode='r') as f:
                self.__dict__ = json.load(f, encoding='utf-8-sig') 
        else: #set variables if no settings file
            self.OnlyLive = False
            self.Command = "!boop"
            self.Permission = "Everyone"
            self.PermissionInfo = ""
            self.Cost = 5
            self.UseCD = True
            self.CoolDown = 0
            self.OnCooldown = "{0} the command is still on cooldown for {1} seconds!"
            self.UserCooldown = 10
            self.OnUserCooldown = "{0} the command is still on user cooldown for {1} seconds!"
            self.NotEnoughResponse = "{0} you don't have enough points to make it rain"
            self.Payout = 5
            self.Timer = 60
            self.NewBoop = "{0}, someone has booped you in secret. Type {1} followed by a username to guess who booped you and win {2} {4}. You have {3} seconds, and only one guess!"
            self.CorrectGuess = "{0}, that is correct! {1} was the one who booped you. You won {2} {3}"
            self.WrongGuess = "{0}, that was a wrong guess. The person who booped you has received {2} {3}, in addition to the {4} they paid to boop you!"
            self.NoGuess = "{0}, unfortunately, {1} seconds have passed, and you have not guessed! Too bad the one who booped you lost their points as well!"
            
    # Reload settings on save through UI
    def ReloadSettings(self, data):
        self.__dict__ = json.loads(data, encoding='utf-8-sig')
        return

    # Save settings to files (json and js)
    def SaveSettings(self, settingsFile):
        with codecs.open(settingsFile,  encoding='utf-8-sig',mode='w+') as f:
            json.dump(self.__dict__, f, encoding='utf-8-sig')
        with codecs.open(settingsFile.replace("json", "js"), encoding='utf-8-sig',mode='w+') as f:
            f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8-sig')))
        return


#---------------------------------------
# Initialize Data on Load
#---------------------------------------
def Init():
    # Globals
    global MySettings
    
    # Load in saved settings
    MySettings = Settings(settingsFile)
    global tim
    tim = 0

    # End of Init
    return

#---------------------------------------
# Reload Settings on Save
#---------------------------------------
def ReloadSettings(jsonData):
    # Globals
    global MySettings

    # Reload saved settings
    MySettings.ReloadSettings(jsonData)

    # End of ReloadSettings
    return

def Execute(data):

    global booper
    global booped
    global trigger
    global tim



    
    if data.IsWhisper() and data.GetParam(0).lower() == MySettings.Command and time.time()>tim + MySettings.CoolDown:
       
        #check if command is in "live only mode"
        if MySettings.OnlyLive:

            #set run permission
            startCheck = data.IsLive() and Parent.HasPermission(data.User, MySettings.Permission, MySettings.PermissionInfo)
            
        else: #set run permission
            startCheck = True
        
        #check if user has permission
        if startCheck and  Parent.HasPermission(data.User, MySettings.Permission, MySettings.PermissionInfo):
            
            #check if command is on cooldown
            if Parent.IsOnCooldown(ScriptName,MySettings.Command) or Parent.IsOnUserCooldown(ScriptName,MySettings.Command,data.User):
               
                #check if cooldown message is enabled
                if MySettings.UseCD: 
                    
                    #set variables for cooldown
                    cooldownDuration = Parent.GetCooldownDuration(ScriptName,MySettings.Command)
                    usercooldownDuration = Parent.GetUserCooldownDuration(ScriptName,MySettings.Command,data.User)
                    
                    #check for the longest CD!
                    if cooldownDuration > usercooldownDuration:
                    
                        #set cd remaining
                        m_CooldownRemaining = cooldownDuration
                        
                        #send cooldown message
                        Parent.SendStreamWhisper(data.User,MySettings.OnCooldown.format(data.User,m_CooldownRemaining))
                        
                        
                    else: #set cd remaining
                        m_CooldownRemaining = Parent.GetUserCooldownDuration(ScriptName,MySettings.Command,data.User)
                        
                        #send usercooldown message
                        Parent.SendStreamWhisper(data.User, MySettings.OnUserCooldown.format(data.User,m_CooldownRemaining))
            
            else: #check if user got enough points
                if MySettings.Cost < Parent.GetPoints(data.User):
                    if data.User in Parent.GetActiveUsers():
                    
                        if data.GetParam(1).lower() == data.User:
                            Parent.SendStreamWhisper(data.User, "Really? Nice try!")
                        else:
                            if data.GetParam(1).lower() in Parent.GetActiveUsers():
                                trigger = 0
                                booper = data.User.lower()
                                booped = data.GetParam(1).lower()
                                Parent.RemovePoints(data.User, MySettings.Cost)
                                Parent.SendTwitchMessage(MySettings.NewBoop.format(booped, MySettings.Command, MySettings.Payout, MySettings.CoolDown,Parent.GetCurrencyName()))
                                global tim
                                tim = time.time() 
                                # add cooldowns
                                Parent.AddUserCooldown(ScriptName,MySettings.Command,data.User,MySettings.UserCooldown)
                                Parent.AddCooldown(ScriptName,MySettings.Command,MySettings.Cooldown)

                            else:
                                Parent.SendStreamWhisper(data.User,"User not active")
                    else:
                        Parent.SendStreamWhisper(data.User,"You need to be active in chat to boop")

                
                else:
                    #send not enough currency response
                    Parent.SendStreamWhisper(data.User, MySettings.NotEnoughResponse.format(data.User,Parent.GetCurrencyName(),MySettings.Command,MySettings.Cost))

    try:
        if time.time() - tim < MySettings.CoolDown and trigger == 0:
            if data.IsChatMessage() and data.GetParam(0).lower() == MySettings.Command and data.User.lower() == booped and str(data.IsWhisper()) == "False":

                if data.GetParam(1).lower() == booper:
                    
                    Parent.AddPoints(data.User,data.UserName,MySettings.Payout)
                    Parent.SendTwitchMessage(MySettings.CorrectGuess.format(data.User, booper, MySettings.Payout, Parent.GetCurrencyName()))
                else:
                    pay = MySettings.Cost + MySettings.Payout
                    Parent.AddPoints(booper,booper,pay)
                    Parent.SendTwitchMessage(MySettings.WrongGuess.format(data.User, booper, MySettings.Payout, Parent.GetCurrencyName(), MySettings.Cost))
                booper = ""
                booped = ""
                trigger = 1
                
        if time.time() - tim > MySettings.CoolDown and trigger == 0:

            Parent.SendTwitchMessage(MySettings.NoGuess.format(booped,MySettings.CoolDown))
            trigger = 1
    except:
        pass
        
    return

def Tick():
    return

def UpdateSettings():
    with open(m_ConfigFile) as ConfigFile:
        MySettings.__dict__ = json.load(ConfigFile)
    return
