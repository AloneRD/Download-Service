import argparse


class Cli():
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser()

        self.parser.add_argument('--log', choices=['enable', 'disable'], help='enable or disable logging')
        self.parser.add_argument('--delay', type=int, help='enable response delay')
        self.parser.add_argument('--path',required=True, help='path to photo directory')