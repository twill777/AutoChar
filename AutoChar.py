import os
import pdfrw
from random import randint
import pandas as pd
import math

char_sheet_template_path = '5E_CharacterSheet_PyScript.pdf'
char_sheet_output_path = 'Random_Character.pdf'
char_info_excel_path = 'Char_Info.xlsx'

df_armor = pd.read_excel(char_info_excel_path, sheet_name="Armor")
df_races = pd.read_excel(char_info_excel_path, sheet_name="Races")
df_subraces = pd.read_excel(char_info_excel_path, sheet_name="Player Subraces")
df_simple_weapons = pd.read_excel(char_info_excel_path, sheet_name="Simple Weapons")
df_martial_weapons = pd.read_excel(char_info_excel_path, sheet_name="Martial Weapons")
df_backgrounds = pd.read_excel(char_info_excel_path, sheet_name="Player Backgrounds")


ANNOT_KEY = '/Annots'
ANNOT_FIELD_KEY = '/T'
ANNOT_VAL_KEY = '/V'
ANNOT_RECT_KEY = '/Rect'
SUBTYPE_KEY = '/Subtype'
WIDGET_SUBTYPE_KEY = '/Widget'


def write_fillable_pdf(input_pdf_path, output_pdf_path, text_dict, check_dict, skill_prof_dict):
    template_pdf = pdfrw.PdfReader(input_pdf_path)
    annotations = template_pdf.pages[0][ANNOT_KEY]
    for annotation in annotations:
        if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
            if annotation[ANNOT_FIELD_KEY]:
                key = annotation[ANNOT_FIELD_KEY][1:-1]
                if key in text_dict.keys():
                    annotation.update(
                        pdfrw.PdfDict(V='{}'.format(text_dict[key]))
                    )
                    annotation.update(pdfrw.PdfDict(AP=''))
                if key in skill_mod_dict.keys():
                    annotation.update(
                        pdfrw.PdfDict(V='{}'.format(skill_mod_dict[key]))
                    )
                    annotation.update(pdfrw.PdfDict(AP=''))
                if key in check_dict.keys():
                    annotation.update(
                        pdfrw.PdfDict(V='{}'.format(check_dict[key]))
                    )
                    annotation.update(pdfrw.PdfDict(AS=pdfrw.PdfName('Yes')))
                if key in skill_prof_dict.keys():
                    annotation.update(
                        pdfrw.PdfDict(V='{}'.format(skill_prof_dict[key]))
                    )
                    annotation.update(pdfrw.PdfDict(AS=pdfrw.PdfName('Yes')))
    pdfrw.PdfWriter().write(output_pdf_path, template_pdf)


def get_random_level():
    level = randint(1, 20)

    return str(level)


def listString(comma_list):
    if comma_list != comma_list:
        return []
    if comma_list == 1:
        return [comma_list]
    return comma_list.split(',')


def get_random_player_class(player_classes):
    player_class = player_classes[randint(0, len(player_classes) - 1)]

    return player_class


def get_random_race(player_races):
    race = player_races[randint(0, len(player_races) - 1)]

    return race


def get_random_background(player_backgrounds):
    background = player_backgrounds[randint(0, len(player_backgrounds) - 1)]

    return background


def get_alignment_num(race):
    alignment_pref = race.alignment_pref

    alignment_1 = [randint(1, 3), randint(1, 3)]
    alignment_2 = [randint(1, 3), randint(1, 3)]

    alignment_1_pref = check_if_in_list(alignment_pref[0], alignment_1)\
                       + check_if_in_list(alignment_pref[1], alignment_1)
    alignment_2_pref = check_if_in_list(alignment_pref[0],alignment_2)\
                       + check_if_in_list(alignment_pref[1], alignment_2)

    if alignment_1_pref >= alignment_2_pref:
        alignment = alignment_1
    else:
        alignment = alignment_2

    return alignment


def get_alignment(alignment_num):
    alignment = ''

    if alignment_num[0] == 2 and alignment_num[1] == 2:
        alignment = 'True Neutral'
    else:
        if alignment_num[0] == 1:
            alignment += 'Lawful '
        elif alignment_num[0] == 2:
            alignment += 'Neutral '
        elif alignment_num[0] == 3:
            alignment += 'Chaotic '
        else:
            alignment += 'Failed '

        if alignment_num[1] == 1:
            alignment += 'Good'
        elif alignment_num[1] == 2:
            alignment += 'Neutral'
        elif alignment_num[1] == 3:
            alignment += 'Evil'
        else:
            alignment += 'Failed'

    return alignment


def roll_stats(char_class, char_race):
    stats = [roll_stat(), roll_stat(), roll_stat(), roll_stat(), roll_stat(), roll_stat()]
    new_stats = [0, 0, 0, 0, 0, 0]

    pref_stats = char_class.pref_stats
    dump_stats = char_class.dump_stats

    highest = max(stats)
    stats.remove(highest)

    for i in range(2):
        try:
            highest_pos = pref_stats.index(2 - i)
            pref_stats[highest_pos] = -1

            try:
                other_highest_pos = pref_stats.index(2 - i)

                coin = randint(0, 1)
                if coin == 1:
                    highest_pos = other_highest_pos

                pref_stats[other_highest_pos] = -1
            except:
                highest_pos = highest_pos
        except:
            highest_pos = -1

        if highest_pos >= 0:
            new_stats[highest_pos] = highest
            if i == 0:
                highest = max(stats)
                stats.remove(highest)

    for i in range(2):
        lowest_pos = []
        done = False
        while done == False:
            try:
                lowest_pos.append(dump_stats.index(2 - i))
                dump_stats[dump_stats.index(2 - i)] = -1
            except:
                lowest_pos = lowest_pos
                done = True

        lowest_stats = []
        for pos in lowest_pos:
            lowest_stats.append(min(stats))
            stats.remove(min(stats))

        for pos in lowest_pos:
            rand_pos = len(lowest_stats) - 1
            new_stats[pos] = lowest_stats[randint(0, rand_pos)]
            lowest_stats.remove(new_stats[pos])

    for stat in stats:
        if stat > 0:
            new_pos = randint(0, 5)
            while new_stats[new_pos] > 0:
                new_pos = randint(0, 5)
            new_stats[new_pos] = stat

    for i in range(len(new_stats)):
        new_stats[i] += char_race.bonuses[i]

    bonuses_given = []
    for i in range(char_race.rand_bonuses):
        bonus_pos = randint(0, 5)
        while char_class.dump_stats[bonus_pos] != 0 and not check_if_in_list(bonus_pos, bonuses_given):
            bonus_pos = randint(0, 5)
        new_stats[bonus_pos] += 1
        bonuses_given.append(bonus_pos)

    return [str(item) for item in new_stats]


def check_if_in_list(val, list):
    try:
        list.index(val)
        return True
    except:
        return False


def roll_stat():
    rolls = [randint(1, 6), randint(1, 6), randint(1, 6), randint(1, 6)]

    return sum(rolls) - min(rolls)


def get_modifier(stats):
    mods = []

    for stat in stats:
        stat = int(stat)
        mods.append(str(math.floor((stat / 2) - 5)))

    for i in range(len(mods)):
        if math.floor(float(mods[i])) >= 0:
            mods[i] = '+' + mods[i]

    return mods


def get_prof_bonus(level):
    prof_bonus = char_class.prof_bonuses[int(level) - 1]

    return '+' + str(prof_bonus)


def get_saves(char_class, prof_bonus, modifiers):
    saves = []

    for i in range(6):
        saves.append(math.floor(float(modifiers[i])) + (int(prof_bonus) * char_class.save_profs[i]))
        if saves[i] >= 0:
            saves[i] = '+' + str(saves[i])
        else:
            saves[i] = str(saves[i])

    return saves


def get_save_profs(char_class):
    save_prof_strings = []

    for i in range(6):
        if char_class.save_profs[i] == 1:
            save_prof_strings.append('Yes')
        else:
            save_prof_strings.append('No')

    return save_prof_strings


def get_skill_profs(background, char_class, char_subclass):
    skill_profs_set = []

    for skill_prof in background.skills:
        skill_prof_dict[skill_prof] = 'Yes'
        skill_profs_set.append(skill_prof)

    if len(char_class.skill_prof_options) > 0:
        for i in range(char_class.skill_prof_number):
            random_skill = randint(0, len(char_class.skill_prof_options) - 1)
            while check_if_in_list(char_class.skill_prof_options[random_skill], skill_profs_set) == 1:
                random_skill = randint(0, len(char_class.skill_prof_options) - 1)
            skill_prof_dict[char_class.skill_prof_options[random_skill]] = 'Yes'
            skill_profs_set.append(char_class.skill_prof_options[random_skill])

    else:
        for i in range(char_class.skill_prof_number):
            random_skill = randint(0, len(skill_prof_dict) - 1)
            while check_if_in_list(random_skill, skill_profs_set) == 1:
                random_skill = randint(0, len(skill_prof_dict) - 1)
            skill_prof_dict[list(skill_prof_dict)[random_skill]] = 'Yes'
            skill_profs_set.append(random_skill)

    if char_subclass != 'None':
        for prof in char_subclass.skill_profs:
            if isinstance(prof, list):
                prof_pos = randint(0, len(char_subclass.skill_profs) - 1)
                while check_if_in_list(prof[prof_pos], skill_profs_set) == 1:
                    prof_pos = randint(0, len(char_class.skill_prof_options) - 1)
                skill_prof_dict[prof[prof_pos]] = 'Yes'
                skill_profs_set.append(prof[prof_pos])
            else:
                if check_if_in_list(prof, skill_profs_set) == 0:
                    skill_prof_dict[prof] = 'Yes'
                    skill_profs_set.append(prof)


