import pathlib

content = '''# coding=utf-8
from transformers.configuration_utils import PretrainedConfig


class IndicTransConfig(PretrainedConfig):
    model_type = "IndicTrans"
    keys_to_ignore_at_inference = ["past_key_values"]
    attribute_map = {
        "num_attention_heads": "encoder_attention_heads",
        "hidden_size": "d_model",
    }

    def __init__(
        self,
        encoder_vocab_size=None,
        decoder_vocab_size=None,
        encoder_embed_dim=512,
        decoder_embed_dim=512,
        max_source_positions=210,
        max_target_positions=210,
        encoder_layers=6,
        encoder_ffn_dim=2048,
        encoder_attention_heads=8,
        decoder_layers=6,
        decoder_ffn_dim=2048,
        decoder_attention_heads=8,
        encoder_layerdrop=0.00,
        decoder_layerdrop=0.00,
        use_cache=True,
        is_encoder_decoder=True,
        activation_function="relu",
        encoder_normalize_before=False,
        decoder_normalize_before=False,
        layernorm_embedding=False,
        share_decoder_input_output_embed=False,
        dropout=0.1,
        attention_dropout=0.0,
        activation_dropout=0.0,
        init_std=0.02,
        scale_embedding=True,
        decoder_start_token_id=2,
        pad_token_id=1,
        bos_token_id=0,
        eos_token_id=2,
        attn_implementation="eager",
        **kwargs,
    ):
        self.encoder_vocab_size = encoder_vocab_size
        self.decoder_vocab_size = decoder_vocab_size
        self.encoder_normalize_before = encoder_normalize_before
        self.decoder_normalize_before = decoder_normalize_before
        self.layernorm_embedding = layernorm_embedding
        self.max_source_positions = max_source_positions
        self.max_target_positions = max_target_positions
        self.encoder_embed_dim = encoder_embed_dim
        self.decoder_embed_dim = decoder_embed_dim
        self.encoder_ffn_dim = encoder_ffn_dim
        self.encoder_layers = encoder_layers
        self.encoder_attention_heads = encoder_attention_heads
        self.decoder_ffn_dim = decoder_ffn_dim
        self.decoder_layers = decoder_layers
        self.decoder_attention_heads = decoder_attention_heads
        self.dropout = dropout
        self.attention_dropout = attention_dropout
        self.activation_dropout = activation_dropout
        self.activation_function = activation_function
        self.init_std = init_std
        self.encoder_layerdrop = encoder_layerdrop
        self.decoder_layerdrop = decoder_layerdrop
        self.use_cache = use_cache
        self.num_hidden_layers = encoder_layers
        self.scale_embedding = scale_embedding
        self.share_decoder_input_output_embed = share_decoder_input_output_embed
        self.attn_implementation = attn_implementation

        super().__init__(
            pad_token_id=pad_token_id,
            bos_token_id=bos_token_id,
            eos_token_id=eos_token_id,
            is_encoder_decoder=is_encoder_decoder,
            decoder_start_token_id=decoder_start_token_id,
            **kwargs,
        )
'''

p = pathlib.Path(r'C:\Users\ajeem\.cache\huggingface\modules\transformers_modules\ai4bharat\indictrans2_hyphen_indic_hyphen_en_hyphen_dist_hyphen_200M\eb9e49d81077cfc5311e82ff36d8c1fc11557b5d\configuration_indictrans.py')
p.write_text(content, encoding='utf-8')
print("Done! File fixed successfully.")
