import torch
import logging
import transformers
import os

from ts.torch_handler.base_handler import BaseHandler
from transformers import GPT2LMHeadModel, GPT2Tokenizer

logger = logging.getLogger(__name__)
logger.info("Transformers version %s", transformers.__version__)

class ModelHandler(BaseHandler):
    def initialize(self, context):
        # context (JSON object) contains information pertaining to the model artifacts parameters
        # context has 2 attributes: system_properties, manifest
        properties       = context.system_properties
        self.manifest    = context.manifest
        # Logging these two properties we're able to know exactly what they contain
        logger.info(f'Properties: {properties}')
        logger.info(f'Manifest: {self.manifest}')

        # Model directory (actual model not included)
        model_dir        = properties.get('model_dir')

        # Use GPU if available
        self.device      = torch.device(
            "cuda:" + str(properties.get('gpu_id'))
            if torch.cuda.is_available() and properties.get('gpu_id') is not None
            else "cpu"
        )
        logger.info(f'Using device {self.device}')

        # Load model
        # Retrieve file name from manifest property
        model_file       = self.manifest['model']['modelFile']
        # Compose model path
        model_path       = os.path.join(model_dir, model_file)

        if os.path.isfile(model_path):
            self.model   = GPT2LMHeadModel.from_pretrained(model_dir)
            self.model.to(self.device)
            self.model.eval()
            logger.info(f'Successfully loaded model from {model_file}')
        else:
            raise RuntimeError('Missing the model file')

        # Load tokenizer
        self.tokenizer   = GPT2Tokenizer.from_pretrained(model_dir)
        if self.tokenizer is not None:
            logger.info('Successfully loaded tokenizer')
        else:
            raise RuntimeError('Missing tokenizer')

        self.initialized = True
    def preprocess(self, requests):
        input_batch = None
        for idx, data in enumerate(requests):
            data             = requests[0].get('body')
            if data is None:
                data         = requests[0].get('data')
            if isinstance(data, (bytes, bytearray)):
                data = data.decode("utf-8")
            logger.info("Received text: '%s'", data)
            inputs           = self.tokenizer.encode(data, return_tensors = "pt")
            inputs           = inputs.to(self.device)
            if inputs.shape is not None:
                if input_batch is None:
                    input_batch = inputs
                    input_batch = input_batch.to(self.device)
                else:
                    input_batch = torch.cat((input_batch, inputs), 0).to(self.device)

        return input_batch

    def inference(self, inputs):
        inferences = []
        outputs    = self.model.generate(inputs,
                                         do_sample            = True,
                                         max_length           = 200,
                                         num_return_sequences = 1,
                                         no_repeat_ngram_size = 2,
                                         num_beams            = 5,
                                         early_stopping       = True)
        for i, x in enumerate(outputs):
            inferences.append(
                self.tokenizer.decode(outputs[i], skip_special_tokens = False)
            )
        logger.info("Generated text: '%s'", inferences)
        print("Generated text: '%s'", inferences)
        return inferences

    def postprocess(self, outputs):
        return outputs


