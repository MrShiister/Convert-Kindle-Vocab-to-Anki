from ast import alias
from datetime import datetime
from urllib.error import HTTPError
import argparse
import logging
import multiprocessing as mp
import re
import requests
import sqlite3

# get_def returns headword, pronunciation, definition of the given word.
# If the word does not exist in the dictionary, the closest match is used instead.
def get_def(word):
    url = "https://dictionaryapi.com/api/v3/references/collegiate/json/{}".format(word)

    # Attempt 3 times in case of GET failure.
    ok = False
    for _ in range(3):
        try:
            r = requests.get(url, params=params)
            r.raise_for_status()
            json = r.json()
            ok = True
            break
        except HTTPError as err:
            logging.warning("{} HTTPError: {}".format(r.status_code, err))
        except:
            logging.debug(r.text)
    if not ok:
        logging.warning("Cannot retrieve word, skipping: {}".format(word))
        return word, "", ""
            
    # Get Headword
    try:
        headword = json[0]["hwi"]["hw"].replace('*', '')
    except TypeError:
        logging.warning("{}: Definition not found. Searching {} instead...".format(word, json[0]))
        return get_def(json[0])
    logging.debug("Headword: {}".format(headword))

    # Get Pronunciation
    try:
        pronunciation = json[0]["hwi"]["prs"][0]["mw"]
    except:
        pronunciation = ""
    logging.debug("Pronunciation: {}".format(pronunciation))

    # Get Definition
    definition = "; ".join(json[0]["shortdef"])
    logging.debug("Definition: {}".format(definition))

    return headword, pronunciation, definition

# Get the definitions and print to stdout.
def print_def(word):
        headword, pronunciation, definition = get_def(word)
    
        print("         Word: {}".format(word))
        print("     Headword: {}".format(headword))
        print("Pronunciation: {}".format(pronunciation))
        print("   Definition: {}".format(definition))
        print()

        args.outfile.write("{}\t{}\t\t{}\n".format(headword, pronunciation, definition))
        args.outfile.flush()

# print_words is the function called by the subcommand 'test'. It prints the definition of each word to be searched.
def print_words(args):
    logging.info("Searching {} words: {}".format(len(args.word), args.word))

    p = mp.Pool(mp.cpu_count())
    p.map(print_def, args.word)

# get_lookups returns a list of (word, usage) tuples.
def get_lookups(vocabdb, timestamp):
    con = sqlite3.connect(vocabdb)
    cur = con.cursor()

    try:
        cur.execute("""SELECT word, usage
            FROM LOOKUPS
            INNER JOIN WORDS
            ON LOOKUPS.word_key = WORDS.id
            WHERE LOOKUPS.timestamp >= :timestamp""", {"timestamp": timestamp})
    except sqlite3.OperationalError:
        logging.critical("SQLITE Operational Error. Is {} the right file?".format(args.vocabdb))
        raise

    return cur.fetchall()

def write_to_outfile(tuple):
    headword, pronunciation, definition = get_def(tuple[0])
    # Bold the word in the usage sentence.
    usage = re.sub(r'\b{}\b'.format(tuple[0]), "<b>{}</b>".format(tuple[0]), tuple[1])
    logging.debug("Usage: {}".format(usage))
    args.outfile.write("{}\t{}\t{}\t{}\n".format(headword, pronunciation, usage, definition))
    args.outfile.flush()

# export_words is the fuction called by the main command. It writes a tab-separated values file which is meant for importing into Anki. 
def export_words(args):
    # Retrieve the list of (word, usage) tuple from the vocab SQL database file
    wordlist = get_lookups(args.vocabdb, args.start_from)
    logging.info("Searching all words since {}: {} words".format(datetime.fromtimestamp(float(args.start_from)/1000), len(wordlist)))

    p = mp.Pool(mp.cpu_count())

    # Write to specified outfile
    p.map(write_to_outfile, wordlist)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Converts vocab.db from Kindle into a format Anki accepts. Refer to https://github.com/MrShiister/Convert-Kindle-Vocab-to-Anki for full details.")
    parser.add_argument("--log", choices=["debug", "info", "warning", "error", "critical"], default="info", help="Log level. The default level is info.")
    parser.add_argument("-k", "--key", default='04a5d981-0869-42c8-a87c-c8cbfdcfcb56', help="Your dictionaryapi.com API Key")

    parser.add_argument("-o", "--outfile", type=argparse.FileType("w+", encoding="UTF-8"), default="import.tsv", help="Path to outfile")
    parser.add_argument("-d", "--vocabdb", default="./vocab.db", metavar="/path/to/vocab.db", help="Path to vocab.db")
    parser.add_argument("-f", "--start_from", default=0, metavar="epoch_time_in_milli", help="Only find words since the specified Epoch timestamp in milliseconds (13 digits). Useful if you have already used this previously and only want to import new words. e.g. 1571009240989")
    parser.set_defaults(func=export_words)

    subparsers = parser.add_subparsers()
    parser_test = subparsers.add_parser("list", aliases="l", help="Get definition of a list of word(s) and convert into a format Anki accepts.")
    parser_test.add_argument("word", nargs='*', type=str, default=["loosestrife", "cardipnipd", "carte blanche", "outré"], help="Space-separated words to search for the definitions. Use quotes for words with spaces. Leave blank to see sample.")
    parser_test.set_defaults(func=print_words)

    args = parser.parse_args()

    loglevel = getattr(logging, args.log.upper())
    logging.basicConfig(format="[*] {levelname:>8}: {message}", style='{', level=loglevel)

    logging.debug(args)

    params = {'key': args.key}

    args.func(args)