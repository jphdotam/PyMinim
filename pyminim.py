import random
import numpy as np
import pandas as pd

from collections import Counter


class Minimiser:
    def __init__(self, minimisation_vars: dict, arms=('A', 'B'), minimisation_weight=0.8,
                 use_first_patient_id_as_seed=True):
        """Creates a minimisation instance which can be fed patients to randomise.

        Arguments:

            minimisation_vars: a dictionary of variable names (keys) and tuples of categories (values)

            arms: A tuple containing the names of the arms

            minimisation_weight: float containing what % of the time the randomisation is governed by the minimisation
            algorithm rather than by random allocation.

            use_first_patient_id_as_seed: when True, ensures results are reproducible, without making the first
            randomisation result being practically predictable. This is preferable to using a seed such as 42, where
            every trial would allocate the first patient to the same arm, predictably.

        """
        assert 'arm' not in minimisation_vars
        self.minimisation_vars = minimisation_vars
        self.arms = arms
        self.minimisation_weight = minimisation_weight
        self.use_first_patient_id_as_seed = use_first_patient_id_as_seed
        self.df_patients = self.create_patient_dataframe()

    def __repr__(self):
        return f"Minimiser of {len(self.minimisation_vars.keys())} variables " \
               f"({', '.join(self.minimisation_vars.keys())}) - " \
               f"{self.df_patients.shape[0]} patients"

    def characteristics_by_arm(self) -> pd.DataFrame:
        return minimiser.df_patients.groupby(['arm']).aggregate(Counter)

    def create_patient_dataframe(self) -> pd.DataFrame:
        """Returns a dataframe of string types with a column for each minimisation variable, and the arm"""
        columns = list(self.minimisation_vars.keys())
        columns.append('arm')
        dtypes = np.dtype([(k, str) for k in columns])
        data = np.empty(0, dtype=dtypes)
        return pd.DataFrame(data)

    def get_n_patients(self) -> int:
        return self.df_patients.shape[0]

    def check_valid_characteristics(self, characteristics: dict) -> bool:
        pt_chars = sorted(characteristics.keys())
        needed_chars = sorted(self.minimisation_vars.keys())

        if pt_chars != needed_chars:
            raise ValueError(f"Characteristics of patient do not match those needed: {pt_chars} vs {needed_chars}")

        for pt_char in pt_chars:
            if characteristics[pt_char] not in self.minimisation_vars[pt_char]:
                raise ValueError(f"Invalid value {characteristics[pt_char]} for characteristic {pt_char} - "
                                 f"Should one of {self.minimisation_vars[pt_char]}")

        return True

    def randomise_patient(self, id, characteristics: dict):
        """Supply with a dictionary with a key/value for every minimisation var, and also an 'id' key"""
        self.check_valid_characteristics(characteristics)

        # See if first patient in trial
        if self.get_n_patients() == 0:
            if self.use_first_patient_id_as_seed:
                random.seed(id)
            arm = self.get_random_arm()

        # If not first patient
        else:
            if random.random() <= self.minimisation_weight:
                arm = self.get_minimised_arm(characteristics)
            else:
                arm = self.get_random_arm()

        self._add_patient_to_arm(id, characteristics, arm)
        print(f"Randomised patient {id} to {arm}")

    def get_random_arm(self) -> str:
        return random.choice(self.arms)

    def get_minimised_arm(self, characteristics: dict) -> str:
        cols = characteristics.keys()
        values = characteristics.values()
        conditions = list(zip(cols, values))
        rows_boolean = self.apply_conditions(self.df_patients, conditions)
        rows = self.df_patients[rows_boolean]
        if rows.shape[0] == 0:
            arm = self.get_random_arm()
        else:
            counts = rows['arm'].value_counts()

            if len(counts) == 1:  # Only 1 arm has patients; randomise to other
                only_arm = counts.idxmax()
                other_arm = [a for a in self.arms if a != only_arm]
                assert len(other_arm) == 1
                arm = other_arm[0]

            else:  # Both arms have at least 1 patient
                if counts.max() == counts.min():  # Arms have equal numbers
                    arm = self.get_random_arm()
                else:  # Arms has differing numbers, assign to arm with fewest patients
                    arm = counts.idxmin()

        return arm

    def _add_patient_to_arm(self, id: str, characteristics: dict, arm: str):
        assert id not in self.df_patients, f"Patient {id} already in patient list!"
        characteristics['arm'] = arm
        df_patient = pd.DataFrame(patient, index=[id])
        self.df_patients = self.df_patients.append(df_patient)

    @staticmethod
    def apply_conditions(df, conditions) -> pd.DataFrame:
        """Thanks to https://stackoverflow.com/a/43370439"""
        assert len(conditions) > 0
        comps = [df[c] == v for c, v in conditions]
        result = comps[0]
        for comp in comps[1:]:
            result &= comp
        return result


if __name__ == "__main__":
    # Example taken from https://www.bmj.com/content/330/7495/843

    minimisation_vars = {
        'sex': ('male', 'female'),
        'age': ('<=50', '>50'),
        'ethnicity': ('white', 'black', 'asian'),
        'smoker': ('no', 'yes')
    }

    # Generate some patients
    random.seed(42)
    patients = []
    for i in range(160):
        pt = {}
        pt['id'] = i
        pt['sex'] = random.choice(('male', 'male', 'male', 'female', 'female'))  # 60% male
        pt['age'] = random.choice(('>50', '<=50'))  # Equal proportions
        pt['ethnicity'] = random.choice(  # 70% white, 20% asian, 10% black
            ('white', 'white', 'white', 'white', 'white', 'white', 'white', 'asian', 'asian', 'black'))
        pt['smoker'] = random.choice(('no', 'no', 'no', 'yes'))  # 75% non-smokers
        patients.append(pt)

    # Create the minimiser
    minimiser = Minimiser(minimisation_vars)

    # Add patients
    for patient in patients:
        id = patient.pop('id')
        minimiser.randomise_patient(id, patient)

    # Print basic outputs
    print(minimiser)

    pd.set_option('display.max_columns', None)

    # Show the randomisation balance by arm for each var
    print(minimiser.characteristics_by_arm())