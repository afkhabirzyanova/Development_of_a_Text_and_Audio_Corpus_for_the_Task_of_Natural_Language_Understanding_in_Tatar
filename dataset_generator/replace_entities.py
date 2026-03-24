import random
from entities import (
    restaurants,
    cities,
    movies,
    cinemas,
    paintings,
    artists,
    albums,
    songs,
    books,
    playlists
)

ENTITY_MAP = {
    "restaurant_name": restaurants,
    "location": cities,
    "movie_name": movies,
    "object_name": books,
    "artist": artists,
    "album": albums,
    "song": songs,
    "track": songs,
    "music_item": songs,
    "entity_name": songs,
    "playlist": playlists
}


COUNTRY_ROOTS = [

"кыргыз",
"бартелем",
"нигер",
"зимбабв",
"сальвадор",
"аргентин",
"уганд",
"тунис",
"нидерланд",
"макао",
"зеланд",
"панам",
"румын",
"фидж",
"казахстан",
"колумб",
"иордан",
"бангладеш",
"суринам",
"сауд",
"сомал",
"доминик",
"оман",
"камерун",
"япон",
"джерс",
"португал",
"литов",
"намиб",
"албан",
"франц",
"кен",
"грец",
"мальдив",
"бермуд",
"норвег",
"аруб",
"гаит",
"белорус",
"туркмен",
"кипр",
"гайан",
"гуам",
"наур",
"тувал",
"гондурас",
"афган",
"йемен",
"исланд",
"латв",
"гвин",
"сахар",
"армян",
"багам",
"ган",
"бурунд",
"таиланд",
"белиз",
"егип",
"мал",
"лихтеншт",
"чех",
"монак",
"австр",
"таджикистан",
"кит",
"канад",
"судан",
"никараг",
"черногор",
"антаркт",
"либер",
"мадагаскар",
"словен",
"кувейт",
"барбад",
"ирланд",
"люксембург",
"финлянд",
"бразил",
"гамб",
"гренад",
"гренланд",
"лесот",
"мавритан",
"мьянм",
"непал",
"африк",
"итал",
"мальт",
"америк",
"монгол",
"босн",
"ирак",
"сенегал",
"израил",
"филиппин",
"руанд",
"бутан",
"дат",
"бенин",
"азербайджан",
"кост",
"ботсван",
"габон",
"перу",
"индонез",
"катар",
"швед",
"шри",
"пакистан",
"уругва",
"африк",
"мозамбик",
"украин",
"андорр",
"эстон",
"австрал",
"маршалл",
"инд",
"венгр",
"бельг",
"серб",
"сингапур",
"замб",
"джибут",
"бахрейн",
"герман",
"анголь",
"гвин",
"польш",
"оаэ",
"комор",
"сейшел",
"гватемал",
"папуа",
"узбекистан",
"куб",
"испан",
"груз",
"мексик",
"словаки",
"алжир",
"конго",
"кирибат",
"ливан",
"марок",
"швейцар",
"эфиоп",
"нигер",
"ямайк",
"чил",
"камбодж",
"болгар",
"хорват",
"малайз"
]


VOWELS_FRONT = "әөүеи"
VOWELS_BACK = "аоуы"


CASE_SUFFIX = {
    "Acc": ("ны","не"),
    "Dat": ("га","гә"),
    "Loc": ("да","дә"),
    "Abl": ("дан","дән"),
    "Gen": ("ның","нең")
}


def read_conll(path):

    sentences = []
    sentence = []

    with open(path, encoding="utf8") as f:

        for line in f:

            line=line.rstrip()

            if line=="":
                if sentence:
                    sentences.append(sentence)
                    sentence=[]
                continue

            sentence.append(line)

        if sentence:
            sentences.append(sentence)

    return sentences


def write_conll(sentences,path):

    with open(path,"w",encoding="utf8") as f:

        for sentence in sentences:

            for line in sentence:
                f.write(line+"\n")

            f.write("\n")


def normalize_entity(entity):

    if isinstance(entity,str):
        return entity.split()

    return entity


def detect_case_suffix(word):

    if word.endswith(("ның","нең")):
        return "Gen"

    if word.endswith(("ны","не")):
        return "Acc"

    if word.endswith(("га","гә")):
        return "Dat"

    if word.endswith(("да","дә")):
        return "Loc"

    if word.endswith(("дан","дән")):
        return "Abl"

    return None


def get_case(word):

    return detect_case_suffix(word)


def apply_case(word,case):

    if case not in CASE_SUFFIX:
        return word

    last_vowel=None

    for c in reversed(word):

        if c in VOWELS_FRONT+VOWELS_BACK:
            last_vowel=c
            break

    if not last_vowel:
        return word

    front=last_vowel in VOWELS_FRONT

    suffix=CASE_SUFFIX[case][1 if front else 0]

    return word+suffix


def is_country(word):

    word_lower=word.lower()

    for root in COUNTRY_ROOTS:
        if word_lower.startswith(root):
            return True

    return False


def replace_country(word):

    if not is_country(word):
        return word

    case=get_case(word)

    new_word="Россия"

    if case:
        new_word=apply_case(new_word,case)

    return new_word


def normalize_temperature(word):

    if "фаренг" in word.lower() or "фаринг" in word.lower():
        return "цельсий"

    return word


def process(sentences):

    new_sentences=[]

    for sentence in sentences:

        new_sentence=process_sentence(sentence)

        new_sentences.append(new_sentence)

    return new_sentences


def process_sentence(sentence):

    meta=[]
    tokens=[]

    for line in sentence:

        if line.startswith("#"):
            meta.append(line)
            continue

        parts=line.split()

        token=parts[1]
        tag=parts[-1]

        tokens.append([token,tag])

    result=[]

    i=0

    while i<len(tokens):

        token,tag=tokens[i]

        if tag.startswith("B-"):

            entity=tag[2:]

            j=i+1

            while j<len(tokens) and tokens[j][1].startswith("I-") and tokens[j][1][2:]==entity:
                j+=1

            if entity in ENTITY_MAP:

                new_entity=normalize_entity(random.choice(ENTITY_MAP[entity]))

                old_words=[tokens[k][0] for k in range(i,j)]

                playlist_suffix=None
                district_suffix=None

                for w in old_words:

                    if "плейлист" in w:
                        playlist_suffix=w

                    if "район" in w:
                        district_suffix=w

                old_word=tokens[j-1][0]

                case=get_case(old_word)

                if case:
                    new_entity[-1]=apply_case(new_entity[-1],case)

                if playlist_suffix:
                    new_entity.append(playlist_suffix)

                if district_suffix:
                    new_entity.append(district_suffix)

                for k,word in enumerate(new_entity):

                    if k==0:
                        result.append((word,"B-"+entity))
                    else:
                        result.append((word,"I-"+entity))

            else:

                for k in range(i,j):
                    result.append(tuple(tokens[k]))

            i=j

        else:

            token=normalize_temperature(token)
            token=replace_country(token)

            result.append((token,tag))

            i+=1


    new_sentence=[]
    tokens_for_text=[]

    for idx,(token,tag) in enumerate(result,start=1):

        tokens_for_text.append(token)

        new_sentence.append(f"{idx} {token} {tag}")


    new_meta=[]

    for line in meta:

        if line.startswith("# text"):
            new_meta.append("# text: "+" ".join(tokens_for_text))
        else:
            new_meta.append(line)


    return new_meta+new_sentence


if __name__=="__main__":

    sentences=read_conll("/content/drive/MyDrive/dataset_generator/valid_tat_adapted.conll")

    new_sentences=process(sentences)

    write_conll(new_sentences,"output.conll")