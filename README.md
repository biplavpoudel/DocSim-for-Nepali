# DocSim -- Documents Simulator

Synthetically generate random text documents with ground truth!


[//]: # (## Demo)

[//]: # ()
[//]: # (|                   Template                   |                   Generated                   |                   Augmented                   |)

[//]: # (|:--------------------------------------------:|:---------------------------------------------:|:---------------------------------------------:|)

[//]: # (| <img src="documentation/misc/template.jpg"/> | <img src="documentation/misc/generated.jpg"/> | <img src="documentation/misc/augmented.jpg"/> |)

## Requirements

- Atleast Python 3.7
- `pip install -r dependencies.txt`
- Check [`documentation/Installation`](/documentation/Installation.md) for further instructions

## Example Usage

### Generate synthetic images

```
python generate.py <template.json> <num_samples> <output_folder>
```

Check the [`templates/`](templates/) folder for sample document templates.

### Augment generated images

```
python augment.py <config.json> <input_folder> <num_epochs> <output_folder> <num_workers>
```

Check [`documentation/Augmentation`](documentation/Augmentation.md) for more details.

<hr/>
