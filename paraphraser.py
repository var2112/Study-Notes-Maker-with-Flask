from transformers import *
model = PegasusForConditionalGeneration.from_pretrained(
    "tuner007/pegasus_paraphrase")
tokenizer = PegasusTokenizerFast.from_pretrained(
    "tuner007/pegasus_paraphrase")


def get_paraphrased_sentences(sent):
    sentence = "paraphrase: " + sent + " </s>"
    encoding = tokenizer.encode_plus(
        sentence, padding=True, return_tensors="pt")
    input_ids, attention_masks = encoding["input_ids"], encoding["attention_mask"]

    outputs = model.generate(input_ids=input_ids, attention_mask=attention_masks, max_length=256,
                             do_sample=True, top_k=120, top_p=0.95, early_stopping=True, num_return_sequences=1)
    output = tokenizer.decode(
        outputs[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
    return output
