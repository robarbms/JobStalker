import re

# Helper function that checks if a word is in a string
def word_in_text(word: str, text: str):
    replace_chars = [r"\.", r"\,", r";", r"\:", r"\-", r"_", r"/", r"\\"]
    def check(str):
        return re.search(r"\W" + re.escape(str) + r"\W", text, re.IGNORECASE)
    
    # Check for alternate terms
    if re.search(r"\(", word) is not None:
        for term in re.findall(r"\((.*?)\)", word):
            if check(term) is not None:
                return True
        word = re.sub(r" *\(.*\)", "", word)
    exists = check(word)
    if exists is not None:
        return True
    for ch in replace_chars:
        if re.search(ch, word) is not None:
            word_spaced = re.sub(ch, " ", word)
            word_trunc = re.sub(ch, "", word)
            exists = check(word_spaced) or check(word_trunc)
            if exists is not None:
                return True
    return False
    
# Returns a list of keywords found in a text string
def get_keywords(text: str, keyword_list):
    keywords = set()

    for category in keyword_list:
        name = category['name']
        if word_in_text(name, text):
            keywords.add(name)

        for key in category:
            if key != 'name' and key != 'type':
                for item in category[key]:
                    if word_in_text(item['name'], text):
                        keywords.add(item['name'])

                        # if 'creator' in item:
                        #     if word_in_text(item['creator'], text):
                        #         keywords.add(item['creator'])

                        if 'versions' in item:
                            for version in item['versions']:
                                if word_in_text(version, text):
                                    keywords.add(version)
        
    return list(keywords)
