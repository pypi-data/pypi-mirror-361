def wasif_rag(history, query, context_path):

    from langchain import LLMChain, PromptTemplate
    from langchain.memory.buffer import ConversationBufferMemory
    from langchain.schema.runnable import RunnablePassthrough
    from langchain_core.output_parsers import StrOutputParser
    from langchain_community.document_loaders import TextLoader
    from langchain_text_splitters import CharacterTextSplitter
    from langchain_community.vectorstores import FAISS
    from langchain.embeddings import HuggingFaceEmbeddings
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    from langchain import HuggingFacePipeline, PromptTemplate, LLMChain
    import torch

    class StoryCreativityChain:
        def __init__(self):

            model_name = "NousResearch/Llama-2-7b-chat-hf"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype="auto",  
                device_map="auto",   
                load_in_4bit=True   
            )
            
            self.llmPipeline = pipeline("text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            torch_dtype=torch.float16,
            device_map="auto",
            max_new_tokens=100,
            do_sample=True,
            top_k=30,
            num_return_sequences=1,
            eos_token_id=self.tokenizer.eos_token_id
            )
            self.llm = HuggingFacePipeline(pipeline=self.llmPipeline, model_kwargs={'temperature': 0.7, 'max_length': 5, 'top_k': 50})
            
        def getPromptFromTemplate(self):
            system_prompt = """You are a helpful assistant, you will use the provided history and context to answer user questions.
            Read the given context and history before answering questions and think step by step. If you cannot answer a user question based on
            the provided context, inform the user. Do not use any other information for answering the user. Provide a detailed answer to the question."""

            B_INST, E_INST = "[INST]", "[/INST]"
            B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
            SYSTEM_PROMPT1 = B_SYS + system_prompt + E_SYS

            instruction = f"""
            History: {history} \n"""

            instruction += """
            Context: {context} \n
            User: {question}"""

            prompt_template = B_INST + SYSTEM_PROMPT1 + instruction + E_INST
            prompt = PromptTemplate(input_variables=["history", "question", "context"], template=prompt_template)

            return prompt

        def buildRetrieval(self, model_name="sentence-transformers/all-MiniLM-L6-v2", text_files=[context_path]):
            all_docs = []
            for file in text_files:
                loader = TextLoader(file)
                document = loader.load()
                all_docs.append(document[0])
        
            embeddings = HuggingFaceEmbeddings(model_name=model_name)
        
            text_splitter = CharacterTextSplitter(chunk_size=10, chunk_overlap=0, separator=".")
            texts = text_splitter.split_documents(all_docs)
        
            # embeddings = HuggingFaceInstructEmbeddings()
            db = FAISS.from_documents(texts, embeddings)
        
            retriever = db.as_retriever()
            return retriever

        def getNewChain(self):
            prompt = self.getPromptFromTemplate()
            memory = ConversationBufferMemory(input_key="question", memory_key="history", max_len=5)
            retriever = self.buildRetrieval()
            # Initialize LLMChain with proper parameters
            llm_chain = LLMChain(prompt=prompt, llm=self.llm, verbose=True, memory=memory, output_parser=CustomOutputParser())
            parser = StrOutputParser()
            rag_chain = (
                {"context": retriever, "question": RunnablePassthrough()}
                | llm_chain
            )

            return rag_chain, retriever

    class CustomOutputParser(StrOutputParser):
        def parse(self, response: str):
            return response.split('[/INST]')[-1].strip()

    def getAnswer(chain, question):
        response = chain.invoke(question)
        print(response['text'])
        
    story = StoryCreativityChain()
    chain, retriever = story.getNewChain()

    response  = getAnswer(chain, query)
    
    return response