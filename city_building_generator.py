import sys
import random
import datetime

city_base_params = []
cities_list = []
city_aggregate_info = []
city_general_wordset = []
word_randomizer_wordset = []

def initialize():
    try:
        word_randomizer_wordset.extend(open("word_list.txt", "r").read().split("\n"))
    except:
        print("ERROR: could not find 'word_list.txt'. Make sure it's in this directory, and it's newline-separated. Continuing...")

    try:
        city_general_wordset.extend(open("city_common_words.txt", "r").read().split("\n"))
    except:
        print("ERROR: could not find 'city_common_words.txt'. Make sure it's in this directory. Continuing...")

    try:
        city_base_params_string = open('city_base_table.txt').read().replace('\n', '$')
    except:
        print("ERROR: could not find 'city_base_table.txt'. Make sure it's in this directory.")

    city_base_params_rows = city_base_params_string.split("$")
    for row in city_base_params_rows:
        city_base_params.append(row.split(", "))

    try:
        if ('city_poplist.txt' or '\\city_poplist.txt' or '\city_poplist.txt') in sys.argv:
            try:
                cities_list_string = open('city_poplist.txt').read().replace('\n', '$')
                cities_list_rows = cities_list_string.split("$")
                for row in cities_list_rows:
                    cities_list.append((row.split(", ")[0], row.split(", ")[1]))
            except:
                print("ERROR: could not find 'city_poplist.txt'. Make sure it's in this directory.")
        else:
            city_size = sys.argv[1]
            if city_size.isnumeric():
                city_size = city_base_params[6 - int(city_size)][0]        
            if len(sys.argv) >= 3:
                city_name = sys.argv[2]
            else:
                city_name = "template city name " + str(random.randint(1, 100))
            cities_list.append((city_name, city_size))
    except:
            print("Usage: python city_building_generator.py [city size] [city name] OR python city_building_generator.py city_poplist.txt")
            #print(sys.exc_info()) 

city_size_number_dict = {
    "Metropolis":5,
    "City":4,
    "Town":3,
    "Village":2,
    "Hamlet":1
}

building_rarity_number_dict = {
    '6':15,
    '5':8,
    '4':7,
    '3':4,
    '2':3,
    '1':1
}

"""
    takes in building_type for making name / NPC / quirk and making the building itself
    takes in city_name for name / NPC
    takes in list_of_related_words for name / NPC, default is []

    returns a building, a tuple with these values:
        building name, NPC name (optional), quirk (optional) (TODO)
"""
def make_building(building_type, city_name):
    # get the list of words for building_type and city_name
    building_type_words = []
    city_name_words = []
    try:
        building_type_words_all = open('building_list.txt').read().split('\n')
        for row in building_type_words_all:
            if row.split(", ")[0] == building_type:
                building_type_words = row.split(", ")[1:]
        
        if building_type_words == []:
            print("Could not find a building type of " + str(building_type) + ". Continuing...")
    except:
        print("ERROR: Could not access 'building_list.txt'. Make sure it's in the directory.")

    try: 
        city_name_words_all = open('city_list.txt').read().split('\n')
        for row in city_name_words_all:
            if row[0] == city_name:
                city_name_words = row.split(", ")[1:]

        if city_name_words == []:
            print("Could not find a city name of " + str(city_name) + ". Continuing...")
    except:
        print("ERROR: Could not access 'city_list.txt'. Make sure it's in the directory.")


    # make the name (uses building_type, city_name, list_of_related_words)
    building_name = "Default: " + str(city_name) + " " + str(building_type)
    total_words_list = []
    total_words_list.extend(building_type_words)
    total_words_list.extend(city_name_words)
    total_words_list.extend(city_general_wordset)
    total_words_list.extend(word_randomizer_wordset)
    if len(total_words_list) > 3:
        # we can actually make a name
        list_of_candidate_names = produce_words(word_list = total_words_list, number_of_words=20).split('\n')
        building_name = str(list_of_candidate_names[random.randint(0, len(list_of_candidate_names) - 1)])
    
    #print("started a building named: " + str(building_name)) 


    # make an NPC (uses code lifted from word_randomizer)
    list_of_candidate_names = produce_words(word_list = word_randomizer_wordset, number_of_words=50).split('\n')
    npc_name = list_of_candidate_names[random.randint(0, len(list_of_candidate_names) - 1)] + " " + list_of_candidate_names[random.randint(0, len(list_of_candidate_names) - 1)]

    #print("the relevant NPC for " + str(building_name) + " is: " + str(npc_name))

    # make a quirk
    quirk = "Not implemented yet."
    # for specialty stores, pick which specialty they are
    if building_type == "Specialty Store":
        list_of_specialties = [("Arcane", 1), ("Fletcher", 3), ("Machinery", 2), ("Armory", 4), ("Weapons", 4), ("Divining", 2), ("Curiosities", 3), ("Music", 3), ("Botany", 2), ("Cartography", 2), ("Fishing", 2), ("Butcher", 3)]
        quirk = weighted_average_pick(list_of_specialties)

    # for forts, pick whether they have walls, and are in the city
    if building_type == "Fort":
        has_walls = [("Walls", 2), ("No Walls", 3)]
        quirk = weighted_average_pick(has_walls) + ", "
        in_city = [("In City", 1), ("Outside City", 4)]
        quirk = quirk + weighted_average_pick(in_city)

    # for schools, pick which type of school they are
    if building_type == "School":
        list_of_schools = [("Wizards", 1), ("Bards", 3), ("Divinity", 4), ("Culinary", 2), ("Trade", 3), ("Military", 4), ("General", 10)]
        quirk = weighted_average_pick(list_of_schools)

    # for jails, pick whether they are in the city, and if they are a sanitarium
    if building_type == "Jail":
        is_sanitarium = [("Is Sanitarium", 2), ("Is General Prison", 3)]
        quirk = weighted_average_pick(is_sanitarium) + ", "
        in_city = [("In City", 1), ("Outside City", 4)]
        quirk = quirk + weighted_average_pick(in_city)

    # for churches, pick who they serve
    if building_type == "Church":
        list_of_gods = [("Regeli", 2), ("Cavaris", 1), ("Sentris", 5), ("Liihos", 10), ("Entono", 2), ("Hjelles", 4), ("Leoden", 5), ("Merkand", 2), ("Hadheb", 1), ("Epsa", 10), ("Raimondo", 4), ("Talshem", 3), ("Bekeras", 7), ("Noctsia", 4), ("Petgeg", 6), ("Grena", 5), ("Cardonia", 2), ("Donnef", 7), ("Halda", 3)]
        quirk = weighted_average_pick(list_of_gods)

    # for guild halls, pick which type of guild
    if building_type == "Guild Hall":
        list_of_guilds = [("Artisan", 6), ("Adventuring", 3), ("Hunters", 4), ("Mercenary", 1), ("Thieves", 2), ("Engineers", 1)]
        quirk = weighted_average_pick(list_of_guilds)

    # compile and return the building
    return (building_type, building_name, npc_name, quirk)

