# Convert Kindle Vocab to Anki
## Description
The purpose of this project is for porting the vocabs you learned from your Kindle to [Anki](https://apps.ankiweb.net).
In particular, this script converts `vocab.db` into a format Anki can understand and import.

### In Kindle
Your Kindle records down each word you search for and you can review them in Vocab Builder. These words are written into the database `kindle:/system/vocab.db`, specifically in the `LOOKUPS` database table. The ID and context of the word are cross-referenced to the `WORDS` database table.

### In Anki
Create a new note type for Anki for the import.
1. Pick `Basic (and reversed card)`.
2. In the `Fields...` options, adjust the fields to:

|Order|Field Name|Explanation|
|:---:|:---------|:------|
|1    |Word      |The Vocab, which is not necessary the root word|
|2    |Pronunciation |The IPA of the word|
|3    |Example Sentence|The context sentence where you found the word|
|4    |Meaning   |Definition of the word|

3. In the `Cards...` option, the card templates are as follows (copy and paste them, they work as is).

#### Front Template
```HTML
{{Word}}<br>
{{Pronunciation}}<br>

<hr>
<div class='spoiler'>{{Example Sentence}}</div>
```

#### Styling (shared between cards)
```HTML
.card {
 font-family: arial;
 font-size: 20px;
 text-align: center;
 color: black;
 background-color: white;
}

.spoiler { 
  color: white;
}

.spoiler:hover{
  color: black;
}
```

#### Back Template
```HTML
{{Word}}<br>
{{Pronunciation}}<br>

<hr>
{{Example Sentence}}

<hr id=answer>

{{Meaning}}

<div style='color: white;' class='spoiler'>{{Example Sentence}}</div>
```


### Putting it together
`Word` and `Example Sentence` are extracted from the Kindle database file;
`Phonetics` and `Meaning` are queried using a [3rd-party website using Google's Dictionary API](https://googledictionaryapi.eu-gb.mybluemix.net/).

The script takes the ID of the word from `LOOKUPS` to find the actual word and its context from `WORDS`, queries the API for phonetics and meaning, and writes the 4 fields, tab-separated. It is not exactly a `.tsv` file as quotes are taken as is without escaping.

## Usage
1. Export `WORDS.csv` and `LOOKUPS.csv` from `system/vocab.db` manually.
	- Keep column names in the first line for both files.
	- Pick 'Tab' as the Field Separator.
	- Pick " as the quote character.
2. Set up your Anki with the new note type as above.
3. Put `WORDS.csv`, `LOOKUPS.cv` and `convert_db_to_tsv.py` in the same folder.
4. Run `convert_db_to_tsv.py`. Use `--help` for usage information.
5. Import `Kindle_Vocab.tsv` in Anki, pick the note type you made, and allow HTML in fields.

### Bugs
The Google API does not contain information for all words. `Error:` is filled instead so you can find them easily.
I recommend importing all the words, including the errorneous ones, and then filter "error" in Anki and fix them.

## Ideas for Future Work
* Automate extracting tables from database
* Using Merriam-webster dictionary's API
* Parse the list for new vocabs only