def get_skill_modifiers(char_class, modifiers, prof_bonus):
    i = 0

    for skill in skill_mod_dict.keys():
        skill_mod_dict[skill] = modifiers[char_class.skill_abilities[i]]

        if skill_prof_dict[skill + '_prof'] == 'Yes':
            skill_mod_dict[skill] = math.floor(float(skill_mod_dict[skill])) + int(prof_bonus)
            if skill_mod_dict[skill] >= 0:
                skill_mod_dict[skill] = '+' + str(skill_mod_dict[skill])

        skill_mod_dict[skill] = str(skill_mod_dict[skill])

        i += 1


def get_languages(race, char_class):
    racial_class_languages = [race.languages, char_class.languages]

    languages = ''
    languages_list = []
    first = True

    for i in range(2):
        for language in racial_class_languages[i]:
            if not first:
                languages += ', '
            else:
                first = False
            if language == 'Any':
                random_language = randint(0, len(all_languages) - 1)
                while check_if_in_list(all_languages[random_language], languages_list) == 1\
                        or check_if_in_list(all_languages[random_language], racial_class_languages[0]) == 1\
                        or check_if_in_list(all_languages[random_language], racial_class_languages[1]) == 1:
                    random_language = randint(0, len(all_languages) - 1)
                languages += all_languages[random_language]
                languages_list.append(all_languages[random_language])
            else:
                languages += language
                languages_list.append(language)

    return languages


def get_weapon_attack_bonuses(weapons, modifiers, weapon_profs, prof_bonus):
    attack_mods = []

    for weapon in weapons:
        if weapon.name == '':
            attack_mods.append('')
        else:
            if len(weapon.stats_used) == 1:
                attack_mods.append(modifiers[weapon.stats_used[0]])

            else:
                if modifiers[0] > modifiers[1]:
                    attack_mods.append(modifiers[0])
                else:
                    attack_mods.append(modifiers[1])

    for i in range(len(weapons)):
        if check_if_in_list(weapons[i].name + 's', weapon_profs) == 1 \
                or check_if_in_list(weapons[i].skill + 's', weapon_profs) == 1:
            attack_mods[i] = str(math.floor(float(attack_mods[i])) + int(prof_bonus))
            if math.floor(float(attack_mods[i])) >= 0:
                attack_mods[i] = '+' + attack_mods[i]

    return attack_mods


def get_weapon_damage_bonuses(weapons, modifiers):
    damage_mods = []

    for weapon in weapons:
        if weapon.name == '' or weapon.name == 'Net':
            damage_mods.append('')
        else:
            if len(weapon.stats_used) == 1:
                damage_mods.append(modifiers[weapon.stats_used[0]])

            else:
                if modifiers[0] > modifiers[1]:
                    damage_mods.append(modifiers[0])
                else:
                    damage_mods.append(modifiers[1])

    return damage_mods


def get_equipment_list(equipment):
    equipment_list = ''

    for item in equipment:
        equipment_list += item + '\n'

    return equipment_list


def get_weapon_equipment_text(weapon):
    equipment_text = ''

    if weapon.name != '':
        equipment_text += weapon.name

        equipment_text += ' ['
        for trait in weapon.traits:
            equipment_text += trait
            equipment_text += ', '

        equipment_text += weapon.attack_type
        equipment_text += ']'

    return equipment_text


def get_weapon_profs(char_class, char_race, char_background):
    weapon_profs = []

    for prof in char_class.weapon_profs:
        if check_if_in_list(prof, weapon_profs) == 0:
            weapon_profs.append(prof)

    for prof in char_race.weapon_profs:
        if isinstance(prof, list):
            rand_pos = randint(0, len(prof) - 1)
            if check_if_in_list(prof[rand_pos], weapon_profs) == 0:
                weapon_profs.append(prof[rand_pos])
        else:
            if check_if_in_list(prof, weapon_profs) == 0:
                weapon_profs.append(prof)

    for prof in char_background.weapon_profs:
        if isinstance(prof, list):
            rand_pos = randint(0, len(prof) - 1)
            if check_if_in_list(prof[rand_pos], weapon_profs) == 0:
                weapon_profs.append(prof[rand_pos])
        else:
            if check_if_in_list(prof, weapon_profs) == 0:
                weapon_profs.append(prof)

    return weapon_profs


def get_other_profs(char_class, char_background, char_race, artisans_tools, instruments, game_list):
    other_profs = []

    for prof in char_class.other_profs:
        if isinstance(prof, list):
            prof = prof[randint(0, len(prof) - 1)]
            while isinstance(prof, list):
                prof = prof[randint(0, len(prof) - 1)]

        if prof == 'Artisan':
            prof = artisans_tools[randint(0, len(artisan_tools) - 1)]
            while check_if_in_list(prof, other_profs):
                prof = artisans_tools[randint(0, len(artisan_tools) - 1)]

        elif prof == 'Instrument':
            prof = instruments[randint(0, len(instruments) - 1)]
            while check_if_in_list(prof, other_profs):
                prof = instruments[randint(0, len(instruments) - 1)]

        elif prof == 'Gaming':
            prof = game_list[randint(0, len(game_list) - 1)]
            while check_if_in_list(prof, other_profs):
                prof = game_list[randint(0, len(game_list) - 1)]

        other_profs.append(prof)

    for prof in char_race.other_profs:
        if isinstance(prof, list):
            prof = prof[randint(0, len(prof) - 1)]
            while isinstance(prof, list):
                prof = prof[randint(0, len(prof) - 1)]

        if prof == 'Artisan':
            prof = artisan_tools[randint(0, len(artisan_tools) - 1)]
            while check_if_in_list(prof, other_profs):
                prof = artisan_tools[randint(0, len(artisan_tools) - 1)]

        elif prof == 'Instrument':
            prof = instruments[randint(0, len(instruments) - 1)]
            while check_if_in_list(prof, other_profs):
                prof = instruments[randint(0, len(instruments) - 1)]

        elif prof == 'Gaming':
            prof = game_list[randint(0, len(game_list) - 1)]
            while check_if_in_list(prof, other_profs):
                prof = game_list[randint(0, len(game_list) - 1)]

        other_profs.append(prof)

    for prof in char_background.other_profs:
        if isinstance(prof, list):
            prof = prof[randint(0, len(prof) - 1)]
            while isinstance(prof, list):
                prof = prof[randint(0, len(prof) - 1)]

        if prof == 'Artisan':
            prof = artisan_tools[randint(0, len(artisan_tools) - 1)]
            while check_if_in_list(prof, other_profs):
                prof = artisan_tools[randint(0, len(artisan_tools) - 1)]

        elif prof == 'Instrument':
            prof = instruments[randint(0, len(instruments) - 1)]
            while check_if_in_list(prof, other_profs):
                prof = instruments[randint(0, len(instruments) - 1)]

        elif prof == 'Gaming':
            prof = game_list[randint(0, len(game_list) - 1)]
            while check_if_in_list(prof, other_profs):
                prof = game_list[randint(0, len(game_list) - 1)]

        other_profs.append(prof)

    return other_profs


def get_all_profs_and_langs(languages, weapon_profs, other_profs):
    all_profs = ''
    all_profs += languages + '\n'

    weapon_profs_string = ''

    first = True
    for weapon_prof in weapon_profs:
        if not first:
            weapon_profs_string += ', '
        else:
            first = False
        weapon_profs_string += weapon_prof

    all_profs += weapon_profs_string + '\n'

    other_profs_string = ''

    first = True
    for other_prof in other_profs:
        if not first:
            other_profs_string += ', '
        else:
            first = False

        if other_prof not in all_profs:
            other_profs_string += other_prof

    all_profs += other_profs_string + '\n'

    return all_profs


