import json
import csv
from urllib.request import urlopen

import logging
import argparse


def get_meaning(json):
    try:
        part_of_speech = list(json["meaning"])[0] # noun/verb/adjective/etc.
        value = json["meaning"][part_of_speech][0]["definition"]
        return value
    except:
        logging.error("Definition not found")
        return "Error: Definition not found"

def get_phonetic(json):
    try:
        value = json["phonetic"]
        return value.strip("/")
    except:
        logging.warning("Phonetic not found")
        return ""

def test_vocab(word):
    link = "https://googledictionaryapi.eu-gb.mybluemix.net/?define={}&lang=en".format(word)
    response = urlopen(link)
    def_json = json.loads(response.read())
    json1 = def_json[0]
    # meaning = get_meaning(def_json[0])
    part_of_speech = list(json1["meaning"])[0] # noun/verb/adjective/etc.
    logging.info("Part of speech: {}".format(part_of_speech))
    value = json1["meaning"][part_of_speech][0]["definition"]
    logging.info("Value: {}".format(value))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Converts vocab.db from Kindle into a format Anki accepts. Refer to README.md for full details.")
    parser.add_argument("-t", "--test", metavar="word", default="Brussels", help="Test a word and quit.")
    parser.add_argument("--log", choices=["debug", "info", "warning", "error", "critical"], default="info", help="Specify log level. The default level is \"info\".")
    args = parser.parse_args()

    loglevel = getattr(logging, args.log.upper())
    logging.basicConfig(format="[*] {levelname:>8}: {message}", style='{', level=loglevel)

    if args.test:
        test_vocab(args.test)
        raise SystemExit
    
    words_dict={}

    # Read words.csv
    with open("WORDS.csv", encoding="UTF-8") as words_csv:
        words_reader = csv.DictReader(words_csv, dialect="excel-tab")
        for row in words_reader:
            words_dict[row["id"]] = row["word"]

    # Read lookups.csv
    with open("Kindle_Vocab.tsv", "w+", encoding="UTF-8") as output:
        with open("LOOKUPS.csv", encoding="UTF-8") as lookups_csv:
            lookups_reader = csv.DictReader(lookups_csv, dialect="excel-tab")
            for row in lookups_reader:
                word_id = row["word_key"]
                word = words_dict[word_id]
                logging.info("Searching: {}".format(word))

                word_nospaces = word.replace(' ', '%20')

                # Scrap Google API
                link = "https://googledictionaryapi.eu-gb.mybluemix.net/?define={}&lang=en".format(word_nospaces)
                logging.debug(link)

                try:
                    response = urlopen(link)
                except:
                    meaning = "Error: Page not found"
                    phonetic = "Error: Page not found"
                    logging.error("Page not found")
                else:
                    def_json = json.loads(response.read())
                    meaning = get_meaning(def_json[0])
                    phonetic = get_phonetic(def_json[0])
                finally:

                    # Process for tsv
                    word_tsv = "{}".format(word)
                    phonetic_tsv = "{}".format(phonetic)
                    eg_tsv = row["usage"].replace(word, "<b>{}</b>".format(word))
                    eg_tsv = eg_tsv.strip('"')

                    logging.debug(word_tsv)
                    logging.debug(phonetic_tsv)
                    logging.debug(eg_tsv)
                    logging.debug(meaning)

                    # Write to Kindle_Vocab
                    output.write("{}\t{}\t{}\t{}\n".format(word_tsv, phonetic_tsv, eg_tsv, meaning))
                    output.flush()

                    logging.debug("")
