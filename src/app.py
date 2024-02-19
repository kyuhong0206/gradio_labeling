import bsddb3.db as bdb
import gradio as gr
import json
import pickle
from PIL import Image

db = None
image_data_dict = None
index = None
etrieved_data_dict = None
index_db = None
user_name = None

def index_changer(input_index, increase = True):
    input_index = int(input_index.decode())
    if increase:
        input_index +=1
        return str(input_index).encode()
    input_index -=1
    return str(input_index).encode()

def display_image(image_path):
    return Image.open(image_path)

def start_func(user_dropdown):
    global db
    global image_data_dict
    global index
    global etrieved_data_dict
    global index_db
    global user_name

    user_name = user_dropdown

    # set DB
    db = bdb.DB()
    db.open(f"/home/ai04/workspace/gradio_labeling/data/{user_name}.db", None, bdb.DB_HASH, bdb.DB_CREATE)

    index_db = bdb.DB()
    index_db.open("/home/ai04/workspace/gradio_labeling/data/user_index.db", None, bdb.DB_HASH, bdb.DB_CREATE)

    index = index_db[user_name.encode()]
    data_bytes = db[index]
    etrieved_data_dict = pickle.loads(data_bytes)
    image_file_path = etrieved_data_dict['file_path']
    class_name = etrieved_data_dict['class_name']
    anno_text = etrieved_data_dict['annotation']

    return Image.open(image_file_path), class_name, anno_text



def anno_func(anno):
    global db
    global image_data_dict
    global index
    global etrieved_data_dict
    global index_db
    global user_name

    etrieved_data_dict['annotation'] = anno
    dict_bytes = pickle.dumps(etrieved_data_dict)
    db[index] = dict_bytes
    db.sync()

    index = index_changer(index, increase = True)
    data_bytes = db[index]
    etrieved_data_dict = pickle.loads(data_bytes)
    image_file_path = etrieved_data_dict['file_path']
    class_name = etrieved_data_dict['class_name']
    anno_text = etrieved_data_dict['annotation']
    index_db[user_name.encode()] = index
    index_db.sync()

    return Image.open(image_file_path), class_name, anno_text

def move_func(status):
    global image_data_dict
    global index

    if status == 'prev':
        index = index_changer(index, increase = False)
        data_bytes = db[index]
        etrieved_data_dict = pickle.loads(data_bytes)
        image_file_path = etrieved_data_dict['file_path']
        class_name = etrieved_data_dict['class_name']
        anno_text = etrieved_data_dict['annotation']
        return Image.open(image_file_path), class_name, anno_text
    if status == 'next':
        index = index_changer(index, increase = True)
        data_bytes = db[index]
        etrieved_data_dict = pickle.loads(data_bytes)
        image_file_path = etrieved_data_dict['file_path']
        class_name = etrieved_data_dict['class_name']
        anno_text = etrieved_data_dict['annotation']
        return Image.open(image_file_path), class_name, anno_text

with gr.Blocks() as demo:
    gr.Markdown("label test")
    with gr.Row():
        user_dropdown = gr.Dropdown(["user1", "user2", "user3","test"], label = "user")
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
        skip_button = gr.Button('Skip')
    with gr.Row():
        anno_text = gr.Textbox(value = 'annotation here!!')

    true_anno = gr.Textbox(value = 'True', visible = False)
    false_anno = gr.Textbox(value = 'False', visible = False)
    skip_anno = gr.Textbox(value = 'Skip', visible = False)

    prev_text = gr.Textbox(value = 'prev', visible =False)
    next_text = gr.Textbox(value = 'next', visible =False)

    start_button.click(start_func, inputs = [user_dropdown], outputs = [image_output, class_text, anno_text])
    true_button.click(anno_func, inputs = [true_anno], outputs = [image_output, class_text, anno_text])
    false_button.click(anno_func, inputs = [false_anno], outputs = [image_output, class_text, anno_text])
    skip_button.click(anno_func, inputs = [skip_anno], outputs = [image_output, class_text, anno_text])
    prev_button.click(move_func, inputs = prev_text, outputs=[image_output, class_text, anno_text])
    next_button.click(move_func, inputs = next_text, outputs=[image_output, class_text, anno_text])

demo.launch(ssl_verify=False,share=True,server_name="0.0.0.0")