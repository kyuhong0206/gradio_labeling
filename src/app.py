import bsddb3.db as bdb
import gradio as gr
import pickle
from PIL import Image as PILIMAGE

DBPATH = '/home/ai04/workspace/gradio_labeling/data/'
CFGHEIGHT = 600


def get_db_connection(db_path):
    db = bdb.DB()
    db.open(db_path, None, bdb.DB_HASH, bdb.DB_CREATE)

    return db

def get_index_db_conncection(index_db_path):
    index_db = bdb.DB()
    index_db.open(index_db_path, None, bdb.DB_HASH, bdb.DB_CREATE)

    return index_db

def get_last_index(user_name):
    index_db_path = f"{DBPATH}user_index.db"
    index_db = get_index_db_conncection(index_db_path)
    index = int(index_db.get(user_name.encode()).decode())
    index_db.close()

    return index

def get_image_data(user_name, index, start = False):
    db_path = f"{DBPATH}{user_name}.db"
    db = get_db_connection(db_path)
    data_bytes = db.get(str(index).encode())
    retrieved_data_dict = pickle.loads(data_bytes)
    if start:
        item_length = len(db.keys())    
        db.close()
        return retrieved_data_dict, item_length
    db.close()

    return retrieved_data_dict

def index_changer(index, increase = True):
    index = int(index)
    if increase:
        index += 1
        return index
    index -= 1
    return index

def filtering_worked_item(user_dropdown, index, retrieved_data_dict, increase = True):
    anno_text = retrieved_data_dict.get('annotation', '')
    while anno_text:
        index = index_changer(index, increase = increase)
        retrieved_data_dict = get_image_data(user_dropdown, index)
        anno_text = retrieved_data_dict.get('annotation', '')

    return index, retrieved_data_dict
    
def put_anno_data_to_db(user_name, index, anno):
    db_path = f"{DBPATH}{user_name}.db"
    index_db_path = f"{DBPATH}user_index.db"
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

def display_image(image_path):
    #FIXME ratio resize doesn't work!!
    img = PILIMAGE.open(image_path)
    orign_width, orign_height = img.size
    ratio = CFGHEIGHT / orign_height
    resize_width = int(orign_width * ratio)
    new_img = img.resize((500, 500), PILIMAGE.Resampling.LANCZOS)

    return new_img

def start_func(user_dropdown, work_check):
    if work_check:
        index = 0
    else:
        index = get_last_index(user_dropdown)
    retrieved_data_dict, item_length = get_image_data(user_dropdown, index, start = True)
    if work_check:
        index, retrieved_data_dict = filtering_worked_item(user_dropdown, index, retrieved_data_dict)
    image_file_path = retrieved_data_dict['file_path']
    class_name = retrieved_data_dict['class_name']
    anno_text = retrieved_data_dict.get('annotation', '')

    return display_image(image_file_path), class_name, anno_text, index, item_length

def anno_func(user_dropdown, anno, index, work_check):
    if index is None:
        raise gr.Error("사용자를 선택해 주세요!")
    index = put_anno_data_to_db(user_dropdown, index, anno)
    retrieved_data_dict = get_image_data(user_dropdown, index)
    if work_check:
        index, retrieved_data_dict = filtering_worked_item(user_dropdown, index, retrieved_data_dict)
    image_file_path = retrieved_data_dict['file_path']
    class_name = retrieved_data_dict['class_name']
    anno_text = retrieved_data_dict.get('annotation', '')

    return display_image(image_file_path), class_name, anno_text, index

