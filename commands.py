# commands.py
async def handle_command(message, encrypt_function):
    content = message.content.strip()
    if content.startswith("?helloworld"):
        return await hello_world_command(content, encrypt_function)
    return None


async def hello_world_command(content, encrypt):
    parts = content.split()
    if len(parts) != 2:
        return encrypt("Usage: ?helloworld [language]")

    language = parts[1].lower()

    translations = {
        "english": "Hello World!",
        "spanish": "¡Hola Mundo!",
        "french": "Bonjour le monde!",
        "german": "Hallo Welt!",
        "japanese": "こんにちは世界！",
        "ukrainian": "Привіт, світ!",
    }

    msg = translations.get(language)
    if not msg:
        return encrypt("Unsupported language!")

    return encrypt(msg)
