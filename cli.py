import argparse


class Cli():
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser()

        self.parser.add_argument('--verbose', '-v', action='count', default=0, help='Set level logging')
        self.parser.add_argument('--delay', type=int, help='enable response delay')
        self.parser.add_argument('--path',required=True, help='path to photo directory')