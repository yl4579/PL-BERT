import string
from text_normalize import normalize_text, remove_accents, is_malayalam

special_mappings = {
    "a": "ɐ",
    "'t": 't',
    "'ve": "v",
    "'m": "m",
    "'re": "ɹ",
    "d": "d",
    'll': "l",
    "n't": "nt",
    "'ll": "l",
    "'d": "d",
    "'": "ʔ",
    "wasn": "wˈɒzən",
    "hasn": "hˈæzn",
    "doesn": "dˈʌzən",
}

def issubword(word) : 
    return word.startswith('##')

def phonemize_word(global_phonemizer, word) : 
    # removing subword indicator ## from the string before phonemizing 
    if issubword(word) : 
        word = word[2:]

    phoneme = global_phonemizer.phonemize([word], strip=True)[0]

    if len(word) ==1 and is_malayalam(word) : 
        '''
        for single character unicode, epspeak ng is returning the language prefix
        see issue : https://github.com/bootphon/phonemizer/issues/160
        removing the prefix "mæleɪˈɑːləm" 
        TODO : how to make it generic for any langauge
        '''
        phoneme = phoneme[11:]
    return phoneme

def phonemize(text, global_phonemizer, tokenizer,language='en'):
    text = normalize_text(remove_accents(text),language)
    words = tokenizer.tokenize(text)
    ids = tokenizer.encode(text)[1:-1]
    
    phonemes_bad = [ phonemize_word(global_phonemizer, word) if word not in string.punctuation else word for word in words]
    input_ids = []
    phonemes = []
    
    for i in range(len(words)):
        word = words[i]
        phoneme = phonemes_bad[i]
        id = ids[i]
        
        for k, v in special_mappings.items():
            if word == k:
                phoneme = v
                break
        
        # process special cases (NOT COMPLETE)
        
        if word == "'s":
            if i > 0:
                if phonemes[i - 1][-1] in ['s', 'ʃ', 'n', ]:
                    phoneme = "z"
                else:
                    phoneme = "s"
                    
        if i != len(words) - 1:
            if words[i+1] == "'t":
                if word == "haven":
                    phoneme = "hˈævn"
                if word == "don":
                    phoneme = "dˈəʊn"
        
        if word == "the": # change the pronunciations before voewls
            if i < len(words):
                next_phoneme = phonemes_bad[i + 1].replace('ˈ', '').replace('ˌ', '')
                if next_phoneme[0] in 'ɪiʊuɔɛeəɜoæʌɑaɐ':
                    phoneme = "ðɪ"
                    
        if word == "&": 
            if i > 0 and i < len(words):
                phoneme = "ænd"
                
        if word == "A": # capital "a"
            if i > 0:
                if words[i - 1] == ".":
                    phoneme = "ɐ"
                    
        if "@" in word and len(word) > 1: # remove "@"
            if "@" in word and len(word) > 1:
                phonemes.append(word.replace('@', ''))
                input_ids.append(tokenizer.encode(word.replace('@', ''))[1])
                continue

        input_ids.append(id)
        phonemes.append(phoneme)
        
    assert len(input_ids) == len(phonemes)
    return {'input_ids' : input_ids, 'phonemes': phonemes}

if __name__ == '__main__' :
    from transformers import TransfoXLTokenizer
    tname = "transfo-xl-wt103"
    tokenizer = TransfoXLTokenizer.from_pretrained(tname) # you can use any other tokenizers if you want to

    from transformers import BertTokenizer
    tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')

    import phonemizer
    global_phonemizer = phonemizer.backend.EspeakBackend(language='en-us', preserve_punctuation=True,  with_stress=True,language_switch='remove-flags')
   
    text = 'hello my dear did you get the wrong @number 12 12.5'
    #text = 'ഇവരുമായി സഹകരിക്കില്ലെന്നാണ് സംഘടയുടെ തീരുമാനം.'
    #text = 'നെഗറ്റീവ് എനർജി’ വിവാദം !: ശിശുസംരക്ഷണ ഓഫീസർക്ക് സസ്പെൻഷൻ!'
    from datasets import load_dataset
    dataset = load_dataset("wikipedia",  language="ml", date="20231101",beam_runner='DirectRunner')['train']
    text = dataset[1]['text']
    text = 'hello from (1200 - 1230 - 1240)'
    dd = phonemize(text, global_phonemizer, tokenizer, language="ml")
    pass

