# os.environ['CUDA_VISIBLE_DEVICES'] = '2'
import logging
import threading

from PIL import Image

# sys.path.append("/home/cike/hds/langsam/")
from Interfaces.LangSAM import LangSAM

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')


class LangSAM_Interface(object):
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(LangSAM_Interface, "_instance"):
            with LangSAM_Interface._instance_lock:
                if not hasattr(LangSAM_Interface, "_instance"):
                    # 类加括号就回去执行__new__方法，__new__方法会创建一个类实例
                    LangSAM_Interface._instance = object.__new__(cls)  # 继承object类的__new__方法，类去调用方法，说明是函数，要手动传cls
        return LangSAM_Interface._instance  # obj1
        # 类加括号就会先去执行__new__方法，再执行__init__方法

    def __init__(self, device="cuda:0"):
        logging.info("Loading the LangSAM model...")
        self.model = LangSAM(device)
        logging.info("Model loaded successfully.")

    def predict(self, image, text_prompt, return_mask=False, return_box=True, return_phrase=True, return_logits=True):
        masks, boxes, phrases, logits = self.model.predict(image, text_prompt)
        masks = masks if return_mask is True else []
        boxes = boxes if return_box is True else []
        phrases = phrases if return_phrase is True else []
        logits = logits if return_logits is True else []
        # boxes, logits, masks, phrases
        return boxes, logits, masks, phrases


if __name__ == "__main__":
    import io

    langsam_model = LangSAM_Interface("cuda:0")
    image_path = "/home/cike/hds/langsam/assets/Bollard.jpg"
    with open('/home/cike/hds/langsam/assets/Bollard.jpg', 'rb') as file:
        image = file.read()
    # convert bytes to Image
    image = Image.open(io.BytesIO(image)).convert('RGB')
    # H, W, C

    text_prompt = "bollard.ground.people"
    masks, boxes, phrases, logits = langsam_model.predict(image, text_prompt)

    print(masks)
