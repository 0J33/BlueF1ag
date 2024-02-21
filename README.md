# Blue F1ag

Blue F1ag provides F1 data through graphs for fans to analyze.

[Add Blue F1ag to your discord server](https://discord.com/oauth2/authorize?client_id=892359806898303036&permissions=534723947584&scope=bot)  
[Blue F1ag Support Server](https://discord.com/invite/uXY5Va4Jbb)  
[Blue F1ag ToS](https://bluef1ag.ojee.net/tos)  
[Blue F1ag Privacy Policy](https://bluef1ag.ojee.net/priv)  

# Requirements

Run `pip install -r requirements.txt` to install dependencies.

# Running

- To enable cache make a folder named `doc_cache` in the main directory.
- To run the server, run `main.py`.
- To generate graphs you can either, send a `POST` request to `/` with the proper inputs.
- Alternatively, you can use the functions directly in the `funcs.py` / `funcs_cache.py`.
- To update data, send an empty `POST` request to `/update`.
- Alternatively, you can update data using the functions in the `update.py`.
- All the plotting functions are in `funcs.py` / `funcs_cache.py`.
- `funcs.py` uses aws for storage rather than the built in cache in the fasft1 library.
- `funcs_cahce.py` uses the built in cache in the fastf1 library
- `aws_api.py` contains functions for using aws s3.

# Data

Data is from the [FastF1](https://github.com/theOehrly/Fast-F1) api.
