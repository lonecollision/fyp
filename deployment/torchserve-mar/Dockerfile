FROM pytorch/torchserve:0.7.1-gpu

# copy model_store to new model_store directory
COPY ["./model_store", "./model_store"]

CMD ["torchserve", "--start", "--model-store", "model_store", "--models", "my_model=poetica.mar", "--ncs"]