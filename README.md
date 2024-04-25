# gradio labeling tools
<img width="1156" alt="스크린샷 2024-02-26 오후 3 16 14" src="https://github.com/kyuhong0206/gradio_labeling/assets/32063217/6c700949-cde3-47f9-821f-eff24917a0af">    
    
1. install libdb
    
    sudo apt-get update    
    sudo apt install libdb-dev    

2. install korean font
       
    sudo apt-get install fonts-nanum*    
    sudo fc-cache -fv    

3. create python env and install requirements
    
4. $gradio app.py


app.py : main page for annotating data    
make_db.py: init db for first work    
admin.py: analysis user task statistics.

DB format
```json
"file_path" : image file path(str)
"class_name": image file class name (str)
"annotation": annotations (str) -> True/False/unknown
"datetime": Recorded date(datetime)
"index": unique index number (int)
"pre_anno": with or without pre-annotation(bool)
```


