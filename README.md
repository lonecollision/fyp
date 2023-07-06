# Poetry generator
This repository contains a web app for generating poetry and more!

The model for generating poetry is a pre-trained gpt-2 fine-tuned on approximately 30,000 poems from [Poetry Foundation](https://www.poetryfoundation.org/) and [poets.org](https://poets.org/). 

The corpus and code used to scrape the data are in the ```data``` folder of this repository.

A notebook to fine-tune the model can be found [here](https://colab.research.google.com/drive/1ANdGaYM2e7gHYA3np3dJaO8zMvQMpzoD?usp=sharing).

## Setup
All the files you need to run the web app are in the ```deployment``` folder.

Change into the ```torchserve-mar``` directory and build the image:

```
docker build -t poetica:v1 .
```

Change back to the ```app``` directory and run:

```
docker-compose up
```

This will run both services, you can then access the web app at http://127.0.0.1:5000/.

The handler used to serve the model is available in the ```torchserve``` folder, it was customised from the original [base handler](https://github.com/pytorch/serve/blob/master/ts/torch_handler/base_handler.py) and this [blog post](https://supertype.ai/notes/serving-pytorch-w-torchserve/) helped me create it.


A ```.mar``` file is a packaged version of your model and its artifacts used to register the model into TorchServe.
You can re-create this file with:

```
torch-model-archiver 
--model-name model
--version 1.0 
--model-file my_model/pytorch_model.bin 
--handler handler.py 
--extra-files "./my_model/config.json,./my_model/added_tokens.json,./my_model/merges.txt,./my_model/special_tokens_map.json,./my_model/tokenizer_config.json,./my_model/vocab.json,./my_model/generation_config.json"
--export-path model_store
```

The extra files are model artifacts and are necessary for this to work, they're all available in the ```my_model``` folder (within the ```torchserve``` one).