import os



projectName = "849. Maximize Distance to Closest Person && Difficult Medium"

solitions = "Solitions"
csharp = "CSharp"
python = "Python"
cpp = "C++"
c="C"
javascript = "JavaScript"
typescript="TypeScript"
dart="Dart"
readme="README.md"

htmlTemplate = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="index.js"></script>
    <title>Document</title>
</head>
<body>
    
</body>
</html>
"""


def print_large_text(text, color):
    ascii_letters = {
        'A': ["  ##  ",
              " #  # ",
              "#    #",
              "######",
              "#    #",
              "#    #"],
        'B': ["##### ",
              "#    #",
              "##### ",
              "#    #",
              "#    #",
              "##### "],
        'I': ["######",
              "  ##  ",
              "  ##  ",
              "  ##  ",
              "  ##  ",
              "######"],
        'L': ["#     ",
              "#     ",
              "#     ",
              "#     ",
              "#     ",
              "######"],
        'R': ["##### ",
              "#    #",
              "##### ",
              "#  #  ",
              "#   # ",
              "#    #"],
        'S': [" #####",
              "#     ",
              " #####",
              "     #",
              "     #",
              "##### "],
        'U': ["#    #",
              "#    #",
              "#    #",
              "#    #",
              "#    #",
              " #### "],
        'Z': ["######",
              "    # ",
              "   #  ",
              "  #   ",
              " #    ",
              "######"],
        ' ': ["      ",
              "      ",
              "      ",
              "      ",
              "      ",
              "      "],
        'Ş': [" #####",
              "#     ",
              " #####",
              "     #",
              "##### ",
              "  #   "],
    }
    
    # Renk kodları
    color_code = {'green': '\033[92m', 'red': '\033[91m', 'reset': '\033[0m'}

    lines = [""] * 6
    for char in text:
        for i, line in enumerate(ascii_letters.get(char, [" " * 6] * 6)):
            lines[i] += line + "  "

    for line in lines:
        print(f"{color_code[color]}{line}{color_code['reset']}")  # Renkli yazdır


def status(value:bool):
    if value:
        print_large_text("BAŞARILI", "green")
    else:
        print_large_text("BAŞARISIZ", "red")


def process():
    try:
        os.mkdir(projectName)
        os.mkdir(projectName+"/"+solitions)
        os.mkdir(projectName+"/"+solitions+"/"+csharp)
        os.mkdir(projectName+"/"+solitions+"/"+python)
        os.mkdir(projectName+"/"+solitions+"/"+cpp)
        os.mkdir(projectName+"/"+solitions+"/"+c)
        os.mkdir(projectName+"/"+solitions+"/"+javascript)
        os.mkdir(projectName+"/"+solitions+"/"+typescript)
        os.mkdir(projectName+"/"+solitions+"/"+dart)

        open(projectName+"/"+readme, "w+", encoding="utf8").write(f"# {projectName}")
        open(projectName+"/"+solitions+"/"+python+"/"+"Main.py", "w+", encoding="utf8").write(f"# {projectName}")
        open(projectName+"/"+solitions+"/"+cpp+"/"+"Main.cpp", "w+", encoding="utf8").write(f"// {projectName}")
        open(projectName+"/"+solitions+"/"+c+"/"+"Main.c", "w+", encoding="utf8").write(f"// {projectName}")
        open(projectName+"/"+solitions+"/"+javascript+"/"+"Main.js", "w+", encoding="utf8").write(f"// {projectName}")
        open(projectName+"/"+solitions+"/"+javascript+"/"+"index.html", "w+", encoding="utf8").write(f"<!-- {projectName} -->\n{htmlTemplate}")
        open(projectName+"/"+solitions+"/"+typescript+"/"+"Main.ts", "w+", encoding="utf8").write(f"// {projectName}")
        open(projectName+"/"+solitions+"/"+dart+"/"+"Main.dart", "w+", encoding="utf8").write(f"// {projectName}")

        os.chdir(projectName+"/"+solitions+"/"+csharp+"/")
        os.system("dotnet new console")

        status(True)

    except Exception as e: 
        status(False)
        print("Exception:")
        print(e)


if __name__ == "__main__":
    
    process()

        








