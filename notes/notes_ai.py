KEYWORDS = {
    "python": "dev",
    "esp32": "iot",
    "prova": "faculdade",
    "sistemas operacionais": "faculdade",
}

def sugerir_tags(texto):
    tags = set()

    texto_lower = texto.lower()

    for palavra, tag in KEYWORDS.items():
        if palavra in texto_lower:
            tags.add(tag)

    return list(tags)


def detectar_evento(texto):
    if "prova" in texto.lower():
        return "Evento detectado: possível prova"
    return None