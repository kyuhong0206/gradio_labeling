import bsddb3.db as bdb
import gradio as gr
import pandas as pd
import pickle
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

DBPATH = '/home/ai04/workspace/gradio_labeling/data/'
CFGHEIGHT = 600

font_path = "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf"  
font_prop = font_manager.FontProperties(fname=font_path)
rc('font', family=font_prop.get_name())


def start_func(user_dropdown):
    data_list = []
    db = bdb.DB()
    db_path = f'{DBPATH}{user_dropdown}.db'
    db.open(db_path, None, bdb.DB_HASH, bdb.DB_CREATE)
    for key in db.keys():
        data_bytes = db.get(key)
        data_list.append(pickle.loads(data_bytes))
    df = pd.DataFrame(data_list)
    df['annotation'] = df['annotation'].apply(lambda x: 'Empty' if x == None else x)
    count_df = df[df['annotation'].notnull()]['annotation'].value_counts()
    total = sum(count_df.values)
    percentages = [(count / total) * 100 for count in count_df]
    legend_labels = [f'{label}: {percentage:.1f}%' for label, percentage in zip(count_df.index, percentages)]
    fig, ax = plt.subplots()
    ax.pie(count_df, startangle=140, wedgeprops=dict(width=0.3))
    ax.legend(legend_labels, title="Annotations", loc="best")
    ax.set_title(f'{user_dropdown} Annotation Distribution')

    return fig

def cate_annotation_chart(user_dropdown, class_name):
    data_list = []
    db = bdb.DB()
    db_path = f'{DBPATH}{user_dropdown}.db'
    db.open(db_path, None, bdb.DB_HASH, bdb.DB_CREATE)
    for key in db.keys():
        data_bytes = db.get(key)
        data_list.append(pickle.loads(data_bytes))
    df = pd.DataFrame(data_list)
    df['annotation'] = df['annotation'].apply(lambda x: 'Empty' if x == None else x)
    filtered_data = [item for item in data_list if item['class_name'] == class_name]
    annotations = [item['annotation'] for item in filtered_data if item['annotation']]
    annotation_counts = {annotation: annotations.count(annotation) for annotation in set(annotations)}
    
    if annotation_counts:
        fig, ax = plt.subplots()
        ax.pie(annotation_counts.values(), labels=annotation_counts.keys(), autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.3))
        ax.set_title(f'Annotations for class "{class_name}"')

        return fig
    else:
        gr.Warning('no class')


with gr.Blocks(theme = gr.themes.Soft()) as demo:
    db = gr.State()
    index_text = gr.State()
    index_db = gr.State()
    user_name  = gr.State()
    image_output = gr.State()
    user_dropdown = gr.State()
    work_check = gr.State()
    item_length = gr.State()
    gr.Markdown("""# Huray Label Analysis""")
    with gr.Row():
        with gr.Column(scale=10):
            with gr.Row():
                plot_output = gr.Plot()
        with gr.Column(scale=2):
            
            with gr.Row():
                user_dropdown = gr.Dropdown(["test", "test2", "test3"], label = "user")
            with gr.Row():
                start_button = gr.Button('전체 조회', variant="primary")
                class_text = gr.Textbox(label = 'class', max_lines = 1)
                index_button = gr.Button('클래스 조회')
                true_count_text = gr.Textbox(label = 'ture count', interactive = False, max_lines = 1)
                false_count_text = gr.Textbox(label = 'false count', interactive = False, max_lines = 1)

                skip_count_text = gr.Textbox(label = 'skip count', interactive = False, max_lines = 1)
                none_count_text = gr.Textbox(label = 'none count', interactive = False, max_lines = 1)

    true_anno = gr.Textbox(value = 'True', visible = False, interactive = False, max_lines = 1)
    false_anno = gr.Textbox(value = 'False', visible = False, interactive = False, max_lines = 1)
    skip_anno = gr.Textbox(value = 'Skip', visible = False, interactive = False, max_lines = 1)

    prev_text = gr.Textbox(value = 'prev', visible =False, interactive = False, max_lines = 1)
    next_text = gr.Textbox(value = 'next', visible =False, interactive = False, max_lines = 1)
    move_text = gr.Textbox(value = 'move', visible =False, interactive = False, max_lines = 1)
    item_length = gr.Textbox(value = 'item_length', visible =False, interactive = False, max_lines = 1)

    start_button.click(start_func, inputs = [user_dropdown], outputs = [plot_output])
    index_button.click(cate_annotation_chart, inputs = [user_dropdown, class_text], outputs = [plot_output])

demo.launch(ssl_verify=False, share=True, server_name="0.0.0.0")