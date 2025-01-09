import random
import GirlNameList, BoyNameList, SurnameList



def GetRandomBoy():
    return BoyNameList.BoyNames[random.randint(0, BoyNameList.BoyNames.__len__())]

def GetRandomGirl():
    return GirlNameList.GirlNames[random.randint(0, GirlNameList.GirlNames.__len__())]

def GetRandomSurname():
    return SurnameList.Surnames[random.randint(0, SurnameList.Surnames.__len__())]

def GetRandomBoyNames(count:int, doubleNameChance = 0.3):
    result:list[str] = []
    for i in range(count):
        if random.random() < doubleNameChance:
            result.append(f"{GetRandomBoy()} {GetRandomBoy()} {GetRandomSurname()}")
        else:
            result.append(f"{GetRandomBoy()} {GetRandomSurname()}")
    return result

def GetRandomGirlNames(count:int, doubleNameChance = 0.3):
    result:list[str] = []
    for i in range(count):
        if random.random() < doubleNameChance:
            result.append(f"{GetRandomGirl()} {GetRandomGirl()} {GetRandomSurname()}")
        else:
            result.append(f"{GetRandomGirl()} {GetRandomSurname()}")
    return result


def GetRandomNames(boyCount:int, girlCount:int, suffle:bool, doubleNameChance = 0.3):
    
    boyResult:list[str] = GetRandomBoyNames(boyCount, doubleNameChance)
    girlResult:list[str] = GetRandomGirlNames(girlCount, doubleNameChance)
    result = boyResult + girlResult
    if suffle:
        random.shuffle(result)
    return result


if __name__ == "__main__":
    result = GetRandomNames(10,10,True, 0.1)
    for res in result:
        print(res)






