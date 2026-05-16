import pathlib

path = pathlib.Path(r'C:\Users\ajeem\.cache\huggingface\modules\transformers_modules\ai4bharat\indictrans2_hyphen_indic_hyphen_en_hyphen_dist_hyphen_200M\eb9e49d81077cfc5311e82ff36d8c1fc11557b5d\modeling_indictrans.py')

content = path.read_text(encoding='utf-8')

old = """    def tie_weights(self, **kwargs):
        if self.config.share_decoder_input_output_embed:
            self._tie_or_clone_weights(self.model.decoder.embed_tokens, self.lm_head)"""

new = """    def tie_weights(self, **kwargs):
        if self.config.share_decoder_input_output_embed:
            self.lm_head.weight = self.model.decoder.embed_tokens.weight"""

if old in content:
    content = content.replace(old, new)
    path.write_text(content, encoding='utf-8')
    print("Done! tie_weights fixed successfully.")
else:
    print("Pattern not found — no changes made.")
