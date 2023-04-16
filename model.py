import torch
from torch import nn
import torch.nn.functional as F

class MultiTaskModel(nn.Module):
    def __init__(self, model, num_tokens=178, num_vocab=84827, hidden_size=768):
        super().__init__()

        self.encoder = model
        self.mask_predictor = nn.Linear(hidden_size, num_tokens)
        self.word_predictor = nn.Linear(hidden_size, num_vocab)
    
    def forward(self, phonemes, attention_mask=None):
        output = self.encoder(phonemes, attention_mask=attention_mask)
        tokens_pred = self.mask_predictor(output.last_hidden_state)
        words_pred = self.word_predictor(output.last_hidden_state)
        
        return tokens_pred, words_pred