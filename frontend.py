import os
import requests
import streamlit as st

st.set_page_config(page_title='DT1 AI Assistant', page_icon='🤖')
st.title('🤖 DT1 AI Assistant')
st.caption('Streamlit → Flask → OpenRouter')

api_base = (os.getenv('BASE_URL') or 'http://127.0.0.1:5001').rstrip('/')
model = st.selectbox('AI model', ['nvidia/nemotron-3-ultra-550b-a55b:free'])
question = st.text_area('Ask me something', placeholder='What is cloud computing?', height=130)

if st.button('Send', type='primary'):
    if not question.strip():
        st.warning('Please enter a question.')
    else:
        with st.spinner('Waiting for the AI...'):
            try:
                resp = requests.post(f'{api_base}/chat', json={'input': question, 'model_id': model}, timeout=120)
                data = resp.json()
                if resp.ok:
                    st.subheader('AI response')
                    st.write(data.get('ack') or '(No content returned)')
                else:
                    st.error(f'Backend HTTP {resp.status_code}: {data.get("error", "Unknown error")}')
                    if data.get('detail'):
                        st.code(data['detail'])
            except requests.exceptions.RequestException as exc:
                st.error(f'Cannot reach Flask backend: {exc}')
            except ValueError:
                st.error('The backend returned a non-JSON response.')

if st.button('Clear question'):
    st.rerun()
