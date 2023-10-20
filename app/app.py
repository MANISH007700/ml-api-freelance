from flask import Flask, request, jsonify
from loguru import logger


from app.utils import load_model, check_text_field, paraphrase_text, correct_grammar


logger.info("Initializing flask app...")
app = Flask(__name__)


app.config["paraphrase_model"], app.config["paraphrase_tokenizer"], device_hardware = load_model(model_name="Vamsi/T5_Paraphrase_Paws")
app.config["grammar_model"], app.config["grammar_tokenizer"], _ = load_model(model_name="vennify/t5-base-grammar-correction")

logger.info("Flask app initialized!")

@app.route("/paraphrase", methods=["POST"])
@check_text_field(app)
def paraphrase_api():
    text = request.form["text"]
    
    if text:
        paraphrashed_text = paraphrase_text(app.config["paraphrase_model"], app.config["paraphrase_tokenizer"], device_hardware, text)
    else:
        logger.info("Empty text provided.")
        paraphrashed_text = text

    response_data = {
        "paraphrased_text": paraphrashed_text,
        'status': 200
    }

    return jsonify(response_data)


@app.route("/correct-grammar", methods=["POST"])
@check_text_field(app)
def correct_grammar_api():
    text = request.form["text"]
    
    if text:
        corrected_text = correct_grammar(app.config["grammar_model"], app.config["grammar_tokenizer"], device_hardware, text)
    else:
        logger.info("Empty text provided.")
        corrected_text = text

    response_data = {
        "corrected_text": corrected_text,
        'status': 200
    }

    return jsonify(response_data)

@app.route("/healthz/", methods=["GET"])
def health_check():
    return "Welcome to the grammar checker api."