def get_weapons_and_equipment(char_class, weapon_profs, all_weapon_names):
    equipment_options = char_class.starting_equipment_options
    all_equipment_list = []
    weapon_list = []
    equipment_list = []

    for i in range(len(equipment_options[0])):
        random_selection = randint(0, len(equipment_options) - 1)

        proficicent = True
        if 'if prof' in equipment_options[random_selection][i]:
            # print('Checking proficiencies for ' + equipment_options[random_selection][i])
            proficicent = False
            for weapon_prof in weapon_profs:
                if weapon_prof in equipment_options[random_selection][i]:
                    proficicent = True

        while equipment_options[random_selection][i] == 'None' or not proficicent:
            random_selection = randint(0, len(equipment_options) - 1)
            proficicent = True
            if 'if prof' in equipment_options[random_selection][i]:
                # print('Checking proficiencies for ' + equipment_options[random_selection][i])
                proficicent = False
                for weapon_prof in weapon_profs:
                    if weapon_prof in equipment_options[random_selection][i]:
                        proficicent = True

        if 'if prof' in equipment_options[random_selection][i]:
            all_equipment_list.append(equipment_options[random_selection][i][:equipment_options[random_selection][i].
                                      index('if prof') - 1])

        all_equipment_list.append(equipment_options[random_selection][i])

    done = False
    while not done:
        done = True
        for item in all_equipment_list:
            if '&' in item:
                all_equipment_list.remove(item)
                split_pos = item.index('&')
                all_equipment_list.append(item[0:split_pos - 1])
                all_equipment_list.append(item[split_pos+2:len(item)])
                done = False

    all_equipment_list += char_class.starting_equipment_given

    # print(all_equipment_list)
    for item in all_equipment_list:
        is_weapon = False

        for name in all_weapon_names:
            if name in item:
                is_weapon = True

        if is_weapon:
            # print('\t' + item + ' is a weapon')
            if '*' in item:
                weapon_name = item[0:item.index('*') - 1]
                multiple_num = item[item.index('*') - 1:]
                multiple = True
                # print('\t\t' + weapon_name + ' has' + multiple_num + ' instances')
            else:
                weapon_name = item
                multiple = False
                # print('\t\t' + weapon_name + ' is alone')
            weapon_found = False
            for weapon in simple_weapons:
                if not weapon_found and weapon.name == weapon_name:
                    # print('\t\t' + weapon_name + ' was found as a simple weapon')
                    weapon_found = True
                    new_item = weapon
            if not weapon_found:
                for weapon in martial_weapons:
                    if not weapon_found and weapon.name == weapon_name:
                        # print('\t\t' + weapon_name + ' was found as a martial weapon')
                        weapon_found = True
                        new_item = weapon
            if multiple:
                new_item.name += multiple_num

            in_list = False
            for weapon in weapon_list:
                if weapon.name in new_item.name:
                    in_list = True
            if not in_list:
                weapon_list.append(new_item)
            equipment_list.append(get_weapon_equipment_text(new_item))

        elif 'Simple Weapon' in item:
            # print('\t' + item + ' is a random Simple Weapon')
            new_item = simple_weapons[randint(0, len(simple_weapons) - 1)]
            if 'is melee' in item:
                while 'melee' not in new_item.attack_type:
                    # print('\t\t' + new_item.name + ' is not a melee Simple Weapon')
                    new_item = simple_weapons[randint(0, len(simple_weapons) - 1)]
                # print('\t\t' + new_item.name + ' is a melee Simple Weapon')
            if '*' in item:
                new_item.name += item[item.index('*') - 1:]

            # print('\t\t\t' + new_item.name + ' is a Simple Weapon')

            in_list = False
            for weapon in weapon_list:
                if weapon.name in new_item.name:
                    in_list = True
            if not in_list:
                weapon_list.append(new_item)
            equipment_list.append(get_weapon_equipment_text(new_item))

        elif 'Martial Weapon' in item:
            # print('\t' + item + ' is a random Martial Weapon')
            new_item = martial_weapons[randint(0, len(martial_weapons) - 1)]
            if 'is melee' in item:
                while 'melee' not in new_item.attack_type:
                    # print('\t\t' + new_item.name + ' is not a melee Martial Weapon')
                    new_item = martial_weapons[randint(0, len(martial_weapons) - 1)]
                # print('\t\t' + new_item.name + ' is a melee Martial Weapon')
            if '*' in item:
                new_item.name += item[item.index('*') - 1:]

            # print('\t\t\t' + new_item.name + ' is a Martial Weapon')

            in_list = False
            for weapon in weapon_list:
                if weapon.name in new_item.name:
                    in_list = True
            if not in_list:
                weapon_list.append(new_item)
            equipment_list.append(get_weapon_equipment_text(new_item))
        else:
            # print('\t' + item + " is not a weapon")
            equipment_list.append(item)

    return [weapon_list, equipment_list]


def get_armor_class(equipment_list, armor_list, stats, modifiers, race):
    ac = 10 + math.floor(float(modifiers[1]))

    armored = False
    for armor in armor_list:
        if armor.name in equipment_list:
            armored = True
            armor_worn = armor

    if armored:
        if math.floor(float(stats[0])) >= armor_worn.min_strength:
            ac = armor_worn.base_ac_bonus
            if armor_worn.max_dex_bonus < math.floor(float(modifiers[1])):
                ac += armor_worn.max_dex_bonus
            else:
                ac += math.floor(float(modifiers[1]))

    if 'Shield' in equipment_list:
        ac += 2

    return ac


def sort_equipment_list(current_equipment_list):
    new_equipment_list = ''
    list_of_equipment = []

    while '\n' in current_equipment_list:
        list_of_equipment.append(current_equipment_list[:current_equipment_list.index('\n')])
        current_equipment_list = current_equipment_list[current_equipment_list.index('\n') + 1:]

    list_of_equipment.sort()

    for item in list_of_equipment:
        new_equipment_list += item + '\n'

    return new_equipment_list


def get_name(name_list, last_name_1_list, last_name_2_list, consonant_list, vowel_list, midset_list, cannot_end_name,
             cannot_start_name):
    first_name = ''
    last_name = ''

    first_name = get_first_name(name_list, consonant_list, vowel_list, cannot_end_name, cannot_start_name)

    longer_name = randint(1, 6)

    while longer_name == 1:
        first_name += ' ' + get_first_name(name_list, consonant_list, vowel_list, cannot_end_name, cannot_start_name)
        longer_name = randint(1, 6)

    name_connector = randint(1, 6)

    if name_connector == 1:
        midset_pos = randint(0, len(midset_list) - 1)
        first_name += ' ' + midset_list[midset_pos]

    last_name_1_pos = randint(0, len(last_name_1_list) - 1)
    last_name_2_pos = randint(0, len(last_name_2_list) - 1)

    last_name = last_name_1_list[last_name_1_pos] + last_name_2_list[last_name_2_pos]

    # print(first_name + ' ' + last_name)

    return first_name + ' ' + last_name


def get_first_name(name_list, consonant_list, vowel_list, cannot_end_name, cannot_start_name):
    first_name = ''

    which_name = randint(1, 7)

    if which_name == 1:
        first_name_pos = randint(0, len(name_list) - 1)
        first_name = name_list[first_name_pos]
    else:
        if which_name > 4:
            which_name -= 3
        which_name += 1
        vowel = False
        start_vowel = randint(0, 1)
        if start_vowel == 0:
            vowel = True

        for i in range(which_name):
            if vowel:
                randpos = randint(0, len(vowel_list) - 1)
                while (check_if_in_list(vowel_list[randpos], cannot_start_name) and i == 0)\
                        or (check_if_in_list(vowel_list[randpos], cannot_end_name) and i == which_name - 1):
                    randpos = randint(0, len(vowel_list) - 1)
                first_name += vowel_list[randpos]
            else:
                randpos = randint(0, len(consonant_list) - 1)
                while (check_if_in_list(consonant_list[randpos], cannot_start_name) and i == 0) \
                        or (check_if_in_list(consonant_list[randpos], cannot_end_name) and i == which_name - 1):
                    randpos = randint(0, len(vowel_list) - 1)
                first_name += consonant_list[randpos]
            vowel = not vowel

    return first_name.capitalize()


def get_attack_list(char_subclass, char_level):
    attack_list = []

    for attack in char_subclass.attack_list:
        if int(char_level) >= int(attack[1]):
            attack_list.append(attack[0])
            if len(attack) == 3:
                attack_list.remove(attack[2])

    return attack_list


def get_attack_string(attack_list):
    attack_string = ''

    for attack in attack_list:
        attack_string += attack + '\n'

    return attack_string


def get_passive_list(char_subclass, char_level):
    passive_list = []

    for passive in char_subclass.passive_list:
        if int(char_level) >= int(passive[1]):
            passive_list.append(passive[0])
            if len(passive) == 3:
                passive_list.remove(passive[2])

    return passive_list


def get_passive_string(passive_list):
    passive_string = ''

    for passive in passive_list:
        passive_string += passive + '\n'

    return passive_string


class PlayerClass:
    def __init__(self, name, pref_stats, dump_stats, save_profs, skill_prof_options, skill_prof_number, languages,
                 weapon_profs, starting_equipment_options, starting_equipment_given, other_profs, subclass_level,
                 attack_list, passive_list):
        self.name = name
        self.pref_stats = pref_stats
        self.dump_stats = dump_stats
        self.prof_bonuses = [2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6]
        self.skill_abilities = [1, 4, 3, 0, 5, 3, 4, 5, 3, 4, 3, 4, 5, 5, 3, 2, 2, 4]
        self.save_profs = save_profs
        self.skill_prof_options = skill_prof_options
        self.skill_prof_number = skill_prof_number
        self.languages = languages
        self.weapon_profs = weapon_profs
        self.starting_equipment_options = starting_equipment_options
        self.starting_equipment_given = starting_equipment_given
        self.other_profs = other_profs
        self.subclass_level = subclass_level
        self.attack_list = attack_list
        self.passive_list = passive_list

    def setSubclasses(self, subclasses):
        self.subclasses = subclasses

    def getSubclass(self, subclass_pos):
        return self.subclasses[subclass_pos]

    def pickSubclass(self, char_level):
        if int(char_level) >= int(self.subclass_level):
            subclass_pos = randint(0, len(self.subclasses) - 1)
            self.name = self.subclasses[subclass_pos].name
            return self.subclasses[subclass_pos]
        else:
            return 'None'


class PlayerSubClass:
    def __init__(self, parentClass, name, languages, weapon_profs, skill_profs, other_profs, attack_list, passive_list):
        self.parentClass = parentClass
        self.name = name
        parentClass.languages += languages
        parentClass.weapon_profs += weapon_profs
        self.skill_profs = skill_profs
        parentClass.other_profs += other_profs
        self.attack_list = parentClass.attack_list + attack_list
        self.passive_list = parentClass.passive_list + passive_list


class PlayerRace:
    def __init__(self, name, bonuses, rand_bonuses, languages, weapon_profs, other_profs):
        self.name = name
        self.bonuses = bonuses
        self.rand_bonuses = rand_bonuses
        self.languages = languages
        self.weapon_profs = weapon_profs
        self.other_profs = other_profs

    def setSubraces(self, subraces):
        self.subraces = subraces

    def pickSubrace(self):
        race_pos = randint(0, len(self.subraces) - 1)
        return self.subraces[race_pos]


