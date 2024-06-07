import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageTk
from io import BytesIO
import tkinter as tk

profile_url = 'https://steamcommunity.com/profiles/76561198997983717/stats/236850/achievements/'
general_steam_url = 'https://steamcommunity.com/stats/236850/achievements'
wiki_url = 'https://eu4.paradoxwikis.com/Achievements'

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

steam_achievements = get_steam_achievements(profile_url)

# Genel Steam başarımlarını çekmek için fonksiyon
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

general_steam_achievements = get_general_steam_achievements(general_steam_url)

def get_wiki_achievements(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    achievement_rows = soup.select('table.wikitable tr')

    achievements = []

    for row in achievement_rows[1:]:  
        cols = row.find_all('td')
        if len(cols) > 3:  
            title = cols[0].text.strip()
            description = cols[1].text.strip()
            version = cols[2].text.strip()
            difficulty = cols[3].text.strip()
            achievements.append({
                'Title': title,
                'Wiki Description': description,
                'Version': version,
                'Difficulty': difficulty
            })

    return achievements


wiki_achievements = get_wiki_achievements(wiki_url)

def merge_achievements(steam_achievements, general_achievements, wiki_achievements):
    merged_achievements = []

    for steam_achievement in steam_achievements:
        if not steam_achievement['Unlock Time']:  
            general_achievement = next((ga for ga in general_achievements if ga['Title'] == steam_achievement['Title']), None)
            wiki_achievement = next((wa for wa in wiki_achievements if wa['Title'] == steam_achievement['Title']), None)

            if general_achievement:
                steam_achievement['Completion Percent'] = general_achievement['Completion Percent']
            if wiki_achievement:
                steam_achievement['Wiki Description'] = wiki_achievement['Wiki Description']
                steam_achievement['Version'] = wiki_achievement['Version']
                steam_achievement['Difficulty'] = wiki_achievement['Difficulty']

            merged_achievements.append(steam_achievement)

    return merged_achievements

merged_achievements = merge_achievements(steam_achievements, general_steam_achievements, wiki_achievements)

# Hata ayıklama için çıktı ekleyelim
print(f"Total Steam Achievements: {len(steam_achievements)}")
print(f"Total General Steam Achievements: {len(general_steam_achievements)}")
print(f"Total Wiki Achievements: {len(wiki_achievements)}")
print(f"Total Merged Achievements: {len(merged_achievements)}")

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
        self.wiki_description_label.config(text=f"Wiki Description: {achievement.get('Wiki Description', 'No description available')}")
        self.difficulty_label.config(text=f"Difficulty: {achievement.get('Difficulty', 'Unknown')}")
        self.version_label.config(text=f"Added in Version: {achievement.get('Version', 'Unknown')}")
        self.percent_label.config(text=f"Completion Percent: {achievement.get('Completion Percent', 'Unknown')}")

    def next_achievement(self):
        self.index = (self.index + 1) % self.total
        self.show_achievement()

root = tk.Tk()
root.title("EU4 Achievements")
root.geometry('600x300')
app = AchievementApp(root, merged_achievements)

root.mainloop()
