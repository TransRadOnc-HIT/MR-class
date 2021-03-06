
#import sys
#import os
#sys.path.append(os.getcwd())

from mrclass_resnet.utils import load_config
from mrclass_resnet.infer import infer
import argparse

if __name__ == "__main__":
   
    print("\n########################")
    print("Mrclass")
    print("########################\n")
    parser = argparse.ArgumentParser(description='MRclass')
    parser.add_argument('--config', type = str, help = 'Path to the configuration file', required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    infer(config)

    
    print('Done')

# -*- coding: utf-8 -*-