class PlayerSubRace:
    def __init__(self, parentClass, name, bonuses, languages, weapon_profs, other_profs, alignment_pref):
        self.bonuses = []
        for i in range(len(parentClass.bonuses)):
            self.bonuses.append(parentClass.bonuses[i] + int(bonuses[i]))
        self.bonuses = parentClass.bonuses
        self.rand_bonuses = parentClass.rand_bonuses
        self.alignment_pref = alignment_pref
        self.languages = parentClass.languages + languages
        self.weapon_profs = parentClass.weapon_profs + weapon_profs
        self.other_profs = parentClass.other_profs + other_profs
        self.name = name


class PlayerBackground:
    def __init__(self, name, skills, other_profs, weapon_profs):
        self.name = name
        self.skills = skills
        self.other_profs = other_profs
        self.weapon_profs = weapon_profs


class Weapon:
    def __init__(self, name, damage, traits, attack_type, damage_type, cost, weight, skill):
        self.name = name
        self.damage = damage
        self.traits = traits
        self.attack_type = attack_type
        self.damage_type = damage_type
        self.cost = cost
        self.weight = weight
        self.skill = skill

        if check_if_in_list('finesse', traits) == 1:
            self.stats_used = [0, 1]
        elif 'ranged' in attack_type:
            self.stats_used = [1]
        else:
            self.stats_used = [0]


class Die:
    def __init__(self, name):
        self.name = name
        if name == '':
            self.max = 0
            self.num_rolls = 0
        elif name == 1:
            self.max = 1
            self.num_rolls = 1
        elif check_if_in_list('d', list(name)) == 0:
            self.max = int(name)
            self.num_rolls = 0
        elif name[0] == 'd':
            self.max = int(name[1 : len(name)])
            self.num_rolls = 1
        else:
            index_d = name.index('d')
            self.max = int(name[index_d + 1 : len(name)])
            self.num_rolls = int(name[0:index_d])

    def roll(self):
        sum = 0

        if self.num_rolls == 0:
            sum = self.max

        else:
            for i in range(self.num_rolls):
                sum += randint(0, self.max)

        return sum


class Armor:
    def __init__(self, name, base_ac_bonus, max_dex_bonus, min_strength, armor_level):
        self.name = name
        self.base_ac_bonus = base_ac_bonus
        self.max_dex_bonus = max_dex_bonus
        self.min_strength = min_strength
        self.armor_level = armor_level



