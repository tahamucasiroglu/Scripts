import os


mission = "kullanıcı kayıt ve giriş işlemlerini yapıyordum yarıda kaldım. Tamamlar mısın. "



prompt = f"""
Komutlar:
Sana aşağıda Backend ve Frontend kodları vereceğim. 
Kodları ######################### ile ayırdım.
Kodların başına dosya yollarını verdim. Bu düşünmeni kolaylaştırsın diye verildi.
Eksik bilgiler olursa cevap vermeden önce bu bilgileri iste. Bu sayede bende bir dahakine dikkat ederim. Sende düzgün cevap üretirsin.
Backend Visual Studio üzerinde .NET 8 ile kodlandı.
Frontend React 18 ile kodlandı. Eski React için kullanılan 'npx create-react-app my-app' syntax kullanılmıyor. Vite gibi aracılar kullanılıyor. Bu değişiklik sadece örnek diğer kodlar içinde versiyona dikkat ederek cevap ver.
Proje için vereceğin kodlarda dikkat etmen gereken konular
- api katmanı sadece api yönetimi barındıracak. Controller yapısı sadece gelen veriyi servis katmanına iletecek. Yazdığım kodlardan anlarsın.
- servis katmanında veritabanı işleri database serviste olacak. servis yapısında tüm class yapıları bir interface ile işaretlenecek. örneğin UserService sınıfı hem IService hemde IUserService interface yapısına sahip. 
- Eğer servis görevinde fakat veritabanı olmayan işler eklenecek ise yeni servis olarak servis katmanına ekleriz.
- Infrasructure yapısı servisten gelen komutların hedef ile iletişim kurduğu yer. Örneğin veritabanına sorgu yapılacağı zaman isteklerin ve verilerin doğruluğu serviste bakıldıktan sonra veritabanına erişip sorguyu yapan katman burasıdır. Ayrıca ek servisler oldukça hedef yerlere sorguları buradan götürebiliriz.
- Application katmanında DTO dönüşümü için mapper ve doğrulama için fluent var burada uygulama yapacak işler olacak. örneğin tüm gelen verileri şifreleyecek olursan onun kodları burada ek proje olmalı. Bir yere yada tüm projeye içeride yapıalcak uygulamalar burada olacak.
- Domain içinde projenin kök dosyaları olacak. her yerden erişilecek sınıflar olacak. 
- Verdiğim örnekler sana anlamlı gelmemiş olabilir. Kısaca projemdeki mimariye uygun kodlarla cevap ver. 
- mimaride anlamadığın kısımları kesinlikle sor ve ona göre bende kendimi düzelteyim.
- Frontend katmanında  src içinde çeşitli parçalamalar yaptım. Burada mimari açık ona göre cevaplar ver ek sayfalarda klasörleme methodlarını koru.
- Son sürümlerle çalışmaktayım. İnternetten araştırma yapman ve kendindeki eski veriler yerine neler geldi öğrenmen iyi olabilir.
- veritabanı olarak microsoft sql servisi kullandım.



açıklama sırasında önce yöntemi ve mantığı bana açıkla. sonrasında kodları verirken sadece değişen yerleri değil. O sayfadaki tüm kodları değişmiş şekilde tekrar ver.
Yapı bozulmadan vermeyi unutma. Yeni yapıları klasörle mimariye uygun şekilde.


Birazdan görevini söğleyeceğim. Görevini baştan sona tek seferde tamamlamaya çalış. Eğer bu konuda zorlanırsan belirt. Görevini yaparken kodların güncelliğini ve çalışırlığına dikkat et. Eğer konu ile alakalı projede gelişime müsait benzer konu veya konular olursa sonra söylersen sevinirim. Alternatif yollar varsa onuda söylersen sevinirim.
Görevin:
{mission}



"""



def list_all_files_with_path(directory):
    file_paths = []
    for foldername, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            file_path=file_path.replace("\\", "/")
            file_paths.append(file_path)
    return file_paths

def GetAllCodes():
    backendDir = "YazilimciPazari.Backend/"
    backendDirList = os.listdir(backendDir)
    backendDirList.remove(".vs")
    backendDirList.remove("YazilimciPazari.Backend.sln")

    backendAllDirList = []

    for i in backendDirList:
        if i.endswith(".cs") or i.endswith(".json"):
            backendAllDirList.append(backendDir+i)
        else:
            subbackendListDir = os.listdir(backendDir + i + "/")
            subbackendListDir.remove("bin")
            subbackendListDir.remove("obj")
            subbackendListDir.remove(i+".csproj")
            for j in subbackendListDir:
                if j.endswith(".cs") or j.endswith(".json"):
                    backendAllDirList.append(backendDir + i + "/" + j)
                else:
                    for k in list_all_files_with_path(backendDir + i + "/" + j):
                        backendAllDirList.append(k)



    frontendDir = "YazilimciPazari.Frontend/"
    frontendDirList = os.listdir(frontendDir)
    frontendDirList.remove("node_modules")
    frontendDirList.remove(".gitignore")

    frontenAllDirList:list[str] = []

    for i in frontendDirList:
        if i.count(".") != 0:
            frontenAllDirList.append(frontendDir + i)
        else:
            subfrontendListDir = list_all_files_with_path(frontendDir + i)
            for j in subfrontendListDir:
                frontenAllDirList.append(j)



    with open("For GPT.txt", "w+", encoding="utf-8") as output:
        try:
            global prompt
            output.write(prompt)
            output.write("Backend \n\n\n" + "#"*25 + "\n")
            for i in backendAllDirList:
                codeText = open(i, "r", encoding="utf-8").read()
                output.write(i+"\n\n\n"+codeText[1:]+"\n\n\n"+"#"*25+"\n\n\n")
            
            output.write("Frontend \n\n\n" + "#"*25)
            for i in frontenAllDirList:
                if i.startswith("YazilimciPazari.Frontend/public/"):
                    output.write(i+"#"*25+"\n\n\n")
                else:
                    codeText = open(i, "r", encoding="utf-8").read()
                    output.write(i+"\n\n\n"+codeText[1:]+"\n\n\n"+"#"*25+"\n\n\n")
        except :
            print(i + " dosyasında hata var Hata:\n")
            raise


    











if __name__ == "__main__":
    GetAllCodes()