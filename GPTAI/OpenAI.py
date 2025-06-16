from langchain.document_loaders import DirectoryLoader
# from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain_community.document_loaders import TextLoader
from langchain.indexes import VectorstoreIndexCreator
# from langchain.vectorstores import Chroma
# from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from QueryTypeEnum import QueryType
import constants
import openai

class OpenAI(object):
    _NO_LOCAL_DATA = "./Data/blankData.txt"
    _LOCAL_DATA_DIR = "./Data"
    _LOCAL_DATA_FILE_ALL = "**/[!.]*"
    _LOCAL_DATA_FILE_TXT = "*.txt"
    _CHROMA_DB_DIR = "./chromaDB"

    def return_answer(self, queryType, questionValue):
        PERSIST = True
        chat_history = []

        match queryType:
            case QueryType.LOCAL:
                loader = DirectoryLoader(OpenAI._LOCAL_DATA_DIR, OpenAI._LOCAL_DATA_FILE_TXT)
                if PERSIST:
                    index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory": OpenAI._CHROMA_DB_DIR}).from_loaders([loader])
                else:
                    index = VectorstoreIndexCreator().from_loaders([loader])
                try:
                    result = index.query(questionValue)
                    chat_history.append(result)
                    return result, chat_history
                except Exception as e:
                    if isinstance(e, openai.RateLimitError):
                        raise Exception("Rate limit exceeded too many times.") from e
                    elif isinstance(e, openai.APIConnectionError):
                        raise Exception("The server could not be reached.") from e
                    else:
                        raise e
            case QueryType.GLOBAL:
                loader = TextLoader(OpenAI._NO_LOCAL_DATA)
                if PERSIST:
                    index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory": OpenAI._CHROMA_DB_DIR}).from_loaders([loader])
                else:
                    index = VectorstoreIndexCreator().from_loaders([loader])
                chain = ConversationalRetrievalChain.from_llm(
                    llm=ChatOpenAI(model=constants.GPT_turbo),
                    retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
                )
                try:
                    result = chain({"question": questionValue, "chat_history": chat_history})
                    chat_history.append((questionValue, result['answer']))
                    return result['answer'], chat_history
                except Exception as e:
                    if isinstance(e, openai.RateLimitError):
                        raise Exception("Rate limit exceeded too many times.") from e
                    elif isinstance(e, openai.APIConnectionError):
                        raise Exception("The server could not be reached.") from e
                    else:
                        raise e
            case QueryType.BOTH:
                loader = DirectoryLoader(OpenAI._LOCAL_DATA_DIR, OpenAI._LOCAL_DATA_FILE_TXT)
                if PERSIST:
                    index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory": OpenAI._CHROMA_DB_DIR}).from_loaders([loader])
                else:
                    index = VectorstoreIndexCreator().from_loaders([loader])
                chain = ConversationalRetrievalChain.from_llm(
                    llm=ChatOpenAI(model=constants.GPT_turbo),
                    retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
                )
                try:
                    result = chain({"question": questionValue, "chat_history": chat_history})
                    chat_history.append((questionValue, result['answer']))
                    return result['answer'], chat_history
                except Exception as e:
                    if isinstance(e, openai.RateLimitError):
                        raise Exception("Rate limit exceeded too many times.") from e
                    elif isinstance(e, openai.APIConnectionError):
                        raise Exception("The server could not be reached.") from e
                    else:
                        raise e