player_classes = [
    PlayerClass('Barbarian', [2, 0, 1, 0, 0, 0], [0, 0, 0, 2, 1, 1], [1, 0, 1, 0, 0, 0],
                 ['animal_handling_prof', 'athletics_prof', 'intimidation_prof', 'nature_prof', 'perception_prof',
                  'survival_prof'], 2, [],
                 ['Simple Weapons', 'Martial Weapons'],
                 [['Greataxe', 'Handaxe & Handaxe'],
                 ['Martial Weapon is melee', 'Simple Weapon']],
                 ["Explorer's Pack", 'Javelin * 4'],
                ['Light Armor', 'Medium Armor', 'Shields'], 3,
                [['Rage', 1], ['Reckless Attack', 2], ['Extra Attack', 5], ['Fast Movement', 5],
                 ['Brutal Critical', 9]],
                [['Unarmored Defense', 1], ['Danger Sense', 2], ['Feral Instinct', 7], ['Relentless Rage', 11],
                 ['Persistent Rage', 15], ['Indomitable Might', 18], ['Primal Champion', 20], ['ASI', 4],
                 ['ASI * 2', 8, 'ASI'], ['ASI * 3', 12, 'ASI * 2'], ['ASI * 4', 16, 'ASI * 3'],
                 ['ASI * 5', 19, 'ASI * 4']]),
    PlayerClass('Bard', [0, 1, 0, 0, 0, 2], [0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 1],
                 [], 3, [],
                 ['Simple Weapons', 'Hand Crossbows', 'Longswords', 'Rapiers', 'Shortswords'],
                 [['Rapier', "Diplomat's Pack"],
                 ['Longsword', "Entertainer's Pack"],
                 ['Simple Weapon', 'None']],
                 ['Instrument', 'Leather Armor', 'Dagger'],
                ['Light Armor', 'Instrument', 'Instrument', 'Instrument'], 3,
                [['Bardic Inspiration', 1], ['Countercharm', 6]],
                [['Jack of All Trades', 2], ['Song of Rest', 2], ['Expertise * 2', 3],
                 ['Expertise * 4', 10, 'Expertise * 2'], ['Font of Inspiration', 5], ['Magical Secrets * 2', 10],
                 ['Magical Secrets * 4', 14, 'Magical Secrets * 2'],
                 ['Magical Secrets * 6', 18, 'Magical Secrets * 4'], ['Superior Inspiration', 20], ['ASI', 4],
                 ['ASI * 2', 8, 'ASI'], ['ASI * 3', 12, 'ASI * 2'], ['ASI * 4', 16, 'ASI * 3'],
                 ['ASI * 5', 19, 'ASI * 4']]),
    PlayerClass('Cleric', [1, 0, 1, 0, 2, 0], [0, 0, 0, 1, 0, 1], [0, 0, 0, 0, 1, 1],
                 ['history_prof', 'insight_prof', 'medicine_prof', 'persuasion_prof', 'religion_prof'], 2, [],
                 ['Simple Weapons'],
                 [['Mace', 'Scale Mail', 'Light Crossbow & Bolt * 20', "Priest's Pack"],
                 ['Warhammer if prof', 'Leather Armor', 'Simple Weapon', "Explorer's Pack"],
                 ['None', 'Chain Mail if prof', 'None', 'None']],
                 ['Shield', 'Holy Symbol'],
                ['Light Armor', 'Medium Armor', 'Shields'], 1,
                [['Channel Divinty: Turn Undead', 2]],
                [['Destroy Undead', 5], ['Divine Intervention', 10], ['ASI', 4], ['ASI * 2', 8, 'ASI'],
                 ['ASI * 3', 12, 'ASI * 2'], ['ASI * 4', 16, 'ASI * 3'], ['ASI * 5', 19, 'ASI * 4']]),
    PlayerClass('Druid', [0, 0, 1, 0, 2, 0], [1, 0, 0, 0, 0, 0], [0, 0, 0, 1, 1, 0],
                 ['arcana_prof', 'animal_handling_prof', 'insight_prof', 'medicine_prof', 'nature_prof',
                  'perception_prof', 'religion_prof', 'survival_prof'], 2, ['Druidic'],
                 ['Clubs', 'Daggers', 'Darts', 'Javelins', 'Maces', 'Quarterstaffs', 'Scimtars', 'Sickles', 'Slings',
                  'Spears'],
                 [['Shield', 'Scimtar'],
                 ['Simple Weapon', 'Simple Weapon']],
                 ['Leather Armor', "Explorer's Pack", 'Druidic Focus'],
                ['Light Armor', 'Medium Armor', 'Shields', 'Herbalism Kit'], 2,
                [['Wild Shape', 2], ['Beast Shapes', 18]],
                [['ASI', 4], ['ASI * 2', 8, 'ASI'], ['ASI * 3', 12, 'ASI * 2'], ['ASI * 4', 16, 'ASI * 3'],
                 ['ASI * 5', 19, 'ASI * 4'], ['Timeless Body', 18], ['Archdruid', 20]]),
    PlayerClass('Fighter', [2, 2, 1, 0, 0, 0], [0, 0, 0, 1, 1, 1], [1, 0, 1, 0, 0, 0],
                 ['acrobatics_prof', 'animal_handling_prof', 'athletics_prof', 'history_prof', 'insight_prof',
                  'intimidation_prof', 'perception_prof', 'survival_prof'], 2, [],
                 ['Simple Weapons', 'Martial Weapons'],
                 [['Chain Mail', 'Martial Weapon & Shield', 'Light Crossbow & Bolt * 20', "Dungeoneer's Pack"],
                 ['Leather Armor & Longbow & Arrow * 20', 'Martial Weapon & Martial Weapon', 'Handaxe & Handaxe', "Explorer's Pack"]],
                 [],
                ['Light Armor', 'Medium Armor', 'Heavy Armor', 'Shields'], 3,
                [['Second Wind', 1], ['Action Surge', 2], ['Extra Attack', 5], ['Extra Attack * 2', 11, 'Extra Attack'],
                 ['Extra Attack * 3', 17, 'Extra Attack * 2'], ['Indomitable', 9],
                 ['Indomitable * 2', 13, 'Indomitable'], ['Indomitable * 3', 17, 'Indomitable * 2']],
                [['ASI', 4], ['ASI * 2', 6, 'ASI'], ['ASI * 3', 8, 'ASI * 2'], ['ASI * 4', 12, 'ASI * 3'],
                 ['ASI * 5', 14, 'ASI * 4'], ['ASI * 6', 18, 'ASI * 5'], ['ASI * 7', 19, 'ASI * 6'],
                 ['Fighting Style', 1]]),
    PlayerClass('Monk', [0, 2, 0, 0, 1, 0], [2, 0, 0, 1, 0, 1], [1, 1, 0, 0, 0, 0],
                 ['acrobatics_prof', 'athletics_prof', 'history_prof', 'insight_prof', 'religion_prof', 'stealth_prof'],
                 2, [],
                 ['Simple Weapons', 'Shortswords'],
                 [['Shortsword', "Dungeoneer's Pack"],
                 ['Simple Weapon', "Explorer's Pack"]],
                 ['Dart * 10'],
                [['Artisan', 'Instrument']], 3,
                [['Martial Arts', 1], ['Unarmored Movement', 2], ['Ki', 2], ['\tFlurry of Blows (1 ki)', 2],
                 ['\tPatient Defense (1 ki)', 2], ['\tStep of the Wind (1 ki)', 2], ['\tStunning Strike (1 ki)', 5],
                 ['\tEmpty Body (4 ki / 8 ki)', 18], ['Deflect Missles', 3], ['Extra Attack', 5], ['Evasion', 7],
                 ['Stillness of Mind', 7]],
                [['ASI', 4], ['ASI * 2', 8, 'ASI'], ['ASI * 3', 12, 'ASI * 2'], ['ASI * 4', 16, 'ASI * 3'],
                 ['ASI * 5', 19, 'ASI * 4'], ['Unarmored Defense', 1], ['Slow Fall', 4],
                 ['Ki-Empowered Strikes', 6], ['Purity of Body', 10], ['Tongue of the Sun and Moon', 13],
                 ['Diamond Soul', 14], ['Timeless Body', 15]]),
    PlayerClass('Paladin', [2, 0, 0, 0, 0, 1], [0, 0, 0, 1, 1, 0], [0, 0, 0, 0, 1, 1],
                 ['athletics_prof', 'insight_prof', 'intimidation_prof', 'medicine_prof', 'persuasion_prof',
                  'religion_prof'], 2, [],
                 ['Simple Weapons', 'Martial Weapons'],
                 [['Martial Weapon & Shield', 'Javelin * 5', "Priest's Pack"],
                 ['Martial Weapon & Martial Weapon', 'Simple Weapon is melee', "Explorer's Pack"]],
                 ['Chain Mail', 'Holy Symbol'],
                ['Light Armor', 'Medium Armor', 'Heavy Armor', 'Shields'], 3,
                [['Divine Smite', 2], ['Extra Attack', 5], ['Cleansing Touch', 14]],
                [['ASI', 4], ['ASI * 2', 8, 'ASI'], ['ASI * 3', 12, 'ASI * 2'], ['ASI * 4', 16, 'ASI * 3'],
                 ['ASI * 5', 19, 'ASI * 4'], ['Divine Sense', 1], ['Lay on Hands (Level * 5)', 1],
                 ['Fighting Style', 1], ['Divine Health', 3], ['Aura of Protection (10 ft)', 6],
                 ['Aura of Protection (30 ft)', 6, 'Aura of Protection (10 ft)'], ['Aura of Courage (10 ft)', 6],
                 ['Aura of Courage (30 ft)', 6, 'Aura of Courage (10 ft)'], ['Improved Divine Smite', 11]]),
    PlayerClass('Ranger', [0, 2, 0, 0, 1, 0], [1, 0, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0],
                 ['animal_handling_prof', 'athletics_prof', 'insight_prof', 'investigation_prof', 'nature_prof',
                  'perception_prof', 'stealth_prof', 'survival_prof'], 2, ['Any'],
                 ['Simple Weapons', 'Martial Weapons'],
                 [['Scale Mail', 'Shortsword & Shortsword', "Dungeoneer's Pack"],
                 ['Leather Armor', 'Simple Weapon is melee & Simple Weapon is melee', "Explorer's Pack"]],
                 ['Longbow', 'Arrow * 20'],
                ['Light Armor', 'Medium Armor', 'Shields'], 3,
                [['Fleet of Foot', 8], ['Hide in Plain Sight', 10], ['Vanish', 14], ['Feral Senses', 18],
                 ['Foe Slayer', 20]],
                [['ASI', 4], ['ASI * 2', 8, 'ASI'], ['ASI * 3', 12, 'ASI * 2'], ['ASI * 4', 16, 'ASI * 3'],
                 ['ASI * 5', 19, 'ASI * 4'], ['Favoured Enemy', 1], ['Greater Favoured Enemy', 6],
                 ['Natural Explorer', 1], ['Fighting Style', 2], ['Primeval Awareness', 3]]),
    PlayerClass('Rogue', [0, 2, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0], [0, 1, 0, 1, 0, 0],
                 ['acrobatics_prof', 'athletics_prof', 'deception_prof', 'insight_prof', 'intimidation_prof',
                  'investigation_prof', 'perception_prof', 'performance_prof', 'persuasion_prof',
                  'sleight_of_hand_prof', 'stealth_prof'], 4, ["Thieves' Cant"],
                 ['Simple Weapons', 'Hand Crossbows', 'Longswords', 'Rapiers', 'Shortswords'],
                 [['Rapier', 'Shortbow & Arrow * 20', "Burglar's Pack"],
                 ['Shortsword', 'Shortsword', "Dungeoneer's Pack"],
                 ['None', 'None', "Explorer's Pack"]],
                 ['Leather Armor', 'Dagger', 'Dagger', "Thieves' Tools"],
                ['Light Armor', "Thieves' Tools"], 3,
                [['Sneak Attack', 1], ['Cunning Action', 2], ['Uncanny Dodge', 5], ['Evasion', 7]],
                [['ASI', 4], ['ASI * 2', 8, 'ASI'], ['ASI * 3', 10, 'ASI * 2'], ['ASI * 4', 12, 'ASI * 3'],
                 ['ASI * 5', 16, 'ASI * 4'], ['ASI * 6', 19, 'ASI * 5'], ['Expertise * 2', 1],
                 ['Expertise * 4', 6, 'Expertise * 2'], ['Reliable Talent', 11], ['Blindsense', 14],
                 ['Slippery Mind', 15], ['Stroke of Luck', 20]]),
    PlayerClass('Sorcerer', [0, 0, 1, 0, 0, 2], [0, 0, 0, 1, 1, 0], [0, 0, 1, 0, 0, 1],
                 ['arcana_prof', 'deception_prof', 'insight_prof', 'intimidation_prof', 'persuasion_prof',
                  'religion_prof'], 2, [],
                 ['Daggers', 'Darts', 'Slings', 'Quarterstaffs', 'Light Crossbows'],
                 [['Light Crossbow & Bolt * 20', 'Component Pouch', "Dungeoneer's Pack"],
                 ['Simple Weapon', 'Arcane Focus', "Explorer's Pack"]],
                 ['Dagger', 'Dagger'],
                [], 1,
                [['Font of Magic', 2]],
                [['ASI', 4], ['ASI * 2', 8, 'ASI'], ['ASI * 3', 12, 'ASI * 2'], ['ASI * 4', 16, 'ASI * 3'],
                 ['ASI * 5', 19, 'ASI * 4'], ['Sorcerous Restoratioon', 20]]),
    PlayerClass('Warlock', [0, 0, 1, 0, 0, 2], [0, 0, 0, 1, 1, 0], [0, 0, 0, 0, 1, 1],
                 ['arcana_prof', 'deception_prof', 'history_prof', 'intimidation_prof', 'investigation_prof',
                  'nature_prof', 'religion_prof'], 2, [],
                 ['Simple Weapons'],
                 [['Light Crossbow & Bolt * 20', 'Component Pouch', "Scholar's Pack"],
                 ['Simple Weapon', 'Arcane Focus', "Dungeoneer's Pack"]],
                 ['Leather Armor', 'Simple Weapon', 'Dagger', 'Dagger'],
                ['Light Armor'], 3,
                [],
                [['Pact Boon', 3], ['ASI', 4], ['ASI * 2', 8, 'ASI'], ['ASI * 3', 12, 'ASI * 2'],
                 ['ASI * 4', 16, 'ASI * 3'], ['ASI * 5', 19, 'ASI * 4'], ['Eldritch Invocations * 2', 2],
                 ['Eldritch Invocations * 3', 5, 'Eldritch Invocations * 2'],
                 ['Eldritch Invocations * 4', 7, 'Eldritch Invocations * 3'],
                 ['Eldritch Invocations * 5', 9, 'Eldritch Invocations * 4'],
                 ['Eldritch Invocations * 6', 12, 'Eldritch Invocations * 5'],
                 ['Eldritch Invocations * 7', 15, 'Eldritch Invocations * 6'],
                 ['Eldritch Invocations * 8', 18, 'Eldritch Invocations * 7'], ['Level 6 Mystic Arcanum', 11],
                 ['Level 7 Mystic Arcanum', 13], ['Level 8 Mystic Arcanum', 15], ['Level 9 Mystic Arcanum', 17],
                 ['Eldritch Master', 20]]),
    PlayerClass('Wizard', [0, 1, 1, 2, 0, 0], [1, 0, 0, 0, 0, 0], [0, 0, 0, 1, 1, 0],
                 ['arcana_prof', 'history_prof', 'insight_prof', 'investigation_prof', 'medicine_prof',
                  'religion_prof'], 2, [],
                 ['Daggers', 'Darts', 'Slings', 'Quarterstaffs', 'Light Crossbows'],
                 [['Quarterstaff', 'Component Pouch', "Scholar's Pack"],
                 ['Dagger', 'Arcane Focus', "Explorer's Pack"]],
                 ['Spellbook'],
                [], 2,
                [],
                [['ASI', 4], ['ASI * 2', 8, 'ASI'], ['ASI * 3', 12, 'ASI * 2'], ['ASI * 4', 16, 'ASI * 3'],
                 ['ASI * 5', 19, 'ASI * 4'], ['Arcane Recovery', 1], ['Spell Mastery', 18], ['Signature Spells', 20]])
]

