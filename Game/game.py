from map import rooms
from player import *
from items import *
from gameparser import *
from timeFunction import *
from objectAllocation import *
from mainMenu import *
from endings import *
import sched, time, random
import player
from combat import *
from pygame import mixer

def list_of_items(items):
    """This function takes a list of items (see items.py for the definition) and
    returns a comma-separated list of item names (as a string).
    """

    item_list = ""
    for item in items:
        if item_list != "":
            item_list += ", "
            item_list += item["name"]
        else:
            item_list += item["name"]
    return item_list
def print_room_items(room):
    items_string = list_of_items(room["items"])
    if items_string != "":
        type_print("There is " + items_string + " here.\n")    

def print_containers(container):
    """This function prints all of the containers in a given room"""
    type_print("SEARCH the " + container + ".")





def print_room(room):
    """This function takes a room as an input and nicely displays its name
    and description. The room argument is a dictionary with entries "name",
    "description" etc. (see map.py for the definition). The name of the room
    is printed in all capitals and framed by blank lines. Then follows the
    description of the room and a blank line again. If there are any items
    in the room, the list of items is printed next followed by a blank line
    (use print_room_items() for this). For example:
    """
    global moved
    # Display room name
    print("\n")
    if moved == True or moved == None: #If the player has moved
        type_print(room["name"].upper())
        # Display room description
        type_print(room["description"])
        moved = False

def exit_leads_to(exits, direction):
    """This function takes a dictionary of exits and a direction (a particular
    exit taken from this dictionary). It returns the name of the room into which
    this exit leads
    """
    return rooms[exits[direction]]["name"]


def print_exit(direction, leads_to):
    """This function prints a line of a menu of exits. It takes a direction (the
    name of an exit) and the name of the room into which it leads (leads_to),
    and should print a menu line in the following format:

    GO <EXIT NAME UPPERCASE> to <where it leads>.
    """
    type_print("GO " + direction.upper() + " to " + leads_to + ".")


def print_menu(exits, room_items, inv_items):
    """This function displays the menu of available actions to the player. The
    argument exits is a dictionary of exits as exemplified in map.py. The
    arguments room_items and inv_items are the items lying around in the room
    and carried by the player respectively. The menu should, for each exit,
    call the function print_exit() to print the information about each exit in
    the appropriate format. The room into which an exit leads is obtained
    using the function exit_leads_to(). Then, it should print a list of commands
    related to items: for each item in the room print:

    """
    global energy
    print_room_items(current_room)
    type_print("You can:")
    # Iterate over available exits
    for direction in exits:
        # Print the exit name and where it leads to
        print_exit(direction, exit_leads_to(exits, direction))
    for container in current_room["containers"]: #For all the containers in the room, print the containers using the function
        print_containers(container)
    type_print("INSPECT inventory items.")
    type_print("EAT inventory items.")
    if len(current_room["items"]) > 0: #If there are items in the room
        for item in current_room["items"]:
            type_print("TAKE " + item["name"] + ".")
    if current_room["name"] == "The Children's Ward" and item_ladder in inventory: #If the ladder can be attached
        type_print("ATTACH the ladder to the attic")
    if current_room["name"] == "Reception": #If you can leave through the front door
        type_print("LEAVE through the front door.")
    if current_room["name"] == "Morgue" and player.power_on == False: #If in the morgue and the power isn't on
        type_print("FLIP the switch.")
    if current_room["name"] == "Attic": #If in the attic
        type_print("JUMP through the window.")
    print("")
    if energy > 16: #Print how the player is feeling depending on how much energy they have
        type_print("You are full of energy!")
    elif energy > 12:
        type_print("You are feeling okay!")
    elif energy > 8:
        type_print("You are starting to feel tired.")
    elif energy > 4:
        type_print("You are very tired.")
    elif energy > 0:
        type_print("You are about to faint, eat something!")
    
    type_print("What do you want to do?")


def is_valid_exit(exits, chosen_exit):
    """This function checks, given a dictionary "exits" (see map.py) and
    a players's choice "chosen_exit" whether the player has chosen a valid exit.
    It returns True if the exit is valid, and False otherwise. Assume that
    the name of the exit has been normalised by the function normalise_input().
    For example:
    """
    return chosen_exit in exits


def execute_go(command):
    """This function, given the direction (e.g. "south") updates the current room
    to reflect the movement of the player if the direction is a valid exit
    (and prints the name of the room into which the player is
    moving). Otherwise, it prints "You cannot go there."
    """
    direction = command[1]
    global current_room
    global moved #This variable is used to check wether the room name and description needs to be printed
    exits = (current_room["exits"])
    if is_valid_exit(exits, direction):
        if current_room["name"] == "The Children's Ward" and direction == "up": #Check if wanting to go to the attic
            if rooms["Attic"]["ladder"] == True: #If the ladder has been placed, allow the movement
                moved = True
                current_room = move(exits, direction)
            else:
                type_print("You need a way up!")
                pass
        elif(current_room == rooms["Reception"] ):#Check if the morgue is targeted
            if(direction == "down"):
                if(item_keycard in inventory): #If the player has the keycard then allow the movement
                    moved = True 
                    player.morgue_open = True
                    current_room = move(exits, direction)              
                else:
                    type_print("This door requires a keycard!")
                    pass
            else:
                moved = True 
                current_room = move(exits, direction)
        elif current_room["name"] == "The Children's Ward" and direction == "right": #Check if wanting to go to the xray room
            if player.power_on == True: #If the power is on then allow the movement
                moved = True
                current_room = move(exits, direction)
            else:
                type_print("You need to turn the power on first!")
                pass

        else:
            moved = True 
            current_room = move(exits, direction)

