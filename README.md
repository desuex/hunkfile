# **THIS TOOL IS NO LONGER MAINTAINED**
Please use this repository:
https://github.com/desuex/torus-tools
# hunkfile
Torus Games data format packer-unpacker. Tested on Monster High NGIS PC game. Make sure you are using correct endianness (ps3 hunkfiles are big endian, pc are little). 

Tested on archlinux, python 3.11

# How to use
- Install python dependencies (requirements.txt), use venv whenever possible
- Place your hnk files into `assets/hnk` directory. The script is expecting to have `Localisation_en_US.hnk` and `Global_en_US.hnk` to be there. 
- Run `scripts/hnk2xls.py`. 
- Check xls files inside `assets/xls` directory
- use any spreadsheet software to edit the files
- [NOT WORKING YET] Run `scripts/xls2hnk.py` to update hnk files with your fixed localization 
- Place hnk files back to HUNKFILE directory, reassemble the ROM file if needed (consoles only)