# parentClass, name, languages, weapon_profs, skill_profs, other_profs
barbarian_subclasses = [
    PlayerSubClass(player_classes[0], 'Berserker Barbarian', [], [], [], [],
                   [['Frenzied Rage', 3], ['Intimidating Presence', 10], ['Retaliation', 14]], [['Mindless Rage', 6]]),
    PlayerSubClass(player_classes[0], 'Totem Warrior Barbarian', [], [], [], [],
                   [], [['Spirit Seeker', 3], ['Totem Spirit', 3], ['Aspect of the Beast', 6], ['Spirit Walker', 10],
                        ['Totemic Attunement', 14]])
]
player_classes[0].setSubclasses(barbarian_subclasses)

bard_subclasses = [
    PlayerSubClass(player_classes[1], 'Lore Bard', [], [], ['Any', 'Any', 'Any'], [],
                   [['Cutting Words', 3]], [['Additional Magic Secrets', 6], ['Peerless Skill', 14]]),
    PlayerSubClass(player_classes[1], 'Valor Bard', [], ['Martial Weapons'], [], ['Medium Armor', 'Shields'],
                   [['Combat Inspiration', 3], ['Extra Attack', 6], ['Battle Magic', 14]], [])
]
player_classes[1].setSubclasses(bard_subclasses)

cleric_subclasses = [
    PlayerSubClass(player_classes[2], 'Knowledge Cleric', ['Any', 'Any'], [],
                   [['arcana_prof', 'history_prof', 'nature_prof', 'religion_prof'],
                    ['arcana_prof', 'history_prof', 'nature_prof', 'religion_prof']], [],
                   [['Potent Spellcasting', 8]], [['Channel Divinity: Knowledge of the Ages', 2],
                                                  ['Channel Divinity: Read Thoughts', 6], ['Visions of the Past', 17]]),
    PlayerSubClass(player_classes[2], 'Life Cleric', [], [], [], ['Heavy Armor'],
                   [['Channel Divinity: Preserve Life', 2], ['Divine Strike', 8]],
                   [['Disciple of Life', 2], ['Blessed Healer', 6], ['Supreme Healing', 17]]),
    PlayerSubClass(player_classes[2], 'Light Cleric', [], [], [], [],
                   [['Light Cantrip', 1], ['Warding Flare', 1], ['Channel Divinity: Radiance of the Dawn', 2],
                    ['Potent Spellcasting', 8], ['Corona of Light', 17]], [['Improved Flare', 6]]),
    PlayerSubClass(player_classes[2], 'Nature Cleric', [], [],
                   [['animal_handling_prof', 'nature_prof', 'survival_prof']], ['Heavy Armor'],
                   [['Dampen Elements', 6], ['Divine Strike', 8]], [['Channel Divinity: Charm Animals and Plants', 2],
                                                                    ['Master of Nature', 17]]),
    PlayerSubClass(player_classes[2], 'Tempest Cleric', [], [], [], ['Martial Weapons', 'Heavy Armor'],
                   [['Wrath of Storm', 1], ['Thunderous Strike', 6], ['Divine Strike', 8]],
                   [['Channel Divinity: Destructive Wrath', 2], ['Stormborn', 17]]),
    PlayerSubClass(player_classes[2], 'Trickery Cleric', [], [], [], [],
                   [['Channel Divinity: Invoke Duplicity', 2], ['Channel Divinity: Cloak of Shadows', 6],
                    ['Divine Strike', 8]], [['Blessing of the Trickster', 1], ['Improved Duplicity', 17]]),
    PlayerSubClass(player_classes[2], 'War Cleric', [], [], [], ['Martial Weapons', 'Heavy Armor'],
                   [['War Priest', 1], ['Channel Divinity: Guided Strike', 2],
                    ["Channel Divinity: War Gods' Blessing", 6], ['Divine Strike', 8]], [['Avatar of Battle', 17]])
]
player_classes[2].setSubclasses(cleric_subclasses)

druid_subclasses = [
    PlayerSubClass(player_classes[3], 'Land Druid', [], [], [], [],
                   [["Nature's Sancturay", 14]], [['Bonus Cantrip', 2], ['Natural Recovery', 2], ['Circle Spells', 3],
                                                  ["Land's Stride", 6], ["Nature's Ward", 10]]),
    PlayerSubClass(player_classes[3], 'Moon Druid', [], [], [], [],
                   [['Combat Wild Shape', 2, 'Wild Shape'], ['Primal Strike', 6], ['Elemental Wild Shape', 10]],
                   [['Circle Forms', 2], ['Thousand Forms', 14]])
]
player_classes[3].setSubclasses(druid_subclasses)

fighter_subclasses = [
    PlayerSubClass(player_classes[4], 'Champion Fighter', [], [], [], [],
                   [['Improved Critical', 3], ['Superior Critical', 15, 'Improved Critical'], ['Survivor', 18]],
                   [['Remarkable Athlete', 7], ['Additional Fighting Style', 10]]),
    PlayerSubClass(player_classes[4], 'Battlemaster Fighter', [], [], [], ['Artisan'],
                   [['Superiority Die (d8) * 4', 3], ['Superiority Die (d8) * 5', 7, 'Superiority Die (d8) * 4'],
                    ['Superiority Die (d10) * 5', 10, 'Superiority Die (d8) * 5'],
                    ['Superiority Die (d10) * 6', 15, 'Superiority Die (d10) * 5'],
                    ['Superiority Die (d12) * 6', 18, 'Superiority Die (d10) * 6']], [['Know Your Enemy', 7],
                                                                                      ['Relentless', 15]]),
    PlayerSubClass(player_classes[4], 'Eldritch Knight Fighter', [], [], [], [],
                   [['Eldritch Strike', 10], ['Arcane Charge', 15]],
                   [['Spellcasting', 3], ['Weapon Bond', 3], ['War Magic', 7], ['Improved War Magic', 18, 'War Magic']])
]
player_classes[4].setSubclasses(fighter_subclasses)

monk_subclasses = [
    PlayerSubClass(player_classes[5], 'Open Hand Monk', [], [], [], [],
                   [['Open Hand Technique', 3], ['Wholeness of Body', 6], ['Quivering Palm', 17]],
                   [['Tranquility', 11]]),
    PlayerSubClass(player_classes[5], 'Shadow Monk', [], [], [], [],
                   [['Shadow Arts', 3], ['Shadow Step', 6], ['Cloak of Shadows', 11], ['Opportunist', 17]], []),
    PlayerSubClass(player_classes[5], 'Four-Elements Monk', [], [], [], [],
                   [], [['Elemental Attunemnt', 3], ['Elemental Discipline * 1', 3],
                        ['Elemental Disciplines * 2', 6, 'Elemental Discipline * 1'],
                        ['Elemental Disciplines * 3', 11, 'Elemental Discipline * 2'],
                        ['Elemental Disciplines * 4', 17, 'Elemental Discipline * 3'],
                        ['Max Ki to Spend on a Spell: 3', 5],
                        ['Max Ki to Spend on a Spell: 4', 9, 'Max Ki to Spend on a Spell: 3'],
                        ['Max Ki to Spend on a Spell: 5', 13, 'Max Ki to Spend on a Spell: 4'],
                        ['Max Ki to Spend on a Spell: 6', 17, 'Max Ki to Spend on a Spell: 5']])
]
player_classes[5].setSubclasses(monk_subclasses)

paladin_subclasses = [
    PlayerSubClass(player_classes[6], 'Devotion Paladin', [], [], [], [],
                   [['Channel Divinity: Sacred Weapon', 3], ['Channel Divinity: Turn the Unholy', 3],
                    ['Holy Nimbus', 20]], [['Oath Spells', 3], ['Aura of Devotion', 7], ['Purity of Spirit', 15]]),
    PlayerSubClass(player_classes[6], 'Ancients Paladin', [], [], [], [],
                   [["Channel Divinity: Nature's Wrath", 3], ['Channel Divinity: Turn the Fathless', 3],
                    ['Elder Champion', 20]], [['Oath Spells', 3], ['Aura of Warding', 7], ['Undying Sentinal', 15]]),
    PlayerSubClass(player_classes[6], 'Vengeance Paladin', [], [], [], [],
                   [['Channel Divinity: Abjure Enemy', 3], ['Channel Divinity: Vow of Enmity', 3],
                    ['Avenging Angel', 20]], [['Oath Spells', 3], ['Relentless Avenger', 7], ['Sould of Vengence', 15]])
]
player_classes[6].setSubclasses(paladin_subclasses)

ranger_subclasses = [
    PlayerSubClass(player_classes[7], 'Beast Master Ranger', [], [], [], [],
                   [['Coordinated Attack', 5], ['Storm of Claws and Fangs', 11], ["Superior Beat's Defense", 15]],
                   [["Beast's Defense", 7]]),
    PlayerSubClass(player_classes[7], 'Hunter Ranger', [], [], [], [],
                   [["Extra Attack", 5], ['Multiattack', 11], ["Superior Hunter's Defense", 15]],
                   [["Hunter's Prey", 3], ['Defensive Tactics', 7]]),
    PlayerSubClass(player_classes[7], 'Gloom Stalker Ranger', [], [], [], [],
                   [['Extra Attack', 5], ["Stalker's Flurry", 11], ['Shadowy Dodge', 15]],
                   [["Gloom Stalker Magic", 3], ['Dread Ambusher', 3], ['Umbral Sight', 3], ["Iron Mind", 7]])
]
player_classes[7].setSubclasses(ranger_subclasses)

