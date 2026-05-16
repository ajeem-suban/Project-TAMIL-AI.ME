import pathlib

path = pathlib.Path(r'C:\Users\ajeem\Project-TAMIL-AI.ME\ai4bharat_service.py')
content = path.read_text(encoding='utf-8')

old = '''    def translate(self, tamil_text: str) -> str:
        try:
            input_text = f">>tam_Taml<< {tamil_text}"
            encoded = self.tokenizer(
                input_text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=256,
            ).to(DEVICE)

            with torch.no_grad():
                generated = self.model.generate(
                    **encoded,
                    max_length=256,
                    num_beams=4,
                    early_stopping=True,
                )
            return self.tokenizer.decode(generated[0], skip_special_tokens=True)
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return "[Translation failed]"'''

new = '''    def translate(self, tamil_text: str) -> str:
        try:
            # IndicTrans2 format: src_lang tgt_lang <text>
            input_text = f"tam_Taml eng_Latn {tamil_text}"
            self.tokenizer._switch_to_input_mode()
            encoded = self.tokenizer(
                input_text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=256,
            ).to(DEVICE)

            target_lang_id = self.tokenizer.convert_tokens_to_ids("eng_Latn")

            with torch.no_grad():
                generated = self.model.generate(
                    **encoded,
                    forced_bos_token_id=target_lang_id,
                    max_new_tokens=256,
                    num_beams=4,
                    early_stopping=True,
                )
            self.tokenizer._switch_to_target_mode()
            result = self.tokenizer.decode(generated[0], skip_special_tokens=True)
            self.tokenizer._switch_to_input_mode()
            return result
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return "[Translation failed]"'''

if old in content:
    content = content.replace(old, new)
    path.write_text(content, encoding='utf-8')
    print("Done! translate() method fixed.")
else:
    print("Pattern not found — no changes made.")
