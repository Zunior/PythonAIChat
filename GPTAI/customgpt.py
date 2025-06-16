from transformers import GPT2LMHeadModel, GPT2Tokenizer, TFGPT2LMHeadModel, AutoTokenizer
import tensorflow as tf
import Util
import torch
import random
import numpy as np
import UtilText

class CustomGPT:
    _GPT_MODEL_DIR = "./gptModel/model"
    _GPT_TOKENIZER_DIR = "./gptModel/tokenizer"
    _GPT2_MODEL_NAME = "gpt2"

    def return_answer(self, queryType, questionValue):
        tokenizer = GPT2Tokenizer.from_pretrained(CustomGPT._GPT_TOKENIZER_DIR)
        model = GPT2LMHeadModel.from_pretrained(
            CustomGPT._GPT_MODEL_DIR, from_tf=True,
            pad_token_id=tokenizer.eos_token_id,
            local_files_only=True
        )

        seed = random.randint(0, 13)
        np.random.seed(seed)
        torch.random.manual_seed(seed)
        torch.cuda.manual_seed(seed)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        input_ids = torch.tensor(tokenizer.encode(questionValue, add_special_tokens=True)).unsqueeze(0) # bs=1

        model.to(device)
        model.eval()

        outputs = model.generate(
            input_ids.to(device),
            max_length=500,
            do_sample=True,
            top_k=20,
            temperature=0.1
        )

        output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return output_text, ""


        # tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        # # tokenizer = GPT2Tokenizer.from_pretrained(CustomGPT._GPT_TOKENIZER_DIR)
        # inputs = tokenizer(questionValue, return_tensors='pt')
        # # input_ids = tokenizer.encode(questionValue, return_tensors='tf')
        # # model = TFGPT2LMHeadModel.from_pretrained(
        # #     "gpt2", from_pt=True, pad_token_id=tokenizer.eos_token_id
        # # )
        # model = TFGPT2LMHeadModel.from_pretrained("gpt2")
        # # outputs = model.generate(input_ids, max_length=1024)
        # outputs = model.generate(**inputs, num_beams=5,
        #                          max_new_tokens=50, early_stopping=True,
        #                          no_repeat_ngram_size=2)
        #
        # # input_ids = tokenizer.encode(questionValue, return_tensors='pt')
        # # output = model.generate(input_ids, max_length=1024, do_sample=True)
        # text_output = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        # # output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        #
        # return text_output[0], ""
        # # model = TFGPT2LMHeadModel.from_pretrained(CustomGPT._GPT_MODEL_DIR, pad_token_id=tokenizer.eos_token_id)
        # # outputs = model.generate(inputs['input_ids'], max_length=100)

    def train_model(self, input_data):
        tokenizer = GPT2Tokenizer.from_pretrained(CustomGPT._GPT2_MODEL_NAME) # distilgpt2
        # model = TFGPT2LMHeadModel.from_pretrained(CustomGPT._GPT2_MODEL_NAME, from_pt=True, pad_token_id=tokenizer.eos_token_id)
        model = TFGPT2LMHeadModel.from_pretrained(CustomGPT._GPT2_MODEL_NAME)
        max_length = tokenizer.model_max_length
        # Split the input text into smaller chunks
        chunks = UtilText.split_text_no_sentence_break(input_data, max_length)

        # tokenizer.pad_token = tokenizer.eos_token
        # # Tokenize each chunk
        # tokens_list = [tokenizer(chunk, truncation=True,
        #                  max_length=max_length, padding='max_length',
        #                  return_tensors='pt') for chunk in chunks]

        tokenized_all = []
        for chunk in chunks:
            tokenized_all.append(tokenizer.encode(chunk))

        examples = []
        block_size = 100
        for tokenized_one in tokenized_all:
            for i in range(0, len(tokenized_one) - block_size + 1, block_size):  # Truncate in block of block_size
                examples.append(tokenized_one[i:i + block_size])

        inputs, labels = [], []
        for ex in examples:
            inputs.append(ex[:-1])
            labels.append(ex[1:])

        dataset = tf.data.Dataset.from_tensor_slices((inputs, labels))

        BATCH_SIZE = 16
        BUFFER_SIZE = 10000

        dataset = dataset.shuffle(BUFFER_SIZE).batch(BATCH_SIZE, drop_remainder=True)

        optimizer = tf.keras.optimizers.Adam(learning_rate=3e-5, epsilon=1e-08, clipnorm=1.0)
        loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
        metric = tf.keras.metrics.SparseCategoricalAccuracy('accuracy')
        model.compile(optimizer=optimizer, loss=[loss, *[None] * model.config.n_layer], metrics=[metric])
        model.fit(dataset, epochs=3)

        tokenizer.save_pretrained(CustomGPT._GPT_TOKENIZER_DIR)
        model.save_pretrained(CustomGPT._GPT_MODEL_DIR)