rogue_subclasses = [
    PlayerSubClass(player_classes[8], 'Thief Rogue', [], [], [], [],
                   [["Thief's Reflexes", 17]], [["Fast Hands", 3], ["Second-Story Work", 3], ['Supreme Sneak', 9], ['Use Magic Device', 13]]),
    PlayerSubClass(player_classes[8], 'Assasin Rogue', [], [], [], ['Disguise Kit', "Poisoner's Kit"],
                   [['Assasinate', 3], ['Death Strike', 17]], [["Infiltration Expertise", 9], ['Imposter', 13]]),
    PlayerSubClass(player_classes[8], 'Arcane Trickster Rogue', [], [], [], [],
                   [['Versatile Trickster', 13], ['Spell Thief', 17]],
                   [['Spellcasting', 3], ['Mage Hand Legerdemain', 3], ['Magical Ambush', 9]])
]
player_classes[8].setSubclasses(rogue_subclasses)

sorcerer_subclasses = [
    PlayerSubClass(player_classes[9], 'Draconic Sorcerer', ['Draconic'], [], [], [],
                   [['Elemental Affinity', 6], ['Dragon Wings', 14], ['Draconic Prescence', 18]],
                   [['Draconic Ancestry', 1], ['Draconic Resilience', 1]]),
    PlayerSubClass(player_classes[9], 'Wild Magic Sorcerer', [], [], [], [],
                   [['Tides of Chaos', 1], ['Bend Luck', 6], ['Spell Bombardment', 18]],
                   [['Wild Magic Surge', 1], ['Controlled Chaos', 14]])
]
player_classes[9].setSubclasses(sorcerer_subclasses)

warlock_subclasses = [
    PlayerSubClass(player_classes[10], 'Archfey Warlock', [], [], [], [],
                   [['Fey Presence', 1], ['Misty Escape', 6], ['Beguiling Defense', 10], ['Dark Delerium', 14]],
                   [['Expanded Spell List', 1]]),
    PlayerSubClass(player_classes[10], 'Fiend Warlock', [], [], [], [],
                   [['Hurl Through Hell', 14]], [['Expanded Spell List', 1], ["Dark One's Blessing", 1],
                                                 ["Dark One's Own Luck", 6], ['Fiendish Resilience', 10]]),
    PlayerSubClass(player_classes[10], 'Great Old One Warlock', [], [], [], [],
                   [['Entropic Journey', 6], ['Create Thrall', 14]],
                   [['Expanded Spell List', 1], ['Awakened Mind', 1], ['Thought Shield', 10]])
]
player_classes[10].setSubclasses(warlock_subclasses)

wizard_subclasses = [
    PlayerSubClass(player_classes[11], 'Abjuration Wizard', [], [], [], [],
                   [['Arcane Ward', 2], ['Projected Ward', 6]], [['Abjuration Savant', 2], ['Improved Abjuration', 10],
                                                                 ['Spell Resitance', 14]]),
    PlayerSubClass(player_classes[11], 'Conjuration Wizard', [], [], [], [],
                   [['Benign Transport', 6]], [['Conjuration Savant', 2], ['Minor Conjuration', 2],
                                               ['Focused Conjuration', 10], ['Durable Summons', 14]]),
    PlayerSubClass(player_classes[11], 'Divination Wizard', [], [], [], [],
                   [['Portent', 2], ['Greater Portent', 14, 'Portent']],
                   [['Divination Savant', 2], ['Expert Divination', 6], ['The Third Eye', 10]]),
    PlayerSubClass(player_classes[11], 'Enchantment Wizard', [], [], [], [],
                   [['Hypnotic Gaze', 2], ['Instinctive Charm', 6], ['Alter Memories', 14]],
                   [['Enchantment Savant', 2], ['Split Enchantment', 10]]),
    PlayerSubClass(player_classes[11], 'Evocation Wizard', [], [], [], [],
                   [['Sculpt Spells', 2], ['Empowered Evocation', 10], ['Overchannel', 14]], [['Evocation Savant', 2],
                                                                                              ['Potent Cantrip', 6]]),
    PlayerSubClass(player_classes[11], 'Illusion Wizard', [], [], [], [],
                   [['Illusory Self', 10], ['Illusory Reality', 14]],
                   [['Illusion Savant', 2], ['Improved Minor Illusion', 2], ['Malleable Illusions', 6]]),
    PlayerSubClass(player_classes[11], 'Necromancy Wizard', [], [], [], [],
                   [['Command Undead', 14]], [['Necromancy Savant', 2], ['Grim Harvest', 2], ['Undead Thralls', 6], ['Inured to Undeath', 10]]),
    PlayerSubClass(player_classes[11], 'Transmutation Wizard', [], [], [], [],
                   [['Shapechanger', 10], ['Master Transmuter', 14]],
                   [['Transmutation Savant', 2], ['Minor Alchemy', 2], ["Transmuter's Stone", 6]])
]
player_classes[11].setSubclasses(wizard_subclasses)


player_races = []
for i, row in df_races.iterrows():
    player_races.append(PlayerRace(row['Name'], [row['STR'], row['DEX'], row['CON'], row['INT'], row['WIS'], row['CHA']],
                                   row['Rand_bonus'], listString(row['Languages']), listString(row['Weapon_profs']),
                                   listString(row['Other_profs'])))


player_sub_races = []
for i, row in df_subraces.iterrows():
    player_sub_races.append(PlayerSubRace(player_races[row['Parent_class']], row['Name'], listString(row['Bonuses']),
                                    listString(row['Languages']), listString(row['Weapon_profs']),
                                   listString(row['Other_profs']), listString(row['Alignment_pref'])))

"""
player_raceList = [[]]
n = 0
for subrace in player_sub_races:
    player_raceList[row['Parent_class']].append(subrace)
    n = n + 1

for i in range(8):
    player_races[i].setSubraces(player_raceList[i])"""


player_races[0].setSubraces([player_sub_races[16]])
player_races[1].setSubraces([player_sub_races[0], player_sub_races[1], player_sub_races[2]])
player_races[2].setSubraces([player_sub_races[3], player_sub_races[4], player_sub_races[5]])
player_races[3].setSubraces([player_sub_races[6], player_sub_races[7], player_sub_races[8]])
player_races[4].setSubraces([player_sub_races[12]])
player_races[5].setSubraces([player_sub_races[13]])
player_races[6].setSubraces([player_sub_races[9], player_sub_races[10], player_sub_races[11]])
player_races[7].setSubraces([player_sub_races[14]])
player_races[8].setSubraces([player_sub_races[15]])


player_backgrounds = []
for i, row in df_backgrounds.iterrows():
    player_backgrounds.append(PlayerBackground(row['Name'], listString(row['Skills']),
                                   listString(row['Other_profs']), listString(row['Weapon_profs'])))



all_languages = [
    'Common', 'Dwarvish', 'Elvish', 'Giant', 'Gnomish', 'Goblin', 'Halfling', 'Orc', 'Abyssal', 'Celestial', 'Draconic',
    'Deep Speech', 'Infernal', 'Primordial', 'Sylvan', 'Undercommon'
]

artisan_tools = [
    "Alchemist's Supplies", "Brewer's Supplies", "Calligrapher's Supplies", "Carpenter's Tools", "Cobbler's Tools",
    "Cooks's Utensils", "Glassblower's Tools", "Jeweler's Tools", "Leatherworker's Tools", "Mason's Tools",
    "Painter's Supplies", "Potter's Tools", "Smith's Tools", "Tinker's Tools", "Weaver's Tools", "Woodcarver's Tools"
]

instruments = [
    'Bagpipes', 'Snare Drum', 'Dulcimer', 'Flute', 'Lute', 'Lyre', 'French Horn', 'Trumpet', 'Saxophone', 'Pan Flute',
    'Shawm', 'Viola', 'Violin', 'Ukulele', 'Banjo', 'Kazoo', 'Slide Whistle', 'Cowbell', 'Oboe', 'Accordion'
]

game_list = [
    'Playing Cards', 'Dice'
]


simple_weapons = []
for i, row in df_simple_weapons.iterrows():
    dice = []
    for die in listString(row['Damage']):
        dice.append(Die(die))

    if dice == []:
        dice = [Die('')]

    simple_weapons.append(Weapon(row['Name'], dice, listString(row['Traits']), row['Attack_type'], row['Damage_type'],
                                 row['Cost'], float(row['Weight']), row['Skill']))


martial_weapons = []
for i, row in df_martial_weapons.iterrows():
    dice = []
    if dice == []:
        dice = [Die('')]

    for die in listString(row['Damage']):
        dice.append(Die(die))

    martial_weapons.append(Weapon(row['Name'], dice, listString(row['Traits']), row['Attack_type'], row['Damage_type'],
                                 row['Cost'], float(row['Weight']), row['Skill']))


all_weapon_names = []

for weapon in simple_weapons:
    all_weapon_names.append(weapon.name)

for weapon in martial_weapons:
    all_weapon_names.append(weapon.name)


armors = []
for i, row in df_armor.iterrows():
    armors.append(Armor(row['Name'], row['Base AC'], row['Max Dex'], row['Min Strength'], row['Tier']))


skill_prof_dict = {
    'acrobatics_prof': 'No',
    'animal_handling_prof': 'No',
    'arcana_prof': 'No',
    'athletics_prof': 'No',
    'deception_prof': 'No',
    'history_prof': 'No',
    'insight_prof': 'No',
    'intimidation_prof': 'No',
    'investigation_prof': 'No',
    'medicine_prof': 'No',
    'nature_prof': 'No',
    'perception_prof': 'No',
    'performance_prof': 'No',
    'persuasion_prof': 'No',
    'religion_prof': 'No',
    'sleight_of_hand_prof': 'No',
    'stealth_prof': 'No',
    'survival_prof': 'No'
}


