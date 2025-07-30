# Third-Party Software Notices and Information

This project incorporates code from the following open-source software:

## 1. Stable Diffusion Prompt Reader

* **Original Author:** receyuki
* **Project Repository:** [https://github.com/receyuki/stable-diffusion-prompt-reader](https://github.com/receyuki/stable-diffusion-prompt-reader)
* **Version Vendored:** (Specify if known, e.g., v1.3.5, or commit hash a1b2c3d)
* **Original License:** MIT License
* The NovelAI metadata parsing logic within the vendored stable-diffusion-prompt-reader code aligns with the specifications published by NovelAI regarding their image metadata formats (see https://github.com/NovelAI/novelai-image-metadata).
* **Modifications:** The code vendored from Stable Diffusion Prompt Reader has been adapted and modified for integration into Dataset-Tools. These modifications primarily reside within the `dataset_tools/vendored_sdpr/` directory.
Directory Structure of files
`dataset_tools/
├── __init__.py
├── access_disk.py
├── correct_types.py
├── logger.py
├── main.py
├── metadata_parser.py
├── model_parsers/
│   ├── __init__.py
│   ├── base_model_parser.py
│   ├── gguf_parser.py
│   └── safetensors_parser.py
├── model_tool.py
├── ui.py
├── ui_old.py
├── vendored_sdpr/
│   ├── __init__.py               # Package marker for vendored_sdpr
│   ├── constants.py            # Constants used by vendored code (e.g., PARAMETER_PLACEHOLDER)
│   ├── image_data_reader.py    # Vendored Image Reader (Modified)
│   ├── logger.py               # The simple Logger class vendored from SDPR
│   ├── resources/              # Directory for resources (created for importlib.resources)
│   │   └── __init__.py         # Makes 'resources' a sub-package
│   ├── format/                 # Sub-package for different metadata format parsers
│   │   ├── __init__.py         # Exports all format classes
│   │   ├── a1111.py
│   │   ├── base_format.py
│   │   ├── civitai.py          # CivitAI Mojibake Parsing
│   │   ├── comfyui.py
│   │   ├── drawthings.py
│   │   ├── easydiffusion.py
│   │   ├── fooocus.py
│   │   ├── invokeai.py
│   │   ├── novelai.py
│   │   ├── ruinedfooocus.py    # RuinedFoocus
│   │   ├── swarmui.py
│   │   └── utility.py          # Utility functions for the format parsers
└── widgets.py`

### Original Copyright Notice (from Stable Diffusion Prompt Reader)

MIT License
Copyright (c) 2023 receyuki
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Notices for ComfyUI Workflows & Image Research

### ComfyUI Workflows

99% of the comfyUI workflows do not come with a lisc, and we don't have the URLS FOR MOST OF THEM.
We don't own these, these are ONLY for research into how to traverse these. Please do NOT use these without finding who made them.
Except that one stupid Flux one from TensorARt that loads our own Flux loras.
Go for gold.

### ComfyUI or Other Image Data

Workflow images, or images otherwise kept for testing for now are advanced UI resources. They're not ours, and we do not own them.
Thank you to Quadmoon, Tatersbarn and a few others for actually GIVING US some.
If you or someone else you know MADE an image from this pile of gold - please let us know.
Your efforts are a goldmine of information and give us insight into modern UI/UX for AI generation.
