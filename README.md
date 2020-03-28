# PyMinim
A simple minimisation algorithm for 1:1 randomisation in trials


# Usage
It uses a single class and the only dependency outside of the standard library is Pandas.

First, decide what variables you want to minimise by by creating a dictionary, where the keys are the variable names, and the values are tuples of the categories.
For example:
```python
minimisation_vars = {
    'sex': ('male', 'female'),
    'age': ('<=50', '>50'),
    'ethnicity': ('white', 'black', 'asian'),
    'smoker': ('no', 'yes')
}
```

Then you can instantiate the minimiser:

```python
minimiser = Minimiser(minimisation_vars)
```

From here on, it's easy to randomise patients with:

```python
minimiser.randomise_patient(id, characteristics)
```   

Where id is a unique ID for the patient and characteristics is a dict of key:value pairs for the minimisation variables.

For example, if we wanted to simulate randomising 160 patients using the above values, we could do something like this:

```python
for i in range(160):
    pt = {}
    pt['id'] = i
    pt['sex'] = random.choice(('male', 'male', 'male', 'female', 'female'))  # 60% male
    pt['age'] = random.choice(('>50', '<=50'))  # Equal proportions
    pt['ethnicity'] = random.choice(  # 70% white, 20% asian, 10% black
        ('white', 'white', 'white', 'white', 'white', 'white', 'white', 'asian', 'asian', 'black'))
    pt['smoker'] = random.choice(('no', 'no', 'no', 'yes'))  # 75% non-smokers
    patients.append(pt)

for patient in patients:
    id = patient.pop('id')
    minimiser.randomise_patient(id, patient)
```
        
We can see how well the system balanced the 2 arms:

```python
print(minimiser.characteristics_by_arm())
```
```
>                               sex                      age                               ethnicity                  smoker
>   arm                                                        
>   A    {'male': 46, 'female': 34}  {'>50': 40, '<=50': 40}   {'white': 56, 'asian': 17, 'black': 7}  {'no': 59, 'yes': 21}
>   B    {'male': 45, 'female': 35}  {'>50': 40, '<=50': 40}   {'white': 57, 'asian': 14, 'black': 9}  {'no': 62, 'yes': 18}
```

# Details

* THIS SYSTEM IS NOT YET FULLY TESTED
* Currently only works for 1:1 randomisation.
* First patient will be truly randomised, by default using their ID as a seed to make reproducibility easier (can be disabled)
* When arms are equally balanaced, allocation is random
