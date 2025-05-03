import pandas as pd
import time

class EEGStreamer:
    def __init__(self, path="../data/confusion_eeg.csv"):
        self.df = pd.read_csv(path)
        self.features = ['Theta', 'Alpha1', 'Alpha2', 'Beta1', 'Beta2', 'Gamma1', 'Gamma2']
        self.pointer = 0  # Start of stream

    def get_next(self):
        if self.pointer >= len(self.df):
            self.pointer = 0  # loop around

        row = self.df.iloc[self.pointer][self.features].values.reshape(1, -1)
        self.pointer += 1
        return row