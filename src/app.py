import bsddb3.db as bdb
import gradio as gr
import pickle
from PIL import Image

def get_db_connection(db_path):
    db = bdb.DB()
    db.open(db_path, None, bdb.DB_HASH, bdb.DB_CREATE)

    return db

def get_index_db_conncection(index_db_path):
    index_db = bdb.DB()
    index_db.open(index_db_path, None, bdb.DB_HASH, bdb.DB_CREATE)

    return index_db

def get_last_index(user_name):
    index_db_path = "/home/ai04/workspace/gradio_labeling/data/user_index.db"
    index_db = get_index_db_conncection(index_db_path)
    index = int(index_db.get(user_name.encode()).decode())
    index_db.close()

    return index

def get_image_data(user_name, index):
    db_path = f"/home/ai04/workspace/gradio_labeling/data/{user_name}.db"
    db = get_db_connection(db_path)
    data_bytes = db.get(str(index).encode())
    retrieved_data_dict = pickle.loads(data_bytes)
    db.close()

    return retrieved_data_dict

def put_anno_data_to_db(user_name, index, anno):
    db_path = f"/home/ai04/workspace/gradio_labeling/data/{user_name}.db"
    index_db_path = "/home/ai04/workspace/gradio_labeling/data/user_index.db"
    db = get_db_connection(db_path)
    index_db = get_index_db_conncection(index_db_path)
    retrieved_data_dict = get_image_data(user_name, index)
    retrieved_data_dict['annotation'] = anno
    dict_bytes = pickle.dumps(retrieved_data_dict)
    db[str(index).encode()] = dict_bytes
    db.sync()
    index = index_changer(index, increase = True)
    index_db[user_name.encode()] = str(index).encode()
    index_db.sync()
    db.close()
    index_db.close()

    return index

def index_changer(index, increase = True):
    index = int(index)
    if increase:
        index += 1
        return index
    index -= 1
    return index

def display_image(image_path):
    return Image.open(image_path)

def start_func(user_dropdown):
    index = get_last_index(user_dropdown)
    retrieved_data_dict = get_image_data(user_dropdown, index)
    image_file_path = retrieved_data_dict['file_path']
    class_name = retrieved_data_dict['class_name']
    anno_text = retrieved_data_dict.get('annotation', '')

    return Image.open(image_file_path), class_name, anno_text, index

def anno_func(user_dropdown, anno, index):
    if index is None:
        raise gr.Error("사용자를 선택해 주세요!")
    index = put_anno_data_to_db(user_dropdown, index, anno)
    retrieved_data_dict = get_image_data(user_dropdown, index)
    image_file_path = retrieved_data_dict['file_path']
    class_name = retrieved_data_dict['class_name']
    anno_text = retrieved_data_dict.get('annotation', '')

    return Image.open(image_file_path), class_name, anno_text, index

def move_func(user_dropdown, status, index):
    if status == 'prev':
        if index is None:
            raise gr.Error("사용자를 선택해 주세요!")
        index = index_changer(index, increase = False)
        retrieved_data_dict = get_image_data(user_dropdown, index)
        image_file_path = retrieved_data_dict['file_path']
        class_name = retrieved_data_dict['class_name']
        anno_text = retrieved_data_dict['annotation']

        return Image.open(image_file_path), class_name, anno_text, index
    
    if status == 'next':
        if index is None:
            raise gr.Error("사용자를 선택해 주세요!")
        index = index_changer(index, increase = True)
        retrieved_data_dict = get_image_data(user_dropdown, index)
        image_file_path = retrieved_data_dict['file_path']
        class_name = retrieved_data_dict['class_name']
        anno_text = retrieved_data_dict['annotation']

        return Image.open(image_file_path), class_name, anno_text, index

with gr.Blocks(theme = gr.themes.Soft()) as demo:
    db = gr.State()
    index_text = gr.State()
    index_db = gr.State()
    user_name  = gr.State()
    image_output = gr.State()
    user_dropdown = gr.State()
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
    true_button.click(anno_func, inputs = [user_dropdown, true_anno, index_text], outputs = [image_output, class_text, anno_text, index_text])
    false_button.click(anno_func, inputs = [user_dropdown, false_anno, index_text], outputs = [image_output, class_text, anno_text, index_text])
    skip_button.click(anno_func, inputs = [user_dropdown, skip_anno, index_text], outputs = [image_output, class_text, anno_text, index_text])
    prev_button.click(move_func, inputs = [user_dropdown, prev_text, index_text], outputs=[image_output, class_text, anno_text, index_text])
    next_button.click(move_func, inputs = [user_dropdown, next_text, index_text], outputs=[image_output, class_text, anno_text, index_text])

demo.launch(ssl_verify=False, share=True, server_name="0.0.0.0")