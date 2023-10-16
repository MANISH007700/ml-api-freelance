from flask import Flask, request, jsonify
from loguru import logger

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch


logger.info("Initializing flask app...")
app = Flask(__name__)


def load_model():
    model_name = 'Vamsi/T5_Paraphrase_Paws'
    torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(torch_device)
    return model, tokenizer, torch_device

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

model, tokenizer, device_hardware = load_model()
logger.info("Flask app initialized!")

@app.route("/paraphrase/", methods=["POST"])
def paraphrase_api():
    logger.info(f"Input Form --> {request.form}")
    if 'text' in request.form:
        text = request.form["text"]
    else:
        response_data = {
            'error_message': 'No text in form_data. Please provide input text.',
            'status': 400
            }
        return jsonify(response_data), 400
    
    if text:
        paraphrashed_text = paraphrase_text(model, tokenizer, device_hardware, text)
    else:
        logger.info("Empty text provided.")
        paraphrashed_text = text

    response_data = {
        "paraphrased_text": paraphrashed_text,
        'status': 200
    }

    return jsonify(response_data)


@app.route("/healthz/", methods=["GET"])
def health_check():
    return "Welcome to the paraphrase api."