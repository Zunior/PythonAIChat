import openai
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain_community.document_loaders import TextLoader

import Constants
from QueryTypeEnum import QueryType

class OpenAI(object):

    @staticmethod
    def _create_vector_index(loader, persist_enabled, db_directory):
        """
        Creates a VectorstoreIndex from a loader,
        optionally persisting it to a directory.
        """
        if persist_enabled:
            return VectorstoreIndexCreator(
                vectorstore_kwargs={"persist_directory": db_directory}
            ).from_loaders([loader])
        else:
            return VectorstoreIndexCreator().from_loaders([loader])

    @staticmethod
    def _handle_api_exceptions(func, *args, **kwargs):
        """
        Wraps a callable and handles specific OpenAI API exceptions,
        re-raising as more descriptive exceptions.
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, openai.RateLimitError):
                raise Exception("Rate limit exceeded too many times.") from e
            elif isinstance(e, openai.APIConnectionError):
                raise Exception("The server could not be reached.") from e
            else:
                # Re-raise any other unexpected exception
                raise e

    @staticmethod
    def _get_loader(query_type):
        if query_type == QueryType.LOCAL:
            return DirectoryLoader(Constants.LOCAL_DATA_DIR, Constants.LOCAL_DATA_FILE_TXT)
        elif query_type == QueryType.GLOBAL:
            return TextLoader(Constants.NO_LOCAL_DATA)
        elif query_type == QueryType.BOTH:
            return DirectoryLoader(Constants.LOCAL_DATA_DIR, Constants.LOCAL_DATA_FILE_TXT)
        else:
            raise ValueError(f"Unknown query_type: {query_type}")

    def return_answer(self, query_type, question_value):
        PERSIST = True
        chat_history = [];

        # Initialize loader based on query_type
        loader = self._get_loader(query_type)

        # Create index using the helper function
        index = self._create_vector_index(loader, PERSIST, Constants.CHROMA_DB_DIR)

        # Common chain for GLOBAL and BOTH
        if query_type in (QueryType.GLOBAL, QueryType.BOTH):
            llm_model = ChatOpenAI(model=Constants.GPT_turbo)
            retriever_instance = index.vectorstore.as_retriever(search_kwargs={"k": 1})
            chain = ConversationalRetrievalChain.from_llm(
                llm=llm_model,
                retriever=retriever_instance,
            )

        # Perform query based on query_type using the exception handling helper
        match query_type:
            case QueryType.LOCAL:
                result = self._handle_api_exceptions(index.query, question_value)
                chat_history.append(result) # Note: LOCAL appends raw result, GLOBAL/BOTH appends (q,a) tuple
                return result, chat_history
            case QueryType.GLOBAL:
                result_dict = self._handle_api_exceptions(chain.invoke, {"question": question_value, "chat_history": chat_history})
                result_answer = result_dict['answer']
                chat_history.append((question_value, result_answer))
                return result_answer, chat_history
            case QueryType.BOTH:
                result_dict = self._handle_api_exceptions(chain.invoke, {"question": question_value, "chat_history": chat_history})
                result_answer = result_dict['answer']
                chat_history.append((question_value, result_answer))
                return result_answer, chat_history
