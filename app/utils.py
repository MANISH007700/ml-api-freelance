from functools import wraps
from flask import request, jsonify
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
from loguru import logger

# Custom decorator for logging and checking the "text" field in the request form
def check_text_field(current_app):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            logger.info(f"Input Form --> {request.form}")

            if 'text' in request.form:
                return f(*args, **kwargs)  # Call the original function
            else:
                response_data = {
                    'error_message': 'No text in form_data. Please provide input text.',
                    'status': 400
                }
                return jsonify(response_data), 400

        return decorated_function

    return decorator


def paraphrase_text(model, tokenizer, device, input_text, num_return_sequences=1):
    text =  "paraphrase: " + input_text + " </s>"

    encoding = tokenizer.encode_plus(text, padding="max_length", max_length=256, return_tensors="pt")
    input_ids, attention_masks = encoding["input_ids"].to(device), encoding["attention_mask"].to(device)

    outputs = model.generate(
        input_ids=input_ids, attention_mask=attention_masks,
        max_length=256,
        do_sample=True,
        num_beams=5,
        # top_k=120,
        temperature=1.5,
        top_p=1,
        num_return_sequences=num_return_sequences
    )
    paraphrashed_text = tokenizer.decode(outputs[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
    return paraphrashed_text

def correct_grammar(model, tokenizer, device, input_text, num_return_sequences=1):
    text =  input_text

    encoding = tokenizer.encode_plus(text, padding="max_length", max_length=256, return_tensors="pt")
    input_ids, attention_masks = encoding["input_ids"].to(device), encoding["attention_mask"].to(device)

    outputs = model.generate(
        input_ids=input_ids, 
        attention_mask=attention_masks,
        max_new_tokens=256,
        num_return_sequences=num_return_sequences
    )

    corrected_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return corrected_text

def load_model(model_name):
    torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'
    logger.info(f"Loading model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(torch_device)
    return model, tokenizer, torch_device