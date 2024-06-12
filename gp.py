# script for uploading or downloading files

# dev run:
# gradio gp.py

import os
import shutil
import time
import re
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
                if os.path.isfile(p) and (                             \
                   f2.endswith('.jpg') or f2.endswith('.png') ):
                    img_list.append((p, f2))
        else:
            img_list.append((f,f))
    return img_list

# Create the Gradio interface
with gr.Blocks(theme=gr.themes.Default(
                    spacing_size=gr.themes.sizes.spacing_md,
                    radius_size=gr.themes.sizes.radius_md,
                    text_size=gr.themes.sizes.text_lg)) as demo:
    # Text box and save button
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

    # File upload button
    with gr.Row():
        file_input = gr.File(label="Upload a file", scale=2)
        with gr.Column(scale=1):
            upload_output = gr.Textbox(label="Upload status", interactive=False)
            upload_button = gr.Button("Save upload")
            upload_button.click(handle_upload, inputs=file_input, outputs=upload_output)

    with gr.Row():
        upload_status = gr.Textbox(label="Upload status", interactive=False)
        upload_button = gr.UploadButton("Upload a file", file_count="single")
        upload_button.upload(handle_upload, inputs=upload_button, outputs=upload_status)

    gr.Markdown("---")

    #gr.FileExplorer(label="Browse files")
    #gr.Files(label="Browse files")
    #download_button = gr.DownloadButton("Download the file")
    
    explorer = gr.FileExplorer(label="Browse files")
    with gr.Row():
        selected_files = gr.Textbox(label="Selected file", interactive=False)
        view_button = gr.Button("View in gallery")
        update_ex_button = gr.Button("Update")
        update_ex_button.click(lambda i: gr.FileExplorer(root_dir='.'), outputs=explorer)
    explorer.change(lambda f_list: str(f_list), explorer, selected_files)

    img_gallery = gr.Gallery()
    view_button.click(process_view_list, inputs=explorer, outputs=img_gallery)

# Launch the app
demo.launch(server_name="0.0.0.0", server_port=7860)
#demo.launch()