def move_func(user_dropdown, status, index, work_check, item_length):
    if status == 'prev':
        if int(index) == 0:
            raise gr.Error('첫번째 데이터입니다.')
        else:
            index = index_changer(index, increase = False)
        retrieved_data_dict = get_image_data(user_dropdown, index)
        if work_check:
            index, retrieved_data_dict = filtering_worked_item(user_dropdown, index, retrieved_data_dict, increase = False)
        image_file_path = retrieved_data_dict['file_path']
        class_name = retrieved_data_dict['class_name']
        anno_text = retrieved_data_dict.get('annotation', '')
        
        return display_image(image_file_path), class_name, anno_text, index
    
    if status == 'next':
        if int(index) > int(item_length):
            raise gr.Error('마지막 데이터입니다.')
        index = index_changer(index, increase = True)
        retrieved_data_dict = get_image_data(user_dropdown, index)
        if work_check:
            index, retrieved_data_dict = filtering_worked_item(user_dropdown, index, retrieved_data_dict)
        image_file_path = retrieved_data_dict['file_path']
        class_name = retrieved_data_dict['class_name']
        anno_text = retrieved_data_dict.get('annotation', '')

        return display_image(image_file_path), class_name, anno_text, index
    
    if status == 'move':
        if int(index) > int(item_length):
            raise gr.Error('마지막 데이터입니다.')
        retrieved_data_dict = get_image_data(user_dropdown, index)
        if work_check:
            index, retrieved_data_dict = filtering_worked_item(user_dropdown, index, retrieved_data_dict)
        image_file_path = retrieved_data_dict['file_path']
        class_name = retrieved_data_dict['class_name']
        anno_text = retrieved_data_dict.get('annotation', '')

        return display_image(image_file_path), class_name, anno_text, index

with gr.Blocks(theme = gr.themes.Soft()) as demo:
    db = gr.State()
    index_text = gr.State()
    index_db = gr.State()
    user_name  = gr.State()
    image_output = gr.State()
    user_dropdown = gr.State()
    work_check = gr.State()
    item_length = gr.State()
    with gr.Row():
        with gr.Column(scale=10):
            with gr.Row():
                image_output = gr.Image(interactive = False, container = False)
            with gr.Row():
                true_button = gr.Button('True', variant="primary")
                false_button = gr.Button('False')
            with gr.Row():
                skip_button = gr.Button('Unkown')
        with gr.Column(scale=2):
            gr.Markdown("""# Huray Label Studio""")
            with gr.Row():
                user_dropdown = gr.Dropdown(["test", "test2", "test3"], label = "user")
                work_check = gr.Checkbox(label="미작업 라벨만 보기")
            with gr.Row():
                start_button = gr.Button('start', variant="primary")
                index_text = gr.Textbox(label = 'index', max_lines = 1)
                index_button = gr.Button('move')
                class_text = gr.Textbox(label = 'class name',  interactive = False, max_lines = 1)
                anno_text = gr.Textbox(label = 'annotation', interactive = False, max_lines = 1)
                prev_button = gr.Button('prev')
                next_button = gr.Button('next')
    true_anno = gr.Textbox(value = 'True', visible = False, interactive = False, max_lines = 1)
    false_anno = gr.Textbox(value = 'False', visible = False, interactive = False, max_lines = 1)
    skip_anno = gr.Textbox(value = 'Skip', visible = False, interactive = False, max_lines = 1)

    prev_text = gr.Textbox(value = 'prev', visible =False, interactive = False, max_lines = 1)
    next_text = gr.Textbox(value = 'next', visible =False, interactive = False, max_lines = 1)
    move_text = gr.Textbox(value = 'move', visible =False, interactive = False, max_lines = 1)
    item_length = gr.Textbox(value = 'item_length', visible =False, interactive = False, max_lines = 1)

    start_button.click(start_func, inputs = [user_dropdown, work_check], outputs = [image_output, class_text, anno_text, index_text, item_length])
    true_button.click(anno_func, inputs = [user_dropdown, true_anno, index_text, work_check], outputs = [image_output, class_text, anno_text, index_text])
    false_button.click(anno_func, inputs = [user_dropdown, false_anno, index_text, work_check], outputs = [image_output, class_text, anno_text, index_text])
    skip_button.click(anno_func, inputs = [user_dropdown, skip_anno, index_text, work_check], outputs = [image_output, class_text, anno_text, index_text])
    prev_button.click(move_func, inputs = [user_dropdown, prev_text, index_text, work_check, item_length], outputs=[image_output, class_text, anno_text, index_text])
    next_button.click(move_func, inputs = [user_dropdown, next_text, index_text, work_check, item_length], outputs=[image_output, class_text, anno_text, index_text])
    index_button.click(move_func, inputs = [user_dropdown, move_text, index_text, work_check, item_length], outputs=[image_output, class_text, anno_text, index_text])

demo.launch(ssl_verify=False, share=True, server_name="0.0.0.0")