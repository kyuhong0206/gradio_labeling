import bsddb3.db as bdb
import gradio as gr
import json
import pickle
from PIL import Image

db = None
# index = None
etrieved_data_dict = None
index_db = None
user_name = None

def index_changer(input_index, increase = True):
    input_index = int(input_index)
    if increase:
        input_index +=1
        return str(input_index).encode()
    input_index -=1
    return str(input_index).encode()

def display_image(image_path):
    return Image.open(image_path)

def start_func(user_dropdown):
    global db
    # global index
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

    return Image.open(image_file_path), class_name, anno_text, index.decode()


def anno_func(anno, index):
    global db
    # global index
    global etrieved_data_dict
    global index_db
    global user_name
    if index is None:
        raise gr.Error("사용자를 선택해 주세요!")
    etrieved_data_dict['annotation'] = anno
    dict_bytes = pickle.dumps(etrieved_data_dict)
    db[index.encode()] = dict_bytes
    db.sync()

    index = index_changer(index, increase = True)
    data_bytes = db[index]
    etrieved_data_dict = pickle.loads(data_bytes)
    image_file_path = etrieved_data_dict['file_path']
    class_name = etrieved_data_dict['class_name']
    anno_text = etrieved_data_dict['annotation']
    index_db[user_name.encode()] = index
    index_db.sync()

    return Image.open(image_file_path), class_name, anno_text, index.decode()

def move_func(status, index):
    # global index

    if status == 'prev':
        if index is None:
            raise gr.Error("사용자를 선택해 주세요!")
        index = index_changer(index, increase = False)
        data_bytes = db[index]
        etrieved_data_dict = pickle.loads(data_bytes)
        image_file_path = etrieved_data_dict['file_path']
        class_name = etrieved_data_dict['class_name']
        anno_text = etrieved_data_dict['annotation']

        return Image.open(image_file_path), class_name, anno_text, index.decode()
    
    if status == 'next':
        if index is None:
            raise gr.Error("사용자를 선택해 주세요!")
        index = index_changer(index, increase = True)
        data_bytes = db[index]
        etrieved_data_dict = pickle.loads(data_bytes)
        image_file_path = etrieved_data_dict['file_path']
        class_name = etrieved_data_dict['class_name']
        anno_text = etrieved_data_dict['annotation']

        return Image.open(image_file_path), class_name, anno_text, index.decode()

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    db = gr.State()
    index_text =gr.State()
    etrieved_data_dict =gr.State()
    index_db = gr.State()
    user_name  = gr.State()

    gr.Markdown("Huray Label Studio")
    with gr.Row():
        with gr.Row():
            user_dropdown = gr.Dropdown(["test", "test2", "test3"], label = "user")
            work_check = gr.Checkbox(label="작업하지 않은 라벨만 보기"),
        start_button = gr.Button('start')
    with gr.Row():
        prev_button = gr.Button('prev')
        class_text = gr.Textbox(value = 'class name here!!', container = False, interactive = False, max_lines = 1)
        index_text = gr.Textbox(value = 'index', container = False, interactive = False, max_lines = 1)
        next_button = gr.Button('next')
    with gr.Row():
        image_output = gr.Image(height = 600, interactive = False)
    with gr.Row():
        true_button = gr.Button('True', variant="primary")
        false_button = gr.Button('False')
    with gr.Row():
        skip_button = gr.Button('Skip')
    with gr.Row():
        anno_text = gr.Textbox(value = 'annotation here!!', container = False, interactive = False, max_lines = 1)

    true_anno = gr.Textbox(value = 'True', visible = False, interactive = False, max_lines = 1)
    false_anno = gr.Textbox(value = 'False', visible = False, interactive = False, max_lines = 1)
    skip_anno = gr.Textbox(value = 'Skip', visible = False, interactive = False, max_lines = 1)

    prev_text = gr.Textbox(value = 'prev', visible =False, interactive = False, max_lines = 1)
    next_text = gr.Textbox(value = 'next', visible =False, interactive = False, max_lines = 1)

    start_button.click(start_func, inputs = [user_dropdown], outputs = [image_output, class_text, anno_text, index_text])
    true_button.click(anno_func, inputs = [true_anno, index_text], outputs = [image_output, class_text, anno_text, index_text])
    false_button.click(anno_func, inputs = [false_anno, index_text], outputs = [image_output, class_text, anno_text, index_text])
    skip_button.click(anno_func, inputs = [skip_anno, index_text], outputs = [image_output, class_text, anno_text, index_text])
    prev_button.click(move_func, inputs = [prev_text, index_text], outputs=[image_output, class_text, anno_text, index_text])
    next_button.click(move_func, inputs = [next_text, index_text], outputs=[image_output, class_text, anno_text, index_text])

demo.launch(ssl_verify=False, share=True, server_name="0.0.0.0")