import streamlit as st
import os
import chat

def clear_history():
    if 'history' in st.session_state:
        del st.session_state['history']


def config_page():
    st.title("Configuration Settings")

    # API Key
    api_key = st.text_input("OPENAI_API_KEY: ", type='password')
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key

    # Sliders
    st.session_state.chunk_size = st.slider("Chunk size: ", min_value=128, max_value=1048, value=256,
                                            on_change=clear_history, help="Size of the data chunks to process. Larger chunks may improve performance but require more memory.")
    st.session_state.k = st.slider("K value: ", min_value=1, max_value=10, value=3, on_change=clear_history, help = "Specifies how many of the closest matching vectors should be retrieved from the database. For instance, if k=3, the retrieval process will return the 3 nearest neighbors to the query vector.")
    st.session_state.temp = st.slider("Temperature: ", min_value=0.01, max_value=1.0, value=0.2, step=0.01,
                                      on_change=clear_history, help="Controls the creativity of the models responses. Higher values enable more creative responses.")

    # File upload and processing
    if 'vs' not in st.session_state:
        uploaded_file = st.file_uploader("Upload file: ", type=['pdf', 'docx', 'txt', 'json'])

        if uploaded_file:
            with st.spinner("Processing file..."):
                bytes_data = uploaded_file.read()
                file_name = os.path.join('./', uploaded_file.name)
                with open(file_name, "wb") as f:
                    f.write(bytes_data)

                data = chat.load_document(file_name)
                chunks = chat.chunk_data(data, chunk_size=st.session_state.chunk_size)
                st.write(f"Chunk size: {st.session_state.chunk_size}, Chunks: {len(chunks)}")

                tokens, embed_cost = chat.embedding_cost(chunks)
                st.write(f"Embedding cost: {embed_cost:.4f}")

                vector_store = chat.create_embeddings(chunks)
                st.session_state.vs = vector_store
                st.success("File embedded.")