skill_mod_dict = {
    'acrobatics': '+0',
    'animal_handling': '+0',
    'arcana': '+0',
    'athletics': '+0',
    'deception': '+0',
    'history': '+0',
    'insight': '+0',
    'intimidation': '+0',
    'investigation': '+0',
    'medicine': '+0',
    'nature': '+0',
    'perception': '+0',
    'performance': '+0',
    'persuasion': '+0',
    'religion': '+0',
    'sleight_of_hand': '+0',
    'stealth': '+0',
    'survival': '+0'
}


name_list = [
    'Judas', 'Caerus', 'Destin', 'Dexas', 'Alex', 'Gambit', 'Luna', 'Willow', 'Cliff', 'Torren', 'Savanah', 'Rot',
    'Bog', 'Coco', 'Cora', 'Florence', 'Sprig', 'Percival', 'Jester', 'Annabelle', 'Arthur', 'Beatrice', 'Balthazar',
    'Casey', 'Cassandra', 'Candor', 'Delena', 'Damian', 'Ella', 'Etri', 'Elanor', 'Fiona', 'Forrest', 'Gale',
    'Gabriella', 'Grace', 'Hector', 'Herbert', 'Hazel', 'Ilda', 'Isabelle', 'Irving', 'Indy', 'Ichor', 'Jasmine',
    'Jessica', 'Julia', 'Jill', 'James', 'Jack', 'Jeremiah', 'Jeb', 'Kelsy', 'Kelly', 'Kora', 'Kyle', 'Kent', 'Karson',
    'Laura', 'Lauren', 'Lucille', 'Lily', 'Lambert', 'Lucas', 'Luke', 'Lincoln', 'Link', 'Monica', 'Michael', 'Marissa',
    'Margo', 'Mason', 'Manson', 'Marcus', 'Nila', 'Nicholas', 'Nestelle', 'Nathaniel', 'Oscar', 'Orwell', 'Olivia',
    'Owen', 'Ornna', 'Phillipe', 'Patricia', 'Pascal', 'Paula', 'Quentin', 'Quincy', 'Quiplet', 'Rachel', 'Raxon',
    'Raven', 'Rory', 'Sarah', 'Samantha', 'Samuel', 'Santiago', 'Tyler', 'Troy', 'Taylor', 'Theodore', 'Tanya',
    'Undulee', 'Uka', 'Unexe', 'Victor', 'Vanessa', 'Valerie', 'Vladmir', 'Watson', 'Walker', 'Wallace', 'Wither',
    'Wanda', 'Wave', 'Yousef', 'Yohan', 'Yarra', 'Yeuki', 'Xander', 'Xena', 'Zukko', 'Zachary', 'Zara', 'Ekin',
    'Alfonzo', 'Bertrand', 'Cretin', 'Dromanir', 'Drex', 'Elestanor', 'Frontonimir', 'Galactimus', 'Hadeon', 'Escobar',
    'Inphantyne', 'Kanella', 'Lipton', 'Lufaunza', 'Maurice', 'Nalazar', 'Bubbles', 'Hantioumi', 'Schmique', 'Baylor'
]


consonant_list = [
    'b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'r', 's', 't', 'v', 'w', 'x', 'z',
    'ch', 'ss', 'rr', 'nn', 'tt', 'str', 'kr', 'tr', 'wh', 'kl', 'dr', 'pl', 'cr', 'ff', 'ph', 'br', 'rk', 'll',
    'kl', 'ck', 'rt', 'gr', 'rg', 'nt', 'tn', 'zz', 'tch', 'gg'
]


vowel_list = [
    'a', 'e', 'i', 'o', 'u', 'y',
    'aa', 'ae', 'eu', 'ee', 'ie', 'ii', 'au', 'oe', 'oue'
]

cannot_end_name = [
    'ph', 'wh', 'kl', 'ae', 'u', 'kr', 'pl', 'h', 'gr', 'nt', 'tn', 'rk', 'rg', 'cr'
]


cannot_start_name = [
    'rt', 'ck', 'wh', 'ss', 'ee', 'rr', 'ie', 'ii', 'll', 'nn', 'oe', 'rg', 'nt', 'tn', 'tt', 'rk', 'ae', 'zz', 'ff', 'gg'
]


last_name_1 = [
    'Quick', 'Half', 'Blood', 'Soul', 'Blind', 'Moon', 'Sky', 'Light', 'Dark', 'Slip', 'Hollow', 'Old', 'Young', 'Dead',
    'Near', 'Far', 'Dream', 'Home', 'Love', 'Hate', 'Grim', 'Deep', 'Low', 'Rot', 'Gray', 'Frost', 'Gold', 'God',
    'Edge', 'Heart', 'Steel', 'Grave', 'Bright', 'Black', 'White', 'Red', 'Blue', 'Thunder', 'Bell', 'Silver', 'Flame',
    'Void', 'Two', 'Twin'
]


last_name_2 = [
    'step', 'tongue', 'foot', 'sight', 'eyes', 'track', 'wind', 'sword', 'stone', 'jewel', '-Gem', 'water', 'pack',
    'shore', 'walker', 'blade', 'hammer', 'wood', 'cloud', 'wall', 'sleeve', 'strike', 'sun', 'sand', 'hide', 'axe',
    'glow', 'web', 'net', 'weave', 'flame', 'crest', 'break', 'fell', 'snow', 'marsh', 'swamp', 'scar', 'wound',
    'spark', 'leaf', 'son', 'trap', 'bloom', 'stem', 'scab'
]


midset_list = [
    'von', 'the', 'of the', 'of', 'of house', 'da', 'das', 'el', 'sol'
]


name = get_name(name_list, last_name_1, last_name_2, consonant_list, vowel_list, midset_list, cannot_end_name,
                cannot_start_name)

char_class = get_random_player_class(player_classes)
char_level = get_random_level()
char_subclass = char_class.pickSubclass(char_level)
race = get_random_race(player_races).pickSubrace()
background = get_random_background(player_backgrounds)
alignment_num = get_alignment_num(race)
alignment = get_alignment(alignment_num)
prof_bonus = get_prof_bonus(char_level)

stats = roll_stats(char_class, race)
modifiers = get_modifier(stats)

saves = get_saves(char_class, prof_bonus, modifiers)
save_prof_strings = get_save_profs(char_class)
get_skill_profs(background, char_class, char_subclass)
get_skill_modifiers(char_class, modifiers, prof_bonus)

languages = get_languages(race, char_class)
weapon_profs = get_weapon_profs(char_class, race, background)
other_profs = get_other_profs(char_class, background, race, artisan_tools, instruments, game_list)
proficiencies_languages = get_all_profs_and_langs(languages, weapon_profs, other_profs)

[weapons, equipment] = get_weapons_and_equipment(char_class, weapon_profs, all_weapon_names)

for i in range(3):
    if len(weapons) <= i:
        weapons.append(Weapon('', [Die('')], [], '', '', '', 0, ''))

weapon_attack_mods = get_weapon_attack_bonuses(weapons, modifiers, weapon_profs, prof_bonus)
weapon_damage_mods = get_weapon_damage_bonuses(weapons, modifiers)
attack_string = get_attack_string(get_attack_list(char_subclass, char_level))

equipment_list = sort_equipment_list(get_equipment_list(equipment))
passive_string = get_passive_string(get_passive_list(char_subclass, char_level))

ac = get_armor_class(equipment_list, armors, stats, modifiers, race)


text_dict = {
    'character_name': name,
    'class_level': char_class.name + ' ' + char_level,
    'race': race.name,
    'background': background.name,
    'alignment': alignment,

    'prof_bonus': prof_bonus,
    'strength_save': saves[0],
    'dexterity_save': saves[1],
    'constitution_save': saves[2],
    'intelligence_save': saves[3],
    'wisdom_save': saves[4],
    'charisma_save': saves[5],

    'strength_modifier': modifiers[0],
    'strength_score': stats[0],
    'dexterity_modifier': modifiers[1],
    'dexterity_score': stats[1],
    'constitution_modifier': modifiers[2],
    'constitution_score': stats[2],
    'intelligence_modifier': modifiers[3],
    'intelligence_score': stats[3],
    'wisdom_modifier': modifiers[4],
    'wisdom_score': stats[4],
    'charisma_modifier': modifiers[5],
    'charisma_score': stats[5],
    'passive_perception': str(10 + math.floor(float(skill_mod_dict['perception']))),

    'proficiencies_languages': proficiencies_languages,

    'attack1_name': weapons[0].name,
    'attack1_bonus': weapon_attack_mods[0],
    'attack1_damage': weapons[0].damage[0].name + " " + weapon_damage_mods[0] + " " + weapons[0].damage_type,
    'attack2_name': weapons[1].name,
    'attack2_bonus': weapon_attack_mods[1],
    'attack2_damage': weapons[1].damage[0].name + " " + weapon_damage_mods[1] + " " + weapons[1].damage_type,
    'attack3_name': weapons[2].name,
    'attack3_bonus': weapon_attack_mods[2],
    'attack3_damage': weapons[2].damage[0].name + " " + weapon_damage_mods[2] + " " + weapons[2].damage_type,
    'attack_list': attack_string,

    'equipment': equipment_list,
    'features': passive_string,

    'armor_class': ac,
    'initiative': modifiers[1],
    'speed': '30 ft'
}


check_dict = {
    'strength_save_prof': save_prof_strings[0],
    'dexterity_save_prof': save_prof_strings[1],
    'constitution_save_prof': save_prof_strings[2],
    'intelligence_save_prof': save_prof_strings[3],
    'wisdom_save_prof': save_prof_strings[4],
    'charisma_save_prof': save_prof_strings[5]
}


if __name__ == '__main__':
    write_fillable_pdf(char_sheet_template_path, char_sheet_output_path, text_dict, check_dict, skill_prof_dict)