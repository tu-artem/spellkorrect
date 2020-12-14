from typing import Tuple, List

from pydantic import BaseModel
import torch
from transformers import BertTokenizer, BertForMaskedLM

from src.utils import candidates, replace_from


class Correction(BaseModel):
    start: int
    end: int
    original_token: str
    corrected_token: str


class CorrectorResponse(BaseModel):
    original_text: str
    corrected_text: str
    corrections: List[Correction]


class Corrector:
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        self.vocab = set(self.tokenizer.get_vocab().keys())
        self.model = BertForMaskedLM.from_pretrained(
            "bert-base-uncased", return_dict=True
        )
        self.model.eval()

    def correct(self, sentence: str) -> CorrectorResponse:
        tokens = self.tokenizer.basic_tokenizer.tokenize(
            sentence, never_split=self.tokenizer.all_special_tokens
        )
        unknowns = [token for token in tokens if token not in self.vocab]

        corrections = []
        search_from = 0

        corrected = sentence.lower()  # TODO: investigate how to keep original casing

        for unk in unknowns:
            cnds = list(candidates(unk, self.vocab))
            start = sentence.lower().find(unk, search_from)
            end = start + len(unk)

            # replace current unknown token with bert mask
            corrected = replace_from(unk, "[MASK]", corrected, search_from)

            tensor_input = self.tokenizer(corrected, return_tensors="pt")
            logits = self.model(**tensor_input)

            # position of unknown token
            masked_index = torch.where(
                tensor_input["input_ids"] == self.tokenizer.mask_token_id
            )[1]
            candidates_ids = [self.tokenizer.convert_tokens_to_ids(tok) for tok in cnds]
            word = cnds[logits[0][0, masked_index[0], candidates_ids].argmax()]

            corrected = replace_from("[MASK]", word, corrected, search_from)

            search_from = end

            correction = Correction(
                start=start, end=end, original_token=unk, corrected_token=word
            )

            corrections.append(correction)

        payload = CorrectorResponse(
            original_text=sentence, corrected_text=corrected, corrections=corrections
        )

        return payload
