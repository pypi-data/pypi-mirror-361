import pytest
from unifai import UnifAI, ProviderName
from unifai.types import Message, Tool, Embeddings, Embedding, ResponseInfo, Usage
from unifai.exceptions import ProviderUnsupportedFeatureError, BadRequestError, EmbeddingDimensionsError
from basetest import base_test_embedders, base_test, API_KEYS




@pytest.mark.parametrize("input", [
    "Embed this",
    ["Embed this"],
    ["Embed this", "And this"],
    ("Embed this", "And this"),
])
# @base_test(
#     "google", 
#     "openai", 
#     # "ollama", 
#     "cohere",
#     "nvidia",
# )
@base_test_embedders
def test_embeddings_simple(
    provider: ProviderName, 
    init_kwargs: dict, 
    input: str|list[str]
    ):

    ai = UnifAI(api_keys=API_KEYS, provider_configs=[{"provider": provider, "init_kwargs": init_kwargs}])

    if provider == "anthropic":
        with pytest.raises((ProviderUnsupportedFeatureError, AttributeError)):
            result = ai.embed(input, provider)
        return
    
    result = ai.embed(input, provider)

    assert isinstance(result, Embeddings)
    assert isinstance(result.list(), list)
    assert all(isinstance(embedding, list) for embedding in result)
    assert all(isinstance(embedding[0], float) for embedding in result)
    assert isinstance(result.response_info, ResponseInfo)
    assert isinstance(result.response_info.usage, Usage)
    assert isinstance(result.response_info.usage.total_tokens, int)
    # assert result.response_info.usage.input_tokens > 0
    # assert result.response_info.usage.output_tokens == 0
    assert result.response_info.usage.total_tokens == result.response_info.usage.input_tokens


    assert result[0] == result[0]
    assert isinstance(result[0], list)
    assert len(result) == len(result)    
    expected_length = 1 if isinstance(input, str) else len(input) if hasattr(input, "__len__") else 2
    assert len(result) == expected_length

    for i, embedding in enumerate(result):
        assert embedding in result
        assert result[i] == embedding
        assert result[i] == embedding

        
    other_result = Embeddings(
        root=[[0.1]], 
        response_info=ResponseInfo(model="other_model", usage=Usage(input_tokens=1, output_tokens=0))
    )
    combined_result = result + other_result
    assert isinstance(combined_result, Embeddings)
    assert len(combined_result) == len(result) + len(other_result)
    assert combined_result == result + other_result

    result += other_result
    assert isinstance(result, Embeddings)
    assert len(result) == len(combined_result)
    assert result == combined_result
    assert result.response_info and combined_result.response_info
    assert result.response_info.model == combined_result.response_info.model

    texts = input if isinstance(input, list) else [input]
    for text, embedding in zip(texts, result):
        print(f"Text: {text}\nEmbedding: {embedding[0]} and {len(embedding) -1 } more\n")



@pytest.mark.parametrize("input, dimensions", [
    ("Embed this", 100),
    (["Embed this longer text"], 100),
    ("Embed this", 1000),
    (["Embed this longer text"], 1000),
    ("Embed this", 1),
    (["Embed this longer text"], 1),
])
@base_test_embedders
def test_embeddings_dimensions(
    provider: ProviderName, 
    init_kwargs: dict, 
    input: str|list[str],
    dimensions: int
    ):

    ai = UnifAI(api_keys=API_KEYS, provider_configs=[{"provider": provider, "init_kwargs": init_kwargs}])

    result = ai.embed(input, 
                     provider, 
                      dimensions=dimensions,
                      reduce_dimensions=True,
                            )     
    
    assert isinstance(result, Embeddings)
    for embedding in result:
        assert len(embedding) <= dimensions
        assert all(isinstance(value, float) for value in embedding)



@pytest.mark.parametrize("input, dimensions", [
    ("Embed this zero", 0),
    ("Embed this negative", -1),
    ("Embed this huge", 1000000),
])
@pytest.mark.parametrize("reduce_dimensions", [True, False])
@base_test_embedders
def test_embeddings_dimensions_errors(
    provider: ProviderName, 
    init_kwargs: dict, 
    input: str|list[str],
    dimensions: int,
    reduce_dimensions: bool    
    ):

    ai = UnifAI(api_keys=API_KEYS, provider_configs=[{"provider": provider, "init_kwargs": init_kwargs}])
    if dimensions >= 1 and reduce_dimensions:
        result = ai.embed(
            input, 
           provider, 
            dimensions=dimensions,
            reduce_dimensions=reduce_dimensions,        )            
        assert isinstance(result, Embeddings)
        for embedding in result:
            assert len(embedding) <= dimensions
            assert all(isinstance(value, float) for value in embedding)
            print(f"Embedding: {embedding[0]} and {len(embedding) -1 } more\n")

    else:                
        with pytest.raises((EmbeddingDimensionsError, BadRequestError,)):
            result = ai.embed(
                input, 
               provider, 
                dimensions=dimensions,
                reduce_dimensions=reduce_dimensions,
            )
    