def weighted_average_pick(list_of_selections_with_weights):
    total_num = 0
    for item in list_of_selections_with_weights:
        total_num = total_num + item[1]
    
    random_selection = random.randint(0, total_num)
    for item in list_of_selections_with_weights:
        if item[1] >= random_selection:
            return item[0]
        else:
            random_selection = random_selection - item[1]
    
    return "ERROR"


def process_city(city):
    #print(city)

    city_individual_info = {
        "name":None,
        "size":None,
        "num_buildings":None,
        "buildings": [()]
    }
    city_individual_info["name"] = city[0]
    city_individual_info["size"] = city[1]

    relevant_row = city_base_params[6-int(city_size_number_dict[city_individual_info["size"]])]
    city_individual_info["num_buildings"] = int(relevant_row[3])
    #print (relevant_row)

    """
        Okay, so what happens now?
        1: For each 'required' building (that's sixes and fives), we add 1 building of that type
        2: For each 'multiple' building (that's sixes), we add 1 building of that type
        3: For each remaining building, we randomly pick a value based on the rarity-mix, and add a building based on that value 
            (for now, it's a table from 1-6 based on likelihood, and then a series of decimal numbers)
            (for now, 'likely' has the same weight as 'guaranteed' and 'multiple', and 'common' is not much further down)
            (for now, 'unlikely' and 'rare' are really unlikely)
        4: Once we've added every building, we add that city to city_aggregate_info

        Okay, so what's in a building?
        1: Building type (this is the first row of the city_base_params)
        2: (optional) building name-    maybe we can hook in the word_randomizer for names?
                                        maybe we can hook in a table of common words for building types?
        3: (optional) relevant NPC-     this one could also be a task for the word_randomizer
                                        we could maybe randomly generate a race for the NPC and grab NPC names too from a randomizer
        4: (optional) quirk-            especially for taverns and specialty stores, this could add flavor without having to do the hard brain-work
    """

    # handle 'required' buildings (sixes and fives)
    # part 1 and 2: add a building for sixes and fives
    buildings_built = 0
    for i in range(4, len(relevant_row)):
        print("About to check: " + str(relevant_row[i]))
        ### WARNING: This depends on (1) minimum and maximum population never being below 7, and (2) number of buildings never being below 7.
        if relevant_row[i].isnumeric() and int(relevant_row[i]) <= 6:

            # found a rarity indicator
            building_type = city_base_params[0][i]
            city_name = city_individual_info["name"]

            if int(relevant_row[i]) >= 5:
                city_individual_info["buildings"].append(make_building(building_type, city_name))
                buildings_built = buildings_built + 1

            if int(relevant_row[i]) == 6:
                city_individual_info["buildings"].append(make_building(building_type, city_name))
                buildings_built = buildings_built + 1


    # part 3: figure out what to do for the rest of the buildings
    building_rankings = relevant_row[4:]
    building_types = city_base_params[0][4:]
    total_points = 0
    for ranking in building_rankings:
        total_points = total_points + building_rarity_number_dict[ranking]
    
    for times in range(buildings_built, int(relevant_row[3])):
        random_choice = random.randint(0, total_points - 1)
        for i in range(len(building_types)):
            if random_choice < building_rarity_number_dict[building_rankings[i]]:
                city_individual_info["buildings"].append(make_building(building_types[i], city_name))
                break
            else:
                random_choice = random_choice - building_rarity_number_dict[building_rankings[i]]

    city_aggregate_info.append(city_individual_info)

