import streamlit as st
import json
from PIL import Image
from streamlit_utils import *

st.set_page_config(
    page_title="ChatGLM-6B streamlit",
    layout="wide"
)
st.title('ChatGLM-6B streamlit')
st.sidebar.expander('')
st.sidebar.subheader('Parameters')
prompt = st.sidebar.text_area('Prompt', help = "Text send  to ChatGLM-6B")
send = st.sidebar.button("Send", key = "send_prompt", help = "Send text to ChatGLM-6B")
mode = st.sidebar.radio("Feature",('Default', 'Stable Diffusion', 'Web'))
max_length = st.sidebar.slider("Max Length", min_value = 1024, max_value = 8192, value = 2048, step = 1024, help = "Prompt Max Length")
temperature = st.sidebar.slider("Temperature", min_value = 0.10, max_value = 1.00, value = 0.95, step = 0.05)
top_p = st.sidebar.slider("Top_p", min_value = 0.1, max_value = 1.0, value = 0.7, step = 0.1)
input_history = st.sidebar.text_area("History", height = 5, value="[]", help = "The history sended")

if mode == "Default":
    if send:
        if not prompt == "":
            prompt_text = prompt
            request = chatglm_json(str(prompt_text), json.loads(input_history), int(max_length), float(top_p), float(temperature))
            request_list = json.loads(request)
            response = request_list.get('response')
            history = request_list.get('history')
            st.markdown("### User: ")
            st.markdown(prompt_text)
            st.markdown('### ChatGLM-6B: ')
            st.markdown(response)
            st.sidebar.text('Local History')
            st.sidebar.json(history)

if mode == "Stable Diffusion":
    if send:
        if not prompt == "":
            prompt_text = prompt
            prompt_history = [["我接下来会给你一些作画的指令，你只要回复出作画内容及对象，不需要你作画，不需要给我参考，不需要你给我形容你的作画内容，请直接给出作画内容，你不要回复”好的，我会画一张“等不必要的内容，你只需回复作画内容。你听懂了吗","听懂了。请给我一些作画的指令。"]]
            request = chatglm_json(str(f"不需要你作画，不需要给我参考，不需要你给我形容你的作画内容，请给出“{prompt_text}”中的作画内容，请直接给出作画内容和对象"), prompt_history, int(max_length), float(top_p), float(temperature))
            request_list = json.loads(request)
            draw_object = request_list.get('response')
            if draw_object[0] == "，" or draw_object[0] == "," or draw_object[0] == "。" or draw_object[0] == ".":
                draw_object = draw_object[1:len(draw_object)]
            if draw_object[-1] == "，" or draw_object[-1] == "," or draw_object[-1] == "。" or draw_object[-1] == ".":
                draw_object = draw_object[0:len(draw_object)-1]
            draw_object = draw_object.replace("好的", "")
            draw_object = draw_object.replace("我", "")
            draw_object = draw_object.replace("将", "")
            draw_object = draw_object.replace("会", "")
            draw_object = draw_object.replace("画", "")
            if draw_object[0] == "，" or draw_object[0] == "," or draw_object[0] == "。" or draw_object[0] == ".":
                draw_object = draw_object[1:len(draw_object)]
            if draw_object[-1] == "，" or draw_object[-1] == "," or draw_object[-1] == "。" or draw_object[-1] == ".":
                draw_object = draw_object[0:len(draw_object)-1]
            stable_diffusion(str(translate(draw_object)),"")
            st.markdown("### User: ")
            st.markdown(prompt_text)
            st.markdown('### ChatGLM-6B: ')
            image = Image.open('stable_diffusion.png')
            st.markdown(f'好的，这是通过 Stable Diffusion 画出的{draw_object}')
            st.image(image, caption=draw_object+' (Drawing with Stable Diffusion)')
            st.sidebar.text('Local History')
            st.sidebar.json([])

if mode == "Web":
    feature = st.sidebar.multiselect('Feature requests',['知乎专栏','知乎回复','百科','微信公众号','新闻','B站专栏','CSDN','GitHub'])
    web_max_length = st.sidebar.number_input("Web info Max Length", min_value=0, step=1, value=200)
    if send:
        if not prompt == "":
            prompt_text = prompt
            if not feature == []:
                web_info = search_main(str(prompt_text), feature)
                new_web_info = []
                for items in web_info:
                    if len(items) >= web_max_length:
                        new_web_info.append(items[0:web_max_length])
                    else:
                        new_web_info.append(items)
                ask_prompt = f'我的问题是“{prompt_text}”\n我在网上查询到了一些参考信息“{new_web_info}”\n请根据我的问题，参考我给与的信息以及你的理解进行回复'
                print(ask_prompt)
                request = chatglm_json(str(ask_prompt), json.loads("[]"), int(max_length), float(top_p), float(temperature))
                request_list = json.loads(request)
                response = request_list.get('response')
                history = request_list.get('history')
                st.markdown("### User: ")
                st.markdown(prompt_text)
                st.markdown('### ChatGLM-6B: ')
                st.markdown(response)
                st.sidebar.text('Local History')
                st.sidebar.json(history)
            else:
                st.error('No feature selected')