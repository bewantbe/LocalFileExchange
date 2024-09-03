# script for uploading or downloading files

# dev run:
# gradio gp.py

import os
import shutil
import time
import re
import socket
import gradio as gr

# to avoid error
# ValueError: When localhost is not accessible, a shareable link must be created. Please set share=True or check your proxy settings to allow access to localhost.
os.environ['no_proxy'] = 'localhost,127.0.0.1,::1'

def is_valid_windows_filename(filename):
  """
  Checks if a filename is valid for Windows.

  Args:
    filename: The filename to check.

  Returns:
    True if the filename is valid, False otherwise.
  """

  # Check if the filename is empty.
  if not filename:
    return False

  # Check if the filename contains any invalid characters.
  invalid_chars = r'\\/:\*\?"<>\|'
  if re.search(invalid_chars, filename):
    return False

  # Check if the filename is too long.
  max_filename_length = 255
  if len(filename) > max_filename_length:
    return False

  # The filename is valid.
  return True

# Define the function to save user input
def save_text(user_input, save_name):
    # check if the file name is grammatically correct
    if not is_valid_windows_filename(save_name):
        return f'"{save_name}": Invalid file name. Please enter a valid file name.'
    fname = time.strftime(save_name)
    fname = fname.replace(':', '')
    with open(fname, "a") as f:
        f.write(user_input + "\n")
    return f'Text appended to "{fname}".'

# Define the function to handle file upload
def handle_upload(fileobj):
    path = os.path.basename(fileobj)
    shutil.copyfile(fileobj.name, path)
    return f'"{path}" uploaded successfully.'

def process_view_list(file_list):
    if not file_list:
        file_list = '.'
    img_list = []
    for f in file_list:
        # if f is a dir, list all the file ends with jpg or png directly under it
        if os.path.isdir(f):
            for f2 in os.listdir(f):
                p = os.path.join(f, f2)
                if os.path.isfile(p) and not os.path.isdir(p) and (                             \
                   f2.endswith('.jpg') or f2.endswith('.png') ):
                    img_list.append((p, f2))
        else:
            p = f
            f2 = f
            if os.path.isfile(p) and not os.path.isdir(p) and (                             \
                f2.endswith('.jpg') or f2.endswith('.png') ):
                img_list.append((p, f2))
    return [img_list, gr.Tabs(selected='view_gallery')]

def process_view_video(file_list):
    if not file_list:
        file_list = '.'
    for f in file_list:
        if os.path.isfile(f) and f.endswith('.mp4'):
            print('==>> f:', f)
            return [f, gr.Tabs(selected='view_video')]
    return [None, gr.Tabs(selected='browse')]

def get_select_img(evt: gr.SelectData):
    #print(f"==>> evt.selected: {evt.selected}") # True
    #print(f"==>> evt._data: {evt._data}") # {'index': 1, 'value': None}
    #print(f"You selected {evt.value} at {evt.index} from {evt.target}") # You selected None at 1 from gallery
    #return [evt.value, evt.value['image']['path']]
    return evt.value['image']['path']

def get_local_ip():
    # https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


# Create the Gradio interface
with gr.Blocks(theme=gr.themes.Default(
                    spacing_size=gr.themes.sizes.spacing_md,
                    radius_size=gr.themes.sizes.radius_md,
                    text_size=gr.themes.sizes.text_lg)) as demo:
    
    with gr.Tabs() as gr_tabs:
        with gr.Tab('Browse', id='browse'):
            explorer = gr.FileExplorer(label="Browse files")
            with gr.Row():
                root_dir_input = gr.Textbox(label="Root directory", value='.')
                change_root_button = gr.Button("Change root")
                change_root_button.click(lambda i: gr.FileExplorer(root_dir=i), inputs=root_dir_input, outputs=explorer)
            with gr.Row():
                selected_files = gr.Textbox(label="Selected file", interactive=False)
                view_button = gr.Button("View in gallery")
                view_video_button = gr.Button("View video")
                view_text_button = gr.Button("View text")
                #update_ex_button = gr.Button("Update")
                #update_ex_button.click(lambda i: gr.FileExplorer(root_dir='.'), outputs=explorer)
            show_text_output = gr.Textbox(label="Text content", interactive=False, show_copy_button=True)
            gr.Markdown('---')
            explorer.change(lambda f_list: str(f_list), explorer, selected_files)
            view_text_button.click(lambda f: open(f[0]).read(), inputs=explorer, outputs=show_text_output)

        with gr.Tab('Upload', id='upload'):
            with gr.Row():
                text_input = gr.Textbox(
                label="Enter text",
                lines=7,
                placeholder="Enter text here",
                scale=2,
                min_width=300)
                with gr.Column(scale=1, min_width=200):
                    save_name = gr.Textbox(label="File name", lines=1, value='text_%F_%T.txt')
                    save_output = gr.Textbox(label="Save status", interactive=False)
                    save_button = gr.Button("Save text")
                    save_button.click(save_text, inputs=[text_input, save_name], outputs=save_output)
            gr.Markdown("---")
            with gr.Row():
                upload_status = gr.Textbox(label="Upload status", interactive=False)
                upload_button = gr.UploadButton("Upload a file", file_count="single")
                upload_button.upload(handle_upload, inputs=upload_button, outputs=upload_status)

        with gr.Tab('View gallery', id='view_gallery') as view_gallery_tab:
            img_gallery = gr.Gallery(object_fit='contain', show_download_button=False)
            view_button.click(process_view_list, inputs=explorer, outputs=[img_gallery, gr_tabs])

            gr.Markdown("---")
            #selected_img = gr.Textbox(label="Selected image", interactive=False)
            show_img = gr.Image(show_download_button=False)
            #img_gallery.select(get_select_img, outputs=[selected_img, show_img])
            img_gallery.select(get_select_img, outputs=show_img)

        with gr.Tab('View video', id='view_video'):
            show_video = gr.Video(show_download_button=False)
            view_video_button.click(process_view_video, inputs=explorer, outputs=[show_video, gr_tabs])

ip_port = 7860

ip_str = get_local_ip()
print('Server address: ', ip_str, ':', ip_port, sep='')

# Launch the app
demo.launch(server_name="0.0.0.0", server_port=ip_port)
#demo.launch()
