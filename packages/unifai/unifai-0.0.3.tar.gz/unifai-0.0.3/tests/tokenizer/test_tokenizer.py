import pytest
from typing import Optional, Literal

from unifai import UnifAI
from unifai.components._base_components._base_tokenizer import Tokenizer
from basetest import base_test, base_test_tokenizers, API_KEYS

@base_test_tokenizers
def test_init_tokenizers(provider, init_kwargs):
    ai = UnifAI(api_keys=API_KEYS, provider_configs=[{"provider": provider, "init_kwargs": init_kwargs}])
    tokenizer = ai.tokenizer_from_config(provider)
    assert isinstance(tokenizer, Tokenizer)
    assert tokenizer.provider == provider
    

@base_test_tokenizers
def test_tokenize_hello_world(provider, init_kwargs):
    ai = UnifAI(api_keys=API_KEYS, provider_configs=[{"provider": provider, "init_kwargs": init_kwargs}])

    tokenizer = ai.tokenizer_from_config(provider)
    hello_world = "Hello world"
    token_ids = tokenizer.encode(hello_world)
    print("tokenizer.encode Token Ids:", token_ids)
    assert all(isinstance(token_id, int) for token_id in token_ids)

    decoded = tokenizer.decode(token_ids)
    print("tokenizer.decode Decoded:", decoded)
    assert decoded == hello_world

    tokens = tokenizer.tokenize(hello_world)
    print("tokenizer.tokenize Tokens:", tokens)
    for token in tokens:
        assert isinstance(token, str)
        assert len(token) > 0
        assert token in hello_world #or token.startswith(("[", "Ġ"))

    token_count = tokenizer.count_tokens(hello_world)
    # special_tokens = tokenizer.
    print("tokenizer.count_tokens Token Count:", token_count)
    assert token_count == len(tokens)
    assert token_count == len(token_ids)
    assert len(hello_world.split()) == token_count
