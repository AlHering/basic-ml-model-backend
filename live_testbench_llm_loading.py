# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from src.utility.gold.transformer_model_utility import spawn_language_model_instance


vicuna_7b_config = {
    "path": "TheBloke_vicuna-7B-v1.3-GGML/vicuna-7b-v1.3.ggmlv3.q4_0.bin",
    "type": "llamacpp",
    "loader": "_default",
    "context": 2048,
    "verbose": True
}


orca_3b_config = {
    "path": "TheBloke_orca_mini_3B-GGML/orca-mini-3b.ggmlv3.q5_0.bin",
    "type": "llamacpp",
    "loader": "_default",
    "context": 2048,
    "verbose": True
}


orca_7b_config = {
    "path": "TheBloke_orca_mini_7B-GGML/orca-mini-7b.ggmlv3.q5_0.bin",
    "type": "llamacpp",
    "loader": "_default",
    "context": 2048,
    "verbose": True
}


llm = spawn_language_model_instance(orca_7b_config)

response = llm.generate("You are an assistant. Give me a list of fruit trees.")
generation_batches = response.generations
llm_output = response.llm_output
run_info = response.run
print(llm_output)
print(run_info)
print("="*20)
for batch in generation_batches:
    for generation in batch:
        print(generation.text)
