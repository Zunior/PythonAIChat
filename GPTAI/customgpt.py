from transformers import GPT2LMHeadModel, GPT2Tokenizer, TFGPT2LMHeadModel, AutoTokenizer, GenerationConfig
import tensorflow as tf
from transformers import GPT2Tokenizer, TFGPT2LMHeadModel

import Constants
import settings
from Util import Util

class CustomGPT:
    def __init__(self):
        print(f"Loading tokenizer from: {Constants.GPT_TOKENIZER_DIR}")
        self.tokenizer = GPT2Tokenizer.from_pretrained(Constants.GPT_TOKENIZER_DIR)

        if self.tokenizer.pad_token is None:
            if self.tokenizer.eos_token is not None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            else:
                self.tokenizer.add_special_tokens({'pad_token': '[PAD]'})
                self.tokenizer.pad_token_id = self.tokenizer.convert_tokens_to_ids('[PAD]')

        print(f"Loading model from: {Constants.GPT_MODEL_DIR}")
        self.model = TFGPT2LMHeadModel.from_pretrained(
            Constants.GPT_MODEL_DIR,
            pad_token_id=self.tokenizer.eos_token_id,
            local_files_only=True # Good practice to ensure no accidental downloads
        )

        print("Initialization complete. Model and tokenizer are ready.")

    def return_answer(self, query_type, question_value):
        inputs = self.tokenizer(
            question_value,
            return_tensors='tf',
            padding='longest',  # Ensures padding is applied (if needed)
            truncation=True     # Prevents errors if questionValue is too long
        )
        input_ids = inputs['input_ids']
        attention_mask = inputs['attention_mask']

        custom_gen_config = GenerationConfig(
            attention_mask=attention_mask,
            max_length=100,             # Adjust as needed
            num_beams=5,                # Recommended for less creative, more coherent answers
            no_repeat_ngram_size=2,     # To avoid repetition
            early_stopping=True,
            pad_token_id=self.tokenizer.pad_token_id # Explicitly pass
        )

        outputs = self.model.generate(
            input_ids,
            generation_config=custom_gen_config
        )

        output_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        if output_text.startswith(question_value):
            answer_only = output_text[len(question_value):].strip()
        else:
            # Fallback or log a warning if the generated text doesn't start with the prompt
            answer_only = output_text

        return answer_only, "Warning: Generated text did not start with the prompt. Showing full output."

    def train_model(self, input_data):
        max_length = self.tokenizer.model_max_length
        # Split the input text into smaller chunks
        chunks = Util.split_text_no_sentence_break(input_data, max_length)

        tokenized_chunks = [self.tokenizer.encode(chunk) for chunk in chunks]
        # Flatten the list of lists into a single list of token IDs
        all_tokens = [token for chunk in tokenized_chunks for token in chunk]

        examples = []
        # Create overlapping sequences
        for i in range(0, len(all_tokens) - max_length, max_length):
            examples.append(all_tokens[i : i + max_length])

        # Let the model handle labels internally
        dataset = tf.data.Dataset.from_tensor_slices(examples)

        def map_fn(inputs):
            return (inputs, inputs) # Input and labels are the same

        dataset = dataset.map(map_fn)
        dataset = dataset.shuffle(settings.BUFFER_SIZE).batch(settings.BATCH_SIZE, drop_remainder=False)

        optimizer = tf.keras.optimizers.Adam(learning_rate=1e-5, epsilon=1e-08, clipnorm=1.0)
        loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
        metric = tf.keras.metrics.SparseCategoricalAccuracy('accuracy')
        self.model.compile(optimizer=optimizer, loss=loss, metrics=[metric])
        self.model.fit(dataset, epochs=3)

        self.tokenizer.save_pretrained(Constants.GPT_TOKENIZER_DIR)
        self.model.save_pretrained(Constants.GPT_MODEL_DIR)
