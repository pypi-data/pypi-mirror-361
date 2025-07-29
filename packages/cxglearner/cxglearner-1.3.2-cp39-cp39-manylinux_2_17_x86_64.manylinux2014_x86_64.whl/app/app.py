import gradio as gr
import pandas as pd
import numpy as np
import tempfile
import random
import json
from pathlib import Path

from cxglearner.parser import Parser
from cxglearner.config import DefaultConfigs, Config
from cxglearner.utils import init_logger
from cxglearner.utils.utils_cxs import convert_slots_to_str

temp_dir = tempfile.gettempdir()
log_dir = Path(temp_dir) / "logs"
log_dir.mkdir(exist_ok=True)
cahce_dir = Path(temp_dir) / "cache"

config = Config(DefaultConfigs.eng)
config.experiment.log_path = log_dir / "eng.log"
logger = init_logger(config)
parser = Parser(config=config, version="1.1", logger=logger, cache_dir=cahce_dir)
examples = [["she should be more polite with the customers."]]
MAX_EXAMPLAR = 10

with open("data/learner_examplar_1.1.json", "r", encoding="utf-8") as fp:
    examplars = json.load(fp)

logger.debug(len(examplars))


def fill_input_box(example):
    return example[0]


def parse_text(text):
    if not text: return gr.Dataframe(),  gr.update(choices=[], value=None), gr.Dataframe()
    encoded_elements = parser.encoder.encode(text, raw=True)
    tokens, upos, xpos = np.array(encoded_elements["lexical"]), np.array(encoded_elements["upos"]["spaCy"]), np.array(
        encoded_elements["xpos"]["spaCy"])
    encoded_elements = np.vstack((tokens, upos, xpos))
    radio_parsed = parser.parse(text)
    radio_parsed = ["{} | {} | {}-{}".format(cxs[0],
                            convert_slots_to_str(parser.cxs_decoder[cxs[0]], parser.encoder, logger), cxs[1] + 1, cxs[2])
                    for cxs in radio_parsed[0]]
    radio_display = gr.Radio(
        label="Constructions", choices=radio_parsed, interactive=True, value=radio_parsed[0]
    )
    if len(radio_parsed) == 0:
        cons_df = pd.DataFrame()
    else:
        cxs = radio_parsed[0]
        index, cxs, ranges = cxs.split("|")
        cxs = cxs.strip()
        if cxs in examplars:
            exams = random.choices(examplars[cxs], k=min(MAX_EXAMPLAR, len(examplars[cxs])))
            cons_df =  pd.DataFrame(exams, columns=[cxs])
        else:
            cons_df = pd.DataFrame()
    return encoded_elements, radio_display, cons_df


def refresh_examplar(option: str):
    print(option)
    index, cxs, ranges = option.split("|")
    cxs = cxs.strip()
    if cxs in examplars:
        exams = random.choices(examplars[cxs], k=min(MAX_EXAMPLAR, len(examplars[cxs])))
        return pd.DataFrame(exams, columns=[cxs])
    return pd.DataFrame()


def clear_text():
    return "", pd.DataFrame(), gr.Radio(label="Constructions", choices=[]), pd.DataFrame()


with gr.Blocks() as demo:
    with gr.Column():
        gr.Markdown("## CxGLearner Parser")
        with gr.Row():
            input_text = gr.Textbox(label="Input Text", placeholder="Enter a sentence here...")

        with gr.Row():
            dataset = gr.Dataset(components=[input_text],
                                 samples=examples,
                                 label="Click an example")
            clear_buttton = gr.Button("Clear")
            parser_button = gr.Button("Parse")

    with gr.Column():
        gr.Markdown("### Results of Encoding and Parsing")
        enc_display = gr.Dataframe()
        cxs_display = gr.Radio(label="Constructions", choices=[])

    with gr.Column():
        gr.Markdown("### Examplars")
        cons_display = gr.Dataframe()

    parser_button.click(fn=parse_text, inputs=[input_text], outputs=[enc_display, cxs_display, cons_display])
    clear_buttton.click(fn=clear_text, inputs=[], outputs=[input_text, enc_display, cxs_display, cons_display])
    dataset.click(fn=fill_input_box, inputs=dataset, outputs=input_text)
    cxs_display.select(refresh_examplar, inputs=[cxs_display], outputs=cons_display)

demo.launch()