import json
import csv
from urllib.request import urlopen

def get_meaning(json):
    part_of_speech = list(json["meaning"])[0] # noun/verb/adjective/etc.
    try:
        value = json["meaning"][part_of_speech][0]["definition"]
        return value
    except:
        return "Error: Definition not found"

def get_phonetic(json):
    try:
        value = json["phonetic"]
        return value.strip("/")
    except:
        return ""

# if __name__ == '__main__':
def do_not_execute():
    link = "https://googledictionaryapi.eu-gb.mybluemix.net/?define=Brussels&lang=en"
    response = urlopen(link)
    def_json = json.loads(response.read())
    meaning = get_meaning(def_json[0])
    

# def do_not_execute():
if __name__ == '__main__':
    words_dict={}

    # Read words.csv
    with open("words.csv", encoding="UTF-8") as words_csv:
        words_reader = csv.DictReader(words_csv, dialect="excel-tab")
        for row in words_reader:
            words_dict[row["id"]] = row["word"]

    # Read lookups.csv
    with open("Kindle_Vocab_test.tsv", "w+", encoding="UTF-8") as output:
        with open("lookups.csv", encoding="UTF-8") as lookups_csv:
            lookups_reader = csv.DictReader(lookups_csv, dialect="excel-tab")
            for row in lookups_reader:
                word_id = row["word_key"]
                word = words_dict[word_id]
                print(word)

                word_nospaces = word.replace(' ', '%20')

                # Scrap Google API
                link = "https://googledictionaryapi.eu-gb.mybluemix.net/?define={}&lang=en".format(word_nospaces)
                print(link)

                try:
                    response = urlopen(link)
                except:
                    meaning = "Error: Page not found"
                    phonetic = "Error: Page not found"
                else:
                    def_json = json.loads(response.read())
                    meaning = get_meaning(def_json[0])
                    phonetic = get_phonetic(def_json[0])
                finally:

                    # Process for tsv
                    word_tsv = "<big class=\"word\">{}</big>".format(word)
                    phonetic_tsv = "<small class=\"ipa\">{}</small>".format(phonetic)
                    eg_tsv = row["usage"].replace(word, "<b>{}</b>".format(word))
                    eg_tsv = eg_tsv.strip('"')

                    print(word_tsv)
                    print(phonetic_tsv)
                    print(eg_tsv)
                    print(meaning)

                    # Write to Kindle_Vocab
                    output.write("{}\t{}\t{}\t{}\n".format(word_tsv, phonetic_tsv, eg_tsv, meaning))
                    output.flush()

                    print()
