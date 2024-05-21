import base64


input = "input place here"

encoded_text = base64.b64encode(input.encode()).decode()

print(f"Şifrelenmiş metin: {encoded_text}")

decoded_text = base64.b64decode(encoded_text).decode()

print(f"Geri açılmış hali: {decoded_text}")
