# Convert Kindle Vocab to Anki
## Description
Converts vocab.db from Kindle into a format Anki accepts.

### In Kindle
Your Kindle records down each word you search the meaning of into the database vocab.db, specifically the `lookups` database table. These words can be found in Vocab Builder. The ID and context of where the word was found is stored in `words` table.

### In Anki
A custom format of the cards. It contains 4 fields, namely

|Order|Field Name|Remarks|
|:---:|:---------|:------|
|1    |Word      |The Vocab, which is not necessary the root word|
|2    |Pronunciation |The IPA of the word|
|3    |Example Sentence|The context sentence where you found the word|
|4    |Meaning   |Definition of the word|

### Putting it together
Word and Example Sentence are found in the Kindle database file;
Phonetics and Meaning are queried using a [3rd-party website using Google's Dictionary API](https://googledictionaryapi.eu-gb.mybluemix.net/).

The script takes the ID of the word from `lookups` to find the actual word and its context from `words`, queries the API for phonetics and meaning, and writes the 4 fields, tab-separated. It is technically not a tsv file as quotes are taken as is without escaping.

## Usage
1. Extract `words.csv` and `lookups.csv` from system/vocab.db manually. Each value should be tab-separately (so it's technically a .tsv file)
2. Put the .csv files and the .py script in the same folder.
3. Run .py script.
4. Import the output file through Anki, make a card format with these 4 fields, and import, allowing HTML.

## Bonus! My Anki Vocab Card Fields
### Front Template
```HTML
{{Word}}<br>
{{Pronunciation}}<br>

<hr>
<div class='spoiler'>{{Example Sentence}}</div>
```

### Styling (shared between cards)
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

### Back Template
```HTML
{{Word}}<br>
{{Pronunciation}}<br>

<hr>
{{Example Sentence}}

<hr id=answer>

{{Meaning}}

<div style='color: white;' class='spoiler'>{{Example Sentence}}</div>
```

## Future Work
* Automate extracting tables from database
* Parse the list for new vocabs only
