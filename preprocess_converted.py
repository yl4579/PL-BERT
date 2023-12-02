# %% [markdown]
# # Notebook for preprocessing Wikipedia (English) dataset

# %% [markdown]
# ### Initilizing phonemizer and tokenizer

# %%
import yaml

config_path = "Configs/config.yml" # you can change it to anything else
config = yaml.safe_load(open(config_path))

# %%
from phonemize import phonemize

# %%
import phonemizer
global_phonemizer = phonemizer.backend.EspeakBackend(language='en-us',
                                                     preserve_punctuation=True,  
                                                     with_stress=True,
                                                     language_switch='remove-flags'
                                                     )

#from transformers import TransfoXLTokenizer
#tokenizer = TransfoXLTokenizer.from_pretrained(config['dataset_params']['tokenizer']) # you can use any other tokenizers if you want to

from transformers import BertTokenizer
tokenizer = BertTokenizer.from_pretrained(config['dataset_params']['multilingual_tokenizer'])
# %% [markdown]
# ### Process dataset

# %%
from datasets import load_dataset
#dataset = load_dataset("wikipedia", "20220301.en")['train'] # you can use other version of this dataset
#dataset = load_dataset("wikipedia", "20220301.ml")['train'] # you can use other version of this dataset
#dataset  = load_dataset("wikipedia", '20231120.ml', beam_runner='DirectRunner')['train']
dataset = load_dataset("wikipedia",  language="ml", date="20231101",beam_runner='DirectRunner')['train']




# %%
root_directory = "./wiki_ml_phoneme" # set up root directory for multiprocessor processing

# %%
import os
num_shards = 50000

def process_shard(i):
    directory = root_directory + "/shard_" + str(i)
    if os.path.exists(directory):
        print("Shard %d already exists!" % i)
        return
    print('Processing shard %d ...' % i)
    shard = dataset.shard(num_shards=num_shards, index=i)
    processed_dataset = shard.map(lambda t: phonemize(t['text'], 
                                                      global_phonemizer, 
                                                      tokenizer,
                                                      language="ml"
                                                      ), 
                                                      remove_columns=['text'],
                                                      )
    if not os.path.exists(directory):
        os.makedirs(directory)
    processed_dataset.save_to_disk(directory)

# %%
from pebble import ProcessPool
from concurrent.futures import TimeoutError

# %% [markdown]
# #### Note: You will need to run the following cell multiple times to process all shards because some will fail. Depending on how fast you process each shard, you will need to change the timeout to a longer value to make more shards processed before being killed.
# 

# %%
max_workers = 3 # change this to the number of CPU cores your machine has 

with ProcessPool(max_workers=max_workers) as pool:
    pool.map(process_shard, range(num_shards), timeout=300)

# %% [markdown]
# ### Collect all shards to form the processed dataset

# %%
from datasets import load_from_disk, concatenate_datasets

output = [dI for dI in os.listdir(root_directory) if os.path.isdir(os.path.join(root_directory,dI))]
datasets = []
for o in output:
    directory = root_directory + "/" + o
    try:
        shard = load_from_disk(directory)
        datasets.append(shard)
        print("%s loaded" % o)
    except:
        continue

# %%
dataset = concatenate_datasets(datasets)
dataset.save_to_disk(config['data_folder'])
print('Dataset saved to %s' % config['data_folder'])

# %%
# check the dataset size
dataset

# %% [markdown]
# ### Remove unneccessary tokens from the pre-trained tokenizer
# The pre-trained tokenizer contains a lot of tokens that are not used in our dataset, so we need to remove these tokens. We also want to predict the word in lower cases because cases do not matter that much for TTS. Pruning the tokenizer is much faster than training a new tokenizer from scratch. 

# %%
from simple_loader import FilePathDataset, build_dataloader

file_data = FilePathDataset(dataset)
loader = build_dataloader(file_data, num_workers=4, batch_size=128)

# %%
special_token = config['dataset_params']['word_separator']

# %%
# get all unique tokens in the entire dataset

from tqdm import tqdm

unique_index = [special_token]
for _, batch in enumerate(tqdm(loader)):
    unique_index.extend(batch)
    unique_index = list(set(unique_index))

# %%
# get each token's lower case

lower_tokens = []
for t in tqdm(unique_index):
    word = tokenizer.decode([t])
    if word.lower() != word:
        t = tokenizer.encode([word.lower()])[0]
        lower_tokens.append(t)
    else:
        lower_tokens.append(t)

# %%
lower_tokens = (list(set(lower_tokens)))

# %%
# redo the mapping for lower number of tokens

token_maps = {}
for t in tqdm(unique_index):
    word = tokenizer.decode([t])
    word = word.lower()
    new_t = tokenizer.encode([word.lower()])[0]
    token_maps[t] = {'word': word, 'token': lower_tokens.index(new_t)}

# %%
import pickle
with open(config['dataset_params']['token_maps'], 'wb') as handle:
    pickle.dump(token_maps, handle)
print('Token mapper saved to %s' % config['dataset_params']['token_maps'])

# %% [markdown]
# ### Test the dataset with dataloader
# 

# %%
from dataloader import build_dataloader, FilePathDataset

tmp = FilePathDataset(dataset, **config['dataset_params'])

for k in range(len(tmp)) :
    data = tmp[k]

train_loader = build_dataloader(dataset, batch_size=32, num_workers=4, dataset_config=config['dataset_params'])

# %%
_, (words, labels, phonemes, input_lengths, masked_indices) = next(enumerate(train_loader))

pass


