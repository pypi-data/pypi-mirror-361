import copy
from .pnet import PNet
import polars as pl
import os

class SimulationHistoryHandler:
    def __init__(self, places, parquet_file, flush_every=10000):
        self.places = places
        self.parquet_file = parquet_file
        self.flush_every = flush_every
        self.rows = []
        self.last_firing = None
        self._parquet_initialized = False

    def __call__(self, dict_places, firing_sequence, step):
        # Determine the last transition fired (None for step 0)
        if step == 0 or not firing_sequence:
            transition = None
        else:
            transition = firing_sequence[-1]
        row = {'transition': transition, 'step': step}
        for place in self.places:
            row[place] = dict_places.get(place, 0)
        self.rows.append(row)
        if len(self.rows) >= self.flush_every:
            self.flush()

    def flush(self):
        if not self.rows:
            return
        df = pl.DataFrame(self.rows)
        if not self._parquet_initialized or not os.path.exists(self.parquet_file):
            df.write_parquet(self.parquet_file)
            self._parquet_initialized = True
        else:
            # Append to existing parquet file
            old_df = pl.read_parquet(self.parquet_file)
            new_df = pl.concat([old_df, df])
            new_df.write_parquet(self.parquet_file)
        self.rows = []

    def finalize(self):
        self.flush()


def simulate_with_history_to_parquet(pnet: PNet, num_steps: int, parquet_file: str, flush_every: int = 10000, law: str = 'random'):
    """
    Runs a simulation and stores the full history to a Parquet file using polars.
    """
    places = list(pnet.dict_places.keys())
    handler = SimulationHistoryHandler(places, parquet_file, flush_every)
    pnet.simulate_petrinet(num_steps, law, handler)
    handler.finalize()
    return parquet_file 