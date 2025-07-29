from loguru import logger
import os
import safetensors
from safetensors.torch import load_file, save_file


# model_file = 'checkpoints/pi0/model.safetensors'
# model_file = 'checkpoints/pi0/model-00001-of-00003.safetensors'
# model_file = 'outputs/pi0/mgpus-aloha-model-data-0708_1255/checkpoints/002500/pretrained_model/model.safetensors'
model_file = 'outputs/pi0/mgpus-aloha-model-data-0708/checkpoints/003700/pretrained_model/model.safetensors'
# model_file = '/pfs/data/fgang/vla_holo/checkpoints/pi0/'
model_file_1 = 'checkpoints/pi0/model.safetensors'


# state_dict = load_file(model_file, device="cpu")

def load_a(model_file):
    state_dict = load_file(model_file)

    from transformers import __version__ as transformers_version
    from packaging import version

    TRANSFORMERS_MIN_VERSION = "4.52.0"

    # if version.parse(transformers_version) >= version.parse(TRANSFORMERS_MIN_VERSION):
    #     print("Warning: Transformers version >= 4.52.0 detected - applying state dict key transformation")
    #     transformed_state_dict = model._transform_state_dict_keys(state_dict)
    # else:
    transformed_state_dict = state_dict
    from pprint import pprint
    # pprint([k for k in state_dict.keys() if 'language_model' in k])

    # ka = [k for k in state_dict.keys() if '.0.mlp.down_proj.weight' in k and 'language_model' in k]
    ka = [k for k in state_dict.keys() if 'embed_token' in k and 'language_model' in k]
    print(ka)
    a = state_dict[ka[0]]
    print(a)
    return a
        
# load_a(model_file_1)
a = load_a(model_file)


# model_file_1 = '/pfs/data/fgang/vla_holo/outputs/pi0/mgpus-aloha-model-data-0707_1919/checkpoints/last/pretrained_model/model.safetensors'
# sd = load_file(model_file_1)
# sd['model.paligemma_with_expert.paligemma.model.language_model.embed_tokens.weight'] = a
# save_file(sd, os.path.join(os.path.dirname(model_file_1), 'model_1.safetensors'))
# print('done')