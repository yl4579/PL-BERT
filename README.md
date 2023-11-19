# Phoneme-Level BERT for Enhanced Prosody of Text-to-Speech with Grapheme Predictions

### Yinghao Aaron Li, Cong Han, Xilin Jiang, Nima Mesgarani

> Large-scale pre-trained language models have been shown to be helpful in improving the naturalness of text-to-speech (TTS) models by enabling them to produce more naturalistic prosodic patterns. However, these models are usually word-level or sup-phoneme-level and jointly trained with phonemes, making them inefficient for the downstream TTS task where only phonemes are needed. In this work, we propose a phoneme-level BERT (PL-BERT) with a pretext task of predicting the corresponding graphemes along with the regular masked phoneme predictions. Subjective evaluations show that our phoneme-level BERT encoder has significantly improved the mean opinion scores (MOS) of rated naturalness of synthesized speech compared with the state-of-the-art (SOTA) StyleTTS baseline on out-of-distribution (OOD) texts.

Paper: [https://arxiv.org/abs/2301.08810](https://arxiv.org/abs/2301.08810)

Audio samples: [https://pl-bert.github.io/](https://pl-bert.github.io/)

## Pre-requisites
1. Python >= 3.7
2. Clone this repository:
```bash
git clone https://github.com/yl4579/PL-BERT.git
cd PL-BERT
```
3. Create a new environment (recommended):
```bash
conda create --name BERT python=3.8
conda activate BERT
python -m ipykernel install --user --name BERT --display-name "BERT"
```
4. Install python requirements: 
```bash
pip install pandas singleton-decorator datasets "transformers<4.33.3" accelerate nltk phonemizer sacremoses pebble
```

## Preprocessing
Please refer to the notebook [preprocess.ipynb](https://github.com/yl4579/PL-BERT/blob/main/preprocess.ipynb) for more details. The preprocessing is for English Wikipedia dataset only. I will make a new branch for Japanese if I have extra time to demostrate training on other languages. You may also refer to [#6](https://github.com/yl4579/PL-BERT/issues/6#issuecomment-1797869275) for preprocessing in other languages like Japanese. 

## Trianing
Please run each cell in the notebook [train.ipynb](https://github.com/yl4579/PL-BERT/blob/main/train.ipynb). You will need to change the line
`config_path = "Configs/config.yml"` in cell 2 if you wish to use a different config file. The training code is in Jupyter notebook primarily because the initial epxeriment was conducted in Jupyter notebook, but you can easily make it a Python script if you want to. 

## Finetuning
Here is an example of how to use it for StyleTTS finetuning. You can use it for other TTS models by replacing the text encoder with the pre-trained PL-BERT.
1. Modify line 683 in [models.py](https://github.com/yl4579/StyleTTS/blob/main/models.py#L683) with the following code to load BERT model in to StyleTTS:
```python
from transformers import AlbertConfig, AlbertModel

log_dir = "YOUR PL-BERT CHECKPOINT PATH"
config_path = os.path.join(log_dir, "config.yml")
plbert_config = yaml.safe_load(open(config_path))

albert_base_configuration = AlbertConfig(**plbert_config['model_params'])
bert = AlbertModel(albert_base_configuration)

files = os.listdir(log_dir)
ckpts = []
for f in os.listdir(log_dir):
    if f.startswith("step_"): ckpts.append(f)

iters = [int(f.split('_')[-1].split('.')[0]) for f in ckpts if os.path.isfile(os.path.join(log_dir, f))]
iters = sorted(iters)[-1]
        
checkpoint = torch.load(log_dir + "/step_" + str(iters) + ".t7", map_location='cpu')
state_dict = checkpoint['net']
from collections import OrderedDict
new_state_dict = OrderedDict()
for k, v in state_dict.items():
    name = k[7:] # remove `module.`
    if name.startswith('encoder.'):
        name = name[8:] # remove `encoder.`
        new_state_dict[name] = v
bert.load_state_dict(new_state_dict)

nets = Munch(bert=bert,
  # linear projection to match the hidden size (BERT 768, StyleTTS 512)
  bert_encoder=nn.Linear(plbert_config['model_params']['hidden_size'], args.hidden_dim),
  predictor=predictor,
    decoder=decoder,
             pitch_extractor=pitch_extractor,
                 text_encoder=text_encoder,
                 style_encoder=style_encoder,
             text_aligner = text_aligner,
            discriminator=discriminator)
```
2. Modify line 126 in [train_second.py](https://github.com/yl4579/StyleTTS/blob/main/train_second.py#L126) with the following code to adjust the learning rate of BERT model:
```python
# for stability
for g in optimizer.optimizers['bert'].param_groups:
    g['betas'] = (0.9, 0.99)
    g['lr'] = 1e-5
    g['initial_lr'] = 1e-5
    g['min_lr'] = 0
    g['weight_decay'] = 0.01
```
3. Modify line 211 in [train_second.py](https://github.com/yl4579/StyleTTS/blob/main/train_second.py#L211) with the following code to replace text encoder with BERT encoder:
```python
            bert_dur = model.bert(texts, attention_mask=(~text_mask).int()).last_hidden_state
            d_en = model.bert_encoder(bert_dur).transpose(-1, -2)
            d, _ = model.predictor(d_en, s, 
                                                    input_lengths, 
                                                    s2s_attn_mono, 
                                                    m)
```
[line 257](https://github.com/yl4579/StyleTTS/blob/main/train_second.py#L257):
```python
            _, p = model.predictor(d_en, s, 
                                                    input_lengths, 
                                                    s2s_attn_mono, 
                                                    m)
```
and [line 415](https://github.com/yl4579/StyleTTS/blob/main/train_second.py#L415):
```python
                bert_dur = model.bert(texts, attention_mask=(~text_mask).int()).last_hidden_state
                d_en = model.bert_encoder(bert_dur).transpose(-1, -2)
                d, p = model.predictor(d_en, s, 
                                                    input_lengths, 
                                                    s2s_attn_mono, 
                                                    m)
```

4. Modify line 347 in [train_second.py](https://github.com/yl4579/StyleTTS/blob/main/train_second.py#L347) with the following code to make sure parameters of BERT model are updated:
```python
            optimizer.step('bert_encoder')
            optimizer.step('bert')
```

The pre-trained PL-BERT on Wikipedia for 1M steps can be downloaded at: [PL-BERT link](https://drive.google.com/file/d/19gzPmWKdmakeVszSNuUtVMMBaFYMQqJ7/view?usp=sharing).

The demo on LJSpeech dataset along with the pre-modified StyleTTS repo and pre-trained models can be downloaded here: [StyleTTS Link](https://drive.google.com/file/d/18DU4JrW1rhySrIk-XSxZkXt2MuznxoM-/view?usp=sharing). This zip file contains the code modification above, the pre-trained PL-BERT model listed above, pre-trained StyleTTS w/ PL-BERT, pre-trained StyleTTS w/o PL-BERT and pre-trained HifiGAN on LJSpeech from the StyleTTS repo.

## References
- [NVIDIA/NeMo-text-processing](https://github.com/NVIDIA/NeMo-text-processing)
- [tomaarsen/TTSTextNormalization](https://github.com/tomaarsen/TTSTextNormalization)
