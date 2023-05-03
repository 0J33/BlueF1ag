# Blue F1ag
Blue F1ag is a Discord bot that provides F1 data through graphs for fans to analyze.  
[Add Blue F1ag to your discord server](https://ojee.xyz/bluef1ag)  
[Blue F1ag Support Server](https://ojee.xyz/bluef1ag-support)  
[Blue F1ag on top.gg](https://ojee.xyz/bluef1ag-top.gg)  
[Blue F1ag ToS](https://ojee.xyz/bluef1ag-tos)  
[Blue F1ag Privacy Policy](https://ojee.xyz/bluef1ag-priv)  

# Requirements
Run `pip install -r requirements.txt` to install dependencies.

# Data
Data is from the [FastF1](https://github.com/theOehrly/Fast-F1) api.

# Usage

### Running the bot ###
- Make `doc_cache`, `output`, `logs` folders in the main directory.
- Inside the `logs` folder make a `silent.txt` file .
- Make an `env.py` file and inside write: `TOKEN = 'YOURTOKEN'`. Replace `YOURTOKEN` with the token of your bot.
- Run the bot using `main.py`.

### Other ###
- You can edit flask server using `keep_alive.py`.
- All functions are in `funcs.py`.
- You can update drivers/constructors/battles data using `update.py`.
- The `data` folder contains all and current standings and qualifying battles.
