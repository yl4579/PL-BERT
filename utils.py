import glob
import torch

def scan_checkpoint(cp_dir):
    pattern = os.path.join(cp_dir)
    cp_list = glob.glob(pattern)
    print(cp_list)
    if len(cp_list) == 0:
        return None
    return sorted(cp_list)[-1]

def length_to_mask(lengths):
    mask = torch.arange(lengths.max()).unsqueeze(0).expand(lengths.shape[0], -1).type_as(lengths)
    mask = torch.gt(mask+1, lengths.unsqueeze(1))
    return mask