def execute_take(command):
    """This function takes an item_id as an argument and moves this item from the
    list of items in the current room to the player's inventory. However, if
    there is no such item in the room, this function prints
    "You cannot take that."
    """
    item_id = command[1]
    global inventory
    items_room = current_room["items"]
    for item in items_room:
        if item_id == item["id"]:
            inventory.append(item)
            items_room.remove(item)
    

def execute_drop(command):
    """This function takes an item_id as an argument and moves this item from the
    player's inventory to list of items in the current room. However, if there is
    no such item in the inventory, this function prints "You cannot drop that."
    """
    item_id = command[1]
    global inventory
    items_room = current_room["items"]
    for item in inventory:
        if item_id == item["id"]:
            inventory.remove(item)
            items_room.append(item)

def execute_read(command):
    """This function prints the description of a chosen item in the players inventory"
    """

    item_id = command[1]
    global inventory
    for item in inventory:
        if item_id == item["id"]:
            if item["id"] != "map":
                type_print(item["description"])
            else:
                print(item["description"])#We print this because it would take a long time to type_print the ASCII map

def execute_search(command):
    """This function searches a given container and adds any items in it to the 
    player's inventory"""
    container_id = command[1] #The container in question
    global inventory #The player's inventory
    containers_room = current_room["containers"] #All of the containers in the room
    list_of_containers = [] #A blank list to be used later
    to_delete = "" #A blank string to be used later
    for item in containers_room:#For every cotainer in the room
        list_of_containers.append(item)#Add it to the list
        if container_id == item:#If the input container_id is the same as the one in the room
            if len(containers_room[container_id]) != 0:#If there are items in the container
                for items in current_room["containers"][container_id]:
                    type_print("You found a " + items["name"] + ".\n")
                    inventory.append(items)#Add the item(s) to the inventory
            else:
                if item[-1] == "s":
                    type_print("The " + item + " were empty.\n")
                else:
                    type_print("The " + item + " was empty.\n")
            to_delete = item #Remove the container from searchable containers
    if to_delete != "":
        del current_room["containers"][to_delete]

def execute_eat(command):

    item_id = command[1] #The item to be eaten
    global inventory
    global energy
    for item in inventory:
        if item_id == item["id"]:
            if item["energy"] != 0: #Check that the item can be eaten
                energy += item["energy"] #Add the 'energy' attribute value to the player's energy
                player.player_hp += item["energy"] #Also add it to the player's health
                inventory.remove(item) #Remove the food from the inventory
                type_print("You ate the " + item["name"] + ".")
                type_print("Your health is now " + str(player.player_hp) + ".")
            else:
                type_print("You can't eat that!")

def execute_combine(command):
    user_input = [] #A list that will be used later
    for word in command: #For all the items in command
        if word != "combine":
            user_input.append(word)#Add the word to the list

    CraftedItem = crafting(finding_crafting_items(user_input))#Find if an item can be crafted with these items

    if(CraftedItem != None):#If it can
        type_print("\n" + "You have crafted: " + CraftedItem["name"])
        global inventory

        inventory.append(CraftedItem)#Add the item to the inventory
        foundItems = finding_crafting_items(user_input)
        for item in foundItems:
            inventory.remove(item)#Remove all ingredients
    else:
        type_print("You can't craft anything with these")

def execute_jump(command):
    #This is used just so that the command will run when input
    pass

def execute_attach(command):
    #This function is used to attach the ladder to the attic, allowing access
    if current_room["name"] == "The Children's Ward" and item_ladder in inventory:
        rooms["Attic"]["ladder"] = True #Set the ladder attribute to true so that the attic can be accessed
        inventory.remove(item_ladder)
        type_print("You have attached the ladder to the attic.")

def execute_leave(command):
    #This function checks if the player can leave through the front door (has a key)
    if current_room["name"] == "Reception":
        if item_key in inventory:
            pass
        else:
            type_print("You need the key!")
    else:
        type_print("You can't leave through there!")

def execute_flip(command):
    #This function is so that the power can be turned on in the morgue
    if current_room["name"] == "Morgue":
        player.power_on = True #Turn the power on in the hospital (Not just backup generators)
        type_print("You flipped the switch and the room erupts into light, you hear machines powering up, the power is on!")