def print_city(city, format='none'):
    format_string = ',' if format == 'csv' else '\t'
    """
    Here's what I want to print for a city (keep in mind I already have name and that big block available):
    MAX NPC NAME SIZE IS 23 chars
    MAX BUILDING NAME SIZE IS <16 chars
    TAB SIZE IS 4 spaces
    WE CAN FORMAT THIS AS A NICE TABLE

    CITY NAME
    CITY SIZE

    TABLE
    _________
    BUILDING_TYPE   |   BUILDING_NAME   |   NPC_NAME    |   QUIRK
      ...
    until out of buildings
    """

    city_string = "\n" + city["name"] + "\n" + city["size"] + "\n\n"
    city_string = city_string + space_format("Index", 6) + format_string + space_format("Building Type", 25) + format_string + space_format("Building Name", 25) + format_string + space_format("NPC Name", 25) + format_string + space_format("Quirk", 25)
    index = 1
    for building in city["buildings"]:
        if len(building) >= 3:
            building_string = "\n" + space_format(str(index), 6) + format_string + space_format(building[0], 25) + format_string + space_format(building[1], 25) + format_string + space_format(building[2], 25) + format_string + space_format(building[3], 25)
            city_string = city_string + building_string
            index = index + 1
    
    return city_string

def space_format(input, length_of_line):
    if len(input) > length_of_line:
        return input
    
    while len(input) < length_of_line:
        input = input + " "

    return str(input)
    
# word list is either a big string or a list of words
# cloned from word-randomizer
def produce_words(word_list, number_of_words = 10):
    string_input = ""
    if type(word_list) == list:
        for word in word_list:
            string_input = string_input + word
    else:
        string_input = word_list

    vowel_list = ""
    consonant_list = ""
    for c in string_input.lower():
        if c in ['', ' ', '\n', '\t']:
            continue
        elif c in ['a', 'e', 'i', 'o', 'u']:
            vowel_list = vowel_list + c
        else:
            consonant_list = consonant_list + c
    
    format_strings = ['011010', '01011010100', '010110', '000101', '01010010', '001010010', '000101', '01010010', '001010010', '010101010']

    total_output = ""
    for j in range(number_of_words):
        # make a random word
        out = ""

        format_string = format_strings[random.randint(0, len(format_strings) - 1)]

        for char in range(len(format_string)):
            if format_string[char] == "0":
                # pick consonant
                out = out + consonant_list[random.randint(0, len(consonant_list) - 1)]
            else:
                # pick vowel
                out = out + vowel_list[random.randint(0, len(vowel_list) - 1)]
        
        total_output = total_output + out + '\n'
    return total_output


def main():
    initialize()

    for city in cities_list:
        process_city(city)

    city_output = "Output of city_building_generator.py run at " + str(datetime.datetime.now()) + ".\n"
    num_buildings_per_type = []
    for i in range(4, len(city_base_params[0])):
        num_buildings_per_type.append(0)
        building_type = city_base_params[0][i]
        for city in city_aggregate_info:
            for building in city["buildings"]:
                if len(building) >= 3:
                    if building[0] == building_type:
                        num_buildings_per_type[i-4] = num_buildings_per_type[i-4] + 1
        city_output = city_output + "There are " + str(num_buildings_per_type[i-4]) + " " + building_type + " buildings.\n"

    city_output = city_output + "\n\n\n"

    for city in city_aggregate_info:
        city_output = city_output + print_city(city, 'csv')
        city_output = city_output + "\n\n\n"

    filename = "output_file2.csv"
    if len(sys.argv) > 2:
        filename = sys.argv[2]

    outfile = None
    try:
        outfile = open(filename, "x")
    except:
        outfile = open(filename, "w")
    
    outfile.write(city_output)

main()