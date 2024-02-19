import bsddb3.db as bdb
import gradio as gr
import json
from PIL import Image

db = None
image_data_dict = None
index = None



def display_image(image_path):
    return Image.open(image_path)

def start_func(user_dropdown):
    global db
    global image_data_dict
    global index

    user_name = user_dropdown

    with open(f'/home/ai04/data/label_test_data/{user_name}_task.json', 'r') as f:
        image_data_dict = json.load(f)
    # set DB
    db = bdb.DB()
    db.open(f"/home/ai04/data/user_db/{user_name}.db", None, bdb.DB_HASH, bdb.DB_CREATE)
    for item in list(image_data_dict.keys()):
        if db.get(item.encode('utf-8')):
            del image_data_dict[item]

    print(image_data_dict)
    index = 0
    return Image.open(list(image_data_dict.keys())[index]), list(image_data_dict.keys())[index]

def anno_func(anno):
    global db
    global image_data_dict
    global index

    db[list(image_data_dict.keys())[index].encode()] = anno.encode()
    db.sync()
    index += 1
    return Image.open(list(image_data_dict.keys())[index])

def move_func(status):
    global image_data_dict
    global index
    if status == 'prev':
        index -= 1
        return Image.open(list(image_data_dict.keys())[index])
    if status == 'next':
        index += 1
        return Image.open(list(image_data_dict.keys())[index])

with gr.Blocks() as demo:
    gr.Markdown("label test")
    with gr.Row():
        image_path = gr.Textbox(visible =False)
        user_dropdown = gr.Dropdown(["user1", "user2", "user3"], label = "user")
        start_button = gr.Button('start')
    with gr.Row():
        prev_button = gr.Button('prev')
        class_text = gr.Textbox(value = 'class name here!!')
        next_button = gr.Button('next')
    with gr.Row():
        image_output = gr.Image()
    with gr.Row():
        true_button = gr.Button('True')
        false_button = gr.Button('False')

    true_anno = gr.Textbox(value = 'True', visible =False)
    false_anno = gr.Textbox(value = 'False', visible =False)

    prev_text = gr.Textbox(value = 'prev', visible =False)
    next_text = gr.Textbox(value = 'next', visible =False)

    start_button.click(start_func, inputs=[user_dropdown], outputs=[image_output, image_path])
    true_button.click(anno_func, inputs=[true_anno], outputs = image_output)
    false_button.click(anno_func, inputs=[false_anno], outputs = image_output)
    prev_button.click(move_func, inputs = prev_text, outputs = image_output)
    next_button.click(move_func, inputs = next_text, outputs = image_output)

demo.launch(ssl_verify=False,share=True,server_name="0.0.0.0")