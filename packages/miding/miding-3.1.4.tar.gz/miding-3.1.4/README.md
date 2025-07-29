# Miding

This program names '**miding**', an abbreviation of '**Midi Neuronal Generator**', 
which aims to generate listenable midi sequences, attempting to create fair scores.

Sincerely thanks for _**keras**_, the neuronal network model we have applied.
In this program, the model construction is two GRU layer and a Dense layer with the activation Softmax.
### Download

Here is our website:
* https://github.com/JerrySkywolf/miding

This package could also be downloaded through PyPi by:

`pip install miding`

View at the webpage
* https://pypi.org/project/miding

### How to use the model?

For example, you could use a random seed:

``from miding import Predict, Seed, get_seed``

``Predict(seed=get_seed(), epoch=256, model_version=1751770203)``

or a defined seed:

``s = Seed(midi_file='example_seed.mid')``

``Predict(seed=s.get_seed(),epoch=128, model_version=1751770203)``



 