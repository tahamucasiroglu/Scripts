import os
import sys

def scan_files_in_folder(folder, ignore_dirs):
    result = []
    for dirpath, dirnames, filenames in os.walk(folder):
        # İstenmeyen klasörleri atla
        dirnames[:] = [d for d in dirnames if d.lower() not in ignore_dirs]
        for filename in filenames:
            if filename.endswith('.cs') or filename.endswith('.json'):
                full_path = os.path.join(dirpath, filename)
                try:
                    with open(full_path, 'r', encoding='utf-8-sig') as file:
                        content = file.read()
                except Exception as e:
                    content = f"Dosya okunurken hata oluştu: {e}"
                result.append(
                    "------------------------------------\n" +
                    f"{full_path}\n" +
                    f"{content}\n" +
                    "------------------------------------\n"
                )
    return result

def scan_project_files_single(root_dir, output_file, ignore_dirs):
    contents = scan_files_in_folder(root_dir, ignore_dirs)
    with open(output_file, 'w', encoding='utf-8-sig') as out_f:
        out_f.write("".join(contents))

def find_projects(root_dir, ignore_dirs):
    projects = {}
    # .csproj dosyalarını arıyoruz
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d.lower() not in ignore_dirs]
        for filename in filenames:
            if filename.endswith('.csproj'):
                project_name = os.path.splitext(filename)[0]
                # Aynı dizinde birden fazla .csproj varsa ilkini alıyoruz
                if dirpath not in projects:
                    projects[dirpath] = project_name
    return projects

def scan_project_files_separate(root_dir, output_dir, ignore_dirs):
    projects = find_projects(root_dir, ignore_dirs)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Her proje için ayrı txt dosyası oluştur
    for proj_dir, proj_name in projects.items():
        contents = scan_files_in_folder(proj_dir, ignore_dirs)
        output_file = os.path.join(output_dir, f"{proj_name}.txt")
        with open(output_file, 'w', encoding='utf-8-sig') as out_f:
            out_f.write("".join(contents))
        print(f"{proj_name} projesi için çıktı: {output_file}")
        
    # Proje dosyalarına ait olmayan dosyaları "misc.txt" içinde toplayalım (isteğe bağlı)
    misc_contents = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d.lower() not in ignore_dirs]
        # Bulunduğu dizinin herhangi bir proje dizini altında olup olmadığını kontrol et
        belongs_to_project = any(os.path.commonpath([dirpath, proj_dir]) == proj_dir for proj_dir in projects.keys())
        if not belongs_to_project:
            for filename in filenames:
                if filename.endswith('.cs') or filename.endswith('.json'):
                    full_path = os.path.join(dirpath, filename)
                    try:
                        with open(full_path, 'r', encoding='utf-8-sig') as file:
                            content = file.read()
                    except Exception as e:
                        content = f"Dosya okunurken hata oluştu: {e}"
                    misc_contents.append(
                        "------------------------------------\n" +
                        f"{full_path}\n" +
                        f"{content}\n" +
                        "------------------------------------\n"
                    )
    if misc_contents:
        misc_output = os.path.join(output_dir, "misc.txt")
        with open(misc_output, 'w', encoding='utf-8-sig') as out_f:
            out_f.write("".join(misc_contents))
        print(f"Projeye ait olmayan dosyalar için çıktı: {misc_output}")

if __name__ == "__main__":
    # Kullanım:
    # Tek dosya modunda:
    #   python script.py <proje_klasoru> <cikti_dosyasi.txt> single
    # Ayrı dosya modunda:
    #   python script.py <proje_klasoru> <cikti_klasoru> separate
    if len(sys.argv) < 4:
        print("Kullanım: python script.py <proje_klasoru> <cikti_dosyasi/klasoru> <mode: single|separate>")
        sys.exit(1)
    
    project_directory = sys.argv[1]
    output_target = sys.argv[2]
    mode = sys.argv[3].lower()
    
    ignore_dirs = {'bin', 'obj', 'migrations', ".vs", ".git", ".github", "wwwroot", "Others", "Logs"}
    
    if mode == "single":
        scan_project_files_single(project_directory, output_target, ignore_dirs)
        print(f"Tarama tamamlandı. Çıktı '{output_target}' dosyasına yazıldı.")
    elif mode == "separate":
        scan_project_files_separate(project_directory, output_target, ignore_dirs)
        print("Tarama tamamlandı. Ayrı dosyalara yazıldı.")
    else:
        print("Geçersiz mod. Lütfen 'single' veya 'separate' olarak belirtin.")
        sys.exit(1)
