import streamlit as st

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

import os


def load_document(file, query=None):
    '''
    Loads the file using the appropriate loader.
    '''
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_community.document_loaders import Docx2txtLoader
    from langchain_community.document_loaders import TextLoader
    from langchain_community.document_loaders import JSONLoader

    filename, extension = os.path.splitext(file)

    if extension == '.pdf':
        print(f"Loading {extension}.")
        loader = PyPDFLoader(file)

    elif extension == '.docx' or extension == '.doc':
        print(f"Loading {extension}.")
        loader = Docx2txtLoader

    elif extension == '.txt':
        print(f"Loading {extension}.")
        loader = TextLoader(file)

    elif extension == '.json':
        print(f"Loading {extension}.")
        loader = JSONLoader(file)

    else:
        print(f"{extension} not supported.")
        return None

    data = loader.load()
    return data


def chunk_data(data, chunk_size=256, chunk_overlap=20):
    '''
    Breaks down the data into smaller segments.
    '''
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_documents(data)
    return chunks


def create_embeddings(chunks):
    '''
    Embeds the data into ChromaDB.
    '''
    embeddings = OpenAIEmbeddings(model='text-embedding-3-small', dimensions=1536)
    vector_store = Chroma.from_documents(
        chunks,
        embedding=embeddings
    )
    return vector_store


def embedding_cost(chunks):
    '''
    Calculates the embedding cost.
    '''
    import tiktoken
    enc = tiktoken.encoding_for_model('text-embedding-3-small')
    total_tokens = sum([len(enc.encode(page.page_content)) for page in chunks])
    return total_tokens, total_tokens / 1000 * 0.0004


def conversation_chain(vector_store, query, temp=0.2, k=3):
    '''
    Creates a ConversationalRetrievalChain
    '''
    from langchain_openai import ChatOpenAI
    from langchain.memory import ConversationBufferMemory
    from langchain.chains import ConversationalRetrievalChain

    llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=temp)
    retriever = vector_store.as_retriever(searc_type='similarity', search_kwargs={'k': k})
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        chain_type='stuff',
        verbose=False
    )

    result = chain.invoke(query)
    return result['answer']


def chat_page():

    st.title("Chat with your data!")
    # Ensure that the document is loaded
    if 'vs' not in st.session_state:
        st.warning("Please upload a document in the Configuration page.")
        return

    # Initialize chat history if not already done
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask a question"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Generate response
        vector_store = st.session_state.vs
        temp = st.session_state.get('temp', 0.2)
        k = st.session_state.get('k', 3)
        answer = conversation_chain(vector_store, prompt, temp, k)

        # Display AI response
        with st.chat_message("assistant"):
            st.markdown(answer)
        # Add AI response to chat history
        st.session_state.messages.append({"role": "assistant", "content": answer})