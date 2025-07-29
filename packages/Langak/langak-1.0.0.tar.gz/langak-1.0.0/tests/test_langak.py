from langak import detect_language

def test_language(text):
    lang = detect_language(text)
    print(f"Текст: {text}")
    print(f"Определённый язык: {lang}\n")

if __name__ == "__main__":
    test_language("Привет как дела")
    test_language("Hello how are you")
    test_language("你好世界")
    test_language("123456")
