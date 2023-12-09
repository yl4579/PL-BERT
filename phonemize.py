import string
from text_normalize import normalize_text, remove_accents

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


def phonemize(text, global_phonemizer, tokenizer):
    text = normalize_text(remove_accents(text))
    words = tokenizer.tokenize(text)
    
    phonemes_bad = [global_phonemizer.phonemize([word], strip=True)[0] if word not in string.punctuation else word for word in words]
    input_ids = []
    phonemes = []
    
    for i in range(len(words)):
        word = words[i]
        phoneme = phonemes_bad[i]
        
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
                input_ids.append(tokenizer.encode(word.replace('@', ''))[0])
                continue

        input_ids.append(tokenizer.encode(word)[0])
        phonemes.append(phoneme)
        
    assert len(input_ids) == len(phonemes)
    return {'input_ids' : input_ids, 'phonemes': phonemes}

if __name__ == '__main__' :
    from transformers import TransfoXLTokenizer
    tname = "transfo-xl-wt103"
    tokenizer = TransfoXLTokenizer.from_pretrained(tname) # you can use any other tokenizers if you want to

    import phonemizer
    global_phonemizer = phonemizer.backend.EspeakBackend(language='en-us', preserve_punctuation=True,  with_stress=True)
   
    text = 'hello my dear did you get the wrong @number 12 12.5'
    text = 'hello from (1200 - 1230 - 1240)'
    text = 'ദേശീയോദ്യാനങ്ങൾ സംരക്ഷിതപ്രദേശങ്ങളാണ്.'
    dd = phonemize(text, global_phonemizer, tokenizer)
    pass

