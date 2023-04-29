import re

def create_id_name_hashmaps(messages):
    print('MESSAGES')
    print(messages)
    name_to_id = {f'@{message.name}': f'<@{message.id}>' for message in messages}
    id_to_name = {f'<@{message.id}>': f'@{message.name}' for message in messages}
    return name_to_id, id_to_name

def replace_string(text, dictionary):
    pattern = re.compile("|".join(map(re.escape, dictionary.keys())))
    return pattern.sub(lambda m: dictionary[m.group()], text)