from dataflow.operators.generate.KnowledgeCleaning import (
    CorpusTextSplitter,
    KnowledgeExtractor,
    KnowledgeCleaner,
    MultiHopQAGenerator,
)
from dataflow.utils.storage import FileStorage
from dataflow.llmserving import LocalModelLLMServing

class KBCleaningPipeline():
    def __init__(self):

        self.storage = FileStorage(
            first_entry_file_name="../example_data/KBCleaningPipeline/kbc_placeholder.json",
            cache_path="./.cache/gpu",
            file_name_prefix="pdf_cleaning_step",
            cache_type="json",
        )

        local_llm_serving = LocalModelLLMServing(
            model_name_or_path="Qwen/Qwen2.5-7B-Instruct",
            max_tokens=1024,
            tensor_parallel_size=4,
            model_source="local",
            gpu_memory_utilization=0.6,
            repetition_penalty=1.2
        )

        self.knowledge_cleaning_step1 = KnowledgeExtractor(
            intermediate_dir="../example_data/KBCleaningPipeline/raw/"
        )

        self.knowledge_cleaning_step2 = CorpusTextSplitter(
            split_method="token",
            chunk_size=512,
            tokenizer_name="Qwen/Qwen2.5-7B-Instruct",
        )

        self.knowledge_cleaning_step3 = KnowledgeCleaner(
            llm_serving=local_llm_serving,
            lang="en"
        )

        self.knowledge_cleaning_step4 = MultiHopQAGenerator(
            llm_serving=local_llm_serving,
            lang="en"
        )

    def forward(self, url:str=None, raw_file:str=None):
        extracted=self.knowledge_cleaning_step1.run(
            storage=self.storage,
            raw_file=raw_file,
            url=url,
            lang="en"
        )
        
        self.knowledge_cleaning_step2.run(
            storage=self.storage.step(),
            input_file=extracted,
            output_key="raw_content",
        )

        self.knowledge_cleaning_step3.run(
            storage=self.storage.step(),
            input_key= "raw_content",
            output_key="cleaned",
        )
        self.knowledge_cleaning_step4.run(
            storage=self.storage.step(),
            input_key="cleaned",
            output_key="MultiHop_QA"
        )
        
if __name__ == "__main__":
    model = KBCleaningPipeline()
    model.forward(raw_file="../example_data/KBCleaningPipeline/test.pdf")