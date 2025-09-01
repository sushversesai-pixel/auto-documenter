def capitalize_words(text):
    return ' '.join(word.capitalize() for word in text.split())

def remove_duplicates(items):
    return list(set(items))

async def fetch_data(url):
    import asyncio
    await asyncio.sleep(1)
    return f"Data from {url}"