list_of_execute_functions = { "go": execute_go, "take": execute_take, "drop": execute_drop, "read": execute_read, "inspect": execute_read, "search": execute_search,
"eat": execute_eat, "combine": execute_combine, "craft": execute_combine, "jump": execute_jump, "attach": execute_attach, "leave": execute_leave, "flip": execute_flip}

#This is a dictionary of all the commands in the game, and the keywords that will trigger this command

def execute_command(command):
    """This function takes a command (a list of words as returned by
    normalise_input) and, depending on the type of action (the first word of
    the command: "go", "take", or "drop"), executes either execute_go,
    execute_take, or execute_drop, supplying the second word as the argument.

    """
    
    if 0 == len(command):
        return

    if len(command) == 1:
        type_print(command[0] + " what?")
    else:
        for key in list_of_execute_functions:
            if(command[0] == key):
                list_of_execute_functions[key](command)

            


def menu(exits, room_items, inv_items):
    """This function, given a dictionary of possible exits from a room, and a list
    of items found in the room and carried by the player, prints the menu of
    actions using print_menu() function. It then prompts the player to type an
    action. The players's input is normalised using the normalise_input()
    function before being returned.

    """

    # Display menu
    print_menu(exits, room_items, inv_items)

    # Read player's input
    user_input = input("> ")
    print()

    # Normalise the input
    normalised_user_input = normalise_input(user_input)

    return normalised_user_input

def finding_crafting_items(user_input):
    global inventory

    Items = []

    for word in user_input:
        for item in inventory:
            if (item["id"] == word):
                Items.append(item)


    return Items



def crafting(Items):

    if(len(Items) != 0):
        for item in items_list:

            if(len(item["recipe"]) != 0):


                Item_number = 0
                for item2 in Items:
                    if (item2 in item["recipe"]):
                        Item_number += 1

                if(Item_number == len(item["recipe"])):
                    return item
                


        return None    

    else:
        return None


def move(exits, direction):
    """This function returns the room into which the player will move if, from a
    dictionary "exits" of avaiable exits, they choose to move towards the exit
    with the name given by "direction".
    """

    # Next room to go to
    moved = True
    return rooms[exits[direction]]

def play_music():
    if os.path.isdir(os.getcwd() + "\sounds"):
        mixer.music.set_volume(0.1)
        if mixer.music.get_busy() == 0:
            mixer.music.load(os.path.dirname(os.path.realpath(__file__)) + "\sounds\\ambient" + str(random.randint(1,3)) + ".wav")
            mixer.music.play()


# This is the entry point of our program
def main():
    global energy
    gameStart = getCurrentTime() #time the game started
    energyLossTime = getCurrentTime() #time since energy was last lost
    initiateRooms() #Allocate items to containers in the objectAllocation.py file
    schedule = sched.scheduler(time.time, time.sleep) #A scheduler to set up timed events
    xrayCount = 0 #The amount of turns spent in the xray room
    command = [""] #Set command to a blank list so that NoneType errors don't occur
    difficulty = player.difficulty #Get the difficulty from the player.py
    if difficulty == "easy": #Set energy loss time depending on difficulty
        energyLoss = 200
    elif difficulty == "normal":
        energyLoss = 150
    else:
        energyLoss = 100

    # Main game loop
    while True:
        play_music()
        # Display game status (room description, inventory etc.)
        if checkEndings(current_room, command): #Check if any end conditions have been met
            break
        print_room(current_room)
        print_inventory_items(inventory)
        if current_room["name"] == "Xray Room": #Check if in the xray room since the xray room is dangerous
            if xrayCount >= 5: #If more than 5 turns in the xray room
                type_print("You have died")
                type_print("""
                    Your skin starts to ripple with waves of pain, you fall to the floor with a overwhelming sense of nausea. 
                    The pain overtakes and your eyes slowly start to close to the sickening sound of the broken X-Ray machines.
                    Your eyes never open again...""")
                print_game_over() #Kill the player
                break
            else:
                xrayCount += 1 #Another turn spend in the xray room
                schedule.enter(randint(5, 15), 1, type_print(xrayRoomMessage())) #Display a message in 5-15 seconds

        # Show the menu with possible actions and ask the player
        command = menu(current_room["exits"], current_room["items"], inventory)

        # Execute the player's command
        execute_command(command)
        if(player.morgue_open == True): #Check if the morgue has been opened, if so randomly spawn zombies in rooms
            if(command[0] == "go"):
                if(random.randint(1, 10) > 4):
                    combat(difficulty, random.randint(2, 10))

        if checkEndings(current_room, command): #Once again check if any win (or loss) conditions have been met
            break

        if timeSince(energyLossTime, getCurrentTime()) > energyLoss: #Check if it has been long enough to deduct energy
            energy -= 1





# Are we being run as a s`ipt? If so, run main().
# '__main__' is the name of the scope in which top-level code executes.
# See https://docs.python.org/3.4/library/__main__.html for explanation
if __name__ == "__main__":
    main_menu()

