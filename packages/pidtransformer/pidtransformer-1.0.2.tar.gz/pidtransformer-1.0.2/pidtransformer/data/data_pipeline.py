# FILE: src/pid_transformer/data_pipeline.py
from datasets import load_dataset
from transformers import T5Tokenizer

def get_data(config):
    """
    Loads the dataset, initializes the tokenizer, and returns them.
    """
    # 1. Load Tokenizer
    # We use T5 tokenizer as a robust, general-purpose tokenizer.
    # It's important that the vocab_size in config matches the tokenizer's.
    tokenizer = T5Tokenizer.from_pretrained("t5-small")

    # Update config with the actual vocab size from the tokenizer
    config["vocab_size"] = tokenizer.vocab_size

    # 2. Load Dataset from Hugging Face
    dataset = load_dataset(config["dataset_name"], config["subset"], split='train[:1%]') # Use only 1% for quick testing

    # 3. Tokenize the dataset
    def tokenize_function(examples):
        # For this example, we'll just use the document part as both input and target
        # A real summarization task would be more complex.
        text = examples[config["text_column"]]
        tokenized = tokenizer(
            text, 
            max_length=config["max_seq_len"], 
            padding="max_length", 
            truncation=True,
            return_tensors="pt"
        )
        # For a language model, the labels are the same as the input_ids
        tokenized["labels"] = tokenized["input_ids"].clone()
        return tokenized

    processed_dataset = dataset.map(tokenize_function, batched=True, remove_columns=dataset.column_names)
    processed_dataset.set_format(type='torch')

    return processed_dataset, tokenizer