Readme dahil kodlarda gpt ile hazırladım. raspide çalıştıracağım kendime özgü todo app yapmak istedim raspiye bağlanıp görev eklememek içinde basit güvenlik olmayan client hazırladım. 


# Görev Yönetim Uygulaması

Bu proje, PyQt5 ve Flask kullanarak bir görev yönetim uygulaması ve istemci uygulaması oluşturur. Kullanıcılar görev ekleyebilir, düzenleyebilir, silebilir ve tamamlanan görevleri görüntüleyebilir.

## Gereksinimler

- Python 3.x
- PyQt5
- Flask
- Requests

## Kurulum

Gereksinimleri yüklemek için:

```sh
pip install PyQt5 Flask requests
```

## Sunucu Uygulaması

### Çalıştırma

Sunucu uygulamasını çalıştırmak için:

```sh
python Server.py
```

Sunucu, varsayılan olarak tüm ağ arayüzlerinde (0.0.0.0) 5000 numaralı portta dinleyecektir.

### Özellikler

- Görev ekleme
- Görev düzenleme
- Görev tamamlama
- Görev silme
- Tamamlanan görevleri görüntüleme
- Hatırlatma ve bitiş zamanı geldiğinde pop-up uyarıları

## İstemci Uygulaması

### Çalıştırma

İstemci uygulamasını çalıştırmak için:

```sh
python Client.py
```

### Kullanım

1. İstemci uygulamasını başlatın.
2. Sunucu IP adresini girin.
3. Görev bilgilerini doldurun ve "Görev Ekle" butonuna tıklayın.

## Lisans

Bu proje MIT Lisansı ile lisanslanmıştır.

---

# Task Management Application

This project creates a task management application and client application using PyQt5 and Flask. Users can add, edit, delete, and view completed tasks.

## Requirements

- Python 3.x
- PyQt5
- Flask
- Requests

## Installation

To install the required packages:

```sh
pip install PyQt5 Flask requests
```

## Server Application

### Running

To run the server application:

```sh
python Server.py
```

The server will listen on all network interfaces (0.0.0.0) on port 5000 by default.

### Features

- Add tasks
- Edit tasks
- Complete tasks
- Delete tasks
- View completed tasks
- Pop-up alerts for reminder and due times

## Client Application

### Running

To run the client application:

```sh
python Client.py
```

### Usage

1. Start the client application.
2. Enter the server IP address.
3. Fill in the task details and click the "Add Task" button.