from langchain.chains.qa_with_sources.loading import load_qa_with_sources_chain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI

from utils import generate_answer
from utils import get_search_index

open_ai_pkl = "open_ai.pkl"
open_ai_index = "open_ai.index"

gpt_3_5 = OpenAI(model_name='gpt-3.5-turbo',temperature=0)

open_ai_embeddings = OpenAIEmbeddings()

def run(question):

    gpt_3_5_index = get_search_index(open_ai_pkl, open_ai_index, open_ai_embeddings)

    gpt_3_5_chain = load_qa_with_sources_chain(gpt_3_5, chain_type="stuff", verbose=True)

    answer = generate_answer(gpt_3_5_chain, gpt_3_5_index, question)
    return answer
