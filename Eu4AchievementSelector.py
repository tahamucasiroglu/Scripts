import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageTk
from io import BytesIO
import tkinter as tk
import json
import random


def get_steam_achievements(profile_url):
    response = requests.get(profile_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    achievement_rows = soup.select('div.achieveRow')

    achievements = []

    for row in achievement_rows:
        img_url = row.find('img')['src']
        title = row.find('h3').text.strip()
        description = row.find('h5').text.strip()
        unlock_time = row.find('div', class_='achieveUnlockTime')
        if unlock_time:
            unlock_time = unlock_time.text.strip()
        else:
            unlock_time = None
        achievements.append({
            'Image URL': img_url,
            'Title': title,
            'Description': description,
            'Unlock Time': unlock_time
        })

    return achievements


def get_general_steam_achievements(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    achievement_rows = soup.select('div.achieveRow')

    achievements = []

    for row in achievement_rows:
        img_url = row.find('img')['src']
        title = row.find('h3').text.strip()
        description = row.find('h5').text.strip()
        percent = row.find('div', class_='achievePercent').text.strip()
        achievements.append({
            'Image URL': img_url,
            'Title': title,
            'Description': description,
            'Completion Percent': percent
        })

    return achievements


def get_wiki_achievements(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    achievement_tables = soup.select('table.sortable')

    achievements = []

    for table in achievement_tables:
        rows = table.select('tbody > tr')

        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 7: 
                title = str(cols[0].select('div > div > div')).split('<span id')[0].split('>')[-1]
                subTitle = str(cols[0].select('div > div > div')).split(';">')[-1].split('</div>]')[0]
                
                conditions = cols[1].text.strip() if cols[1].text.strip() else 'Yok'
                requirements = [li.text.strip() for li in cols[2].find_all('li')] if cols[2].find_all('li') else [cols[2].text.strip()]
                notes = cols[3].text.strip()
                dlc_icons = [icon['alt'] for icon in cols[4].find_all('img')]
                version = cols[5].text.strip()
                difficulty = cols[6].text.strip()
                

                achievements.append({
                    'Title': title,
                    'SubTitle': subTitle,
                    'Conditions': conditions,
                    'Requirements': requirements,
                    'Notes': notes,
                    'DLC Icons': dlc_icons,
                    'Version': version,
                    'Difficulty': difficulty
                })

    return achievements


def merge_achievements(steam_achievements:list, general_achievements:list, wiki_achievements:list):
    merged_achievements = []

    for steam_achievement in steam_achievements:
        if not steam_achievement['Unlock Time']:
            general_achievement = None
            for ga in general_achievements:
                if ga['Title'] == steam_achievement['Title']:
                    general_achievement = ga
        
            wiki_achievement = None
            for wa in wiki_achievements:
                if wa['Title'] == steam_achievement['Title']:
                    wiki_achievement = wa

            merged_achievements.append({
                'Title': steam_achievement['Title'],
                'SubTitle': general_achievement['Description'],
                'Conditions': wiki_achievement['Conditions'] if wiki_achievement != None else "None",
                'Requirements': wiki_achievement['Requirements'] if wiki_achievement != None else "None",
                'Notes': wiki_achievement['Notes'] if wiki_achievement != None else "None",
                'DLC Icons': wiki_achievement['DLC Icons'] if wiki_achievement != None else "None",
                'Version': wiki_achievement['Version'] if wiki_achievement != None else "None",
                'Difficulty': wiki_achievement['Difficulty'] if wiki_achievement != None else "None",
                'Image URL': steam_achievement['Image URL'] if steam_achievement['Image URL'] != None else general_achievement['Image URL'],
                'Description': steam_achievement['Description'],
                'Completion Percent': general_achievement['Completion Percent'],
                'Image URL': steam_achievement['Image URL']
            })
    random.shuffle(merged_achievements)
    return merged_achievements


class AchievementApp:
    def __init__(self, root, achievements):
        self.root = root
        self.achievements = achievements
        self.index = 0
        self.total = len(achievements)

        self.image_label = tk.Label(root)
        self.image_label.pack()

        self.title_label = tk.Label(root, text="", font=("Helvetica", 16))
        self.title_label.pack()

        self.description_label = tk.Label(root, text="", wraplength=400)
        self.description_label.pack()

        self.wiki_description_label = tk.Label(root, text="", wraplength=400)
        self.wiki_description_label.pack()

        self.difficulty_label = tk.Label(root, text="")
        self.difficulty_label.pack()

        self.version_label = tk.Label(root, text="")
        self.version_label.pack()

        self.percent_label = tk.Label(root, text="")
        self.percent_label.pack()

        self.requirements_label = tk.Label(root, text="", wraplength=400)
        self.requirements_label.pack()

        self.dlc_label = tk.Label(root, text="", wraplength=400)
        self.dlc_label.pack()

        self.complete_button = tk.Button(root, text="Tamam", command=root.quit)
        self.complete_button.pack(side=tk.LEFT)

        self.next_button = tk.Button(root, text="Devam", command=self.next_achievement)
        self.next_button.pack(side=tk.RIGHT)

        if self.total > 0:
            self.show_achievement()

    def show_achievement(self):
        achievement = self.achievements[self.index]

        response = requests.get(achievement['Image URL'])
        img_data = BytesIO(response.content)
        img = Image.open(img_data)
        img = img.resize((64, 64), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)

        self.image_label.config(image=img)
        self.image_label.image = img

        self.title_label.config(text=achievement['Title'])
        self.description_label.config(text=achievement['Description'])
        self.wiki_description_label.config(text=f"Conditions: {achievement.get('Conditions', 'No conditions available')}")
        self.difficulty_label.config(text=f"Difficulty: {achievement.get('Difficulty', 'Unknown')}")
        self.version_label.config(text=f"Added in Version: {achievement.get('Version', 'Unknown')}")
        self.percent_label.config(text=f"Completion Percent: {achievement.get('Completion Percent', 'Unknown')}")

        requirements_text = ', '.join(achievement.get('Requirements', []))
        dlc_text = ', '.join(achievement.get('DLC Icons', []))
        self.requirements_label.config(text=f"Requirements: {requirements_text}")
        self.dlc_label.config(text=f"Required DLCs: {dlc_text}")

    def next_achievement(self):
        self.index = (self.index + 1) % self.total
        self.show_achievement()


# %80 gpt

settingsData = json.load(open("settings.json"))["Eu4AchievementSelector"]

profile_url = settingsData["my_profile_eu4_achievement_url"]
general_steam_url = settingsData["general_eu4_achievement_steam_url"]
wiki_url = settingsData["eu4_wiki_achievement_url"]

general_steam_achievements = get_general_steam_achievements(general_steam_url)
wiki_achievements = get_wiki_achievements(wiki_url)
steam_achievements = get_steam_achievements(profile_url)

merged_achievements = merge_achievements(steam_achievements, general_steam_achievements, wiki_achievements)

print(f"Total Steam Achievements: {len(steam_achievements)}")
print(f"Total General Steam Achievements: {len(general_steam_achievements)}")
print(f"Total Wiki Achievements: {len(wiki_achievements)}")
print(f"Total Merged Achievements: {len(merged_achievements)}")

root = tk.Tk()
root.title("EU4 Achievements")
root.geometry('600x400')
app = AchievementApp(root, merged_achievements)

root.mainloop()
