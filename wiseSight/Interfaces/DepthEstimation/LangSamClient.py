# sys.path.append('/home/cike/hds/langsam/example_notebook')
from Interfaces.LangSAMInterface import LangSAM_Interface


def build_langsam(device):
    langsam_model = LangSAM_Interface(device)
    return langsam_model


def call_langsam(langsam_model, img, prompt):
    return langsam_model.predict(img, prompt, return_mask=True, return_box=True, return_phrase=True, return_logits=True)


# LangSAM utils functions
def get_idx_using_phrases(phrases, phrase):
    for i in range(len(phrases)):
        if phrases[i] == phrase:
            return i
    return -1


def get_ground_idx(phrases):
    idx = get_idx_using_phrases(phrases, 'ground')
    if idx == -1:
        raise Exception('Expected ground in phrases')
    # assert idx != -1, 'Expected ground in phrases'
    return idx
