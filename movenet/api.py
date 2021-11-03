import cv2
import time
import argparse
import os
import torch

from movenet.models.model_factory import load_model
from movenet.utils import read_imgfile, draw_skel_and_kp, process_input


class Infer(object):
    def __init__(self):
        self.model = None

    def init(self, model_name = "movenet"):
        self.model = load_model(model_name)

    def infer(self, image, input_size=192):
        time1 = time.time()
        infer_img, src_img = process_input(image, size=192)
        input_image = torch.Tensor(infer_img) # .cuda()
        with torch.no_grad():
            kpt_with_conf = self.model(input_image)[0, 0, :, :]
            kpt_with_conf = kpt_with_conf.detach().cpu().numpy()
            #print('infer spend: %.4f'%(time.time()-time1))
            #return kpt_with_conf
            #draw_image = draw_skel_and_kp(src_img, kpt_with_conf, conf_thres=0.3)
            #cv2.imwrite(os.path.join(args.output_dir, os.path.relpath(f, args.image_dir)), draw_image)
            
            #print(kpt_with_conf)
            
            return kpt_with_conf

if __name__ == "__main__":
    infer = Infer()
    infer.init()
    image = cv2.imread('./movenet/images/2021-10-27_183637.png')
    rets = infer.infer(image)
    print(rets)
    '''
    [[0.11672449 0.4983359  0.53861076]
     [0.09518386 0.52236164 0.8093194 ]
     [0.09564885 0.47497743 0.8435249 ]
     [0.11097466 0.5598389  0.6196337 ]
     [0.11173555 0.44507813 0.83289146]
     [0.21309422 0.63052    0.89540803]
     [0.21495724 0.37769043 0.85074025]
     [0.36568946 0.6455332  0.8179583 ]
     [0.3696283  0.35331106 0.7355779 ]
     [0.4838968  0.6602464  0.8562068 ]
     [0.48243308 0.34036517 0.83464324]
     [0.48272216 0.5703915  0.83931935]
     [0.48364693 0.4317438  0.77935195]
     [0.69909835 0.5575497  0.747689  ]
     [0.691924   0.4332485  0.6461556 ]
     [0.88191533 0.5286259  0.8637549 ]
     [0.88114727 0.44617733 0.82852405]] 
    '''
