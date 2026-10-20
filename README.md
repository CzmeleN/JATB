# JATB
Just Another Trackmania Bot - a project for Game Botting UWr Class

## Main Goal

- The model can complete all 15 of White difficulty tracks.
- Additional goals consist of receiving timed medals

## Stack

- TMInterface for receiving game info and sending inputs
- Linesight and Yosh's YouTube channel as a reference
- ...

## Ways of working

- TODO

## Progress

- TODO

## Repo Setup

The project uses Poetry 2.x (2.1 or newer) and requires **Python 3.11 or 3.12**.
The virtual environment is created in `./.venv` (see `poetry.toml`) and is not committed.

### Option A: you already have Python 3.11/3.12

```
poetry env use 3.12        # or 3.11, or a full path to the interpreter, e.g. ~/miniconda3/envs/ml/bin/python
poetry install
```

### Option B: you don't have a suitable Python

Install one first, then proceed as in option A. You can do it with conda:
  ```
  conda create -n py312 python=3.12 -y
  poetry env use $(conda run -n py312 which python)
  poetry install
  ```

Check with `poetry env info` (should show Python 3.12 and the `.venv` path).

### Using the environment

- activate the environment with: `eval $(poetry env activate)`
- run the project without activating: `poetry run jatb` (same as `poetry run python -m jatb`; the entry point is `main()` in `jatb/__main__.py`)

## Trackmaina Setup

1. get the software:

    - winetricks from your package manager
    - official trackmania installer https://nadeo-download.cdn.ubi.com/trackmaniaforever/tmnationsforever_setup.exe
    - tagged WINE 11.0 wow64 release https://github.com/Kron4ek/Wine-Builds/releases/download/11.0/wine-11.0-amd64-wow64.tar.xz
    - latest TMLoader https://tomashu.pages.dev/modloader/modloader/TMLoader-latest.zip - I will reupload this zip to have a tagged version
    - dxvk2071 (see below)

2. prepare the game directory, ~/tmnf

    **MAKE SURE TO STAY IN THE SAME SHELL INSTANCE AFTER SOURCING THE ENV**

    - check the downloaded Wine checksum
    ```
    echo "39574efa1132c3ca0d5c77dd2eddbe4a49cca0d6cc2c290ff4924493a1c40314 wine-11.0-amd64-wow64.tar.xz" | sha256sum -c
    ```
    - unpack Wine
    ```
    tar -xvJf wine-11.0-amd64-wow64.tar.xz
    ```
    - load the exports (also creates prefix folder)
    ```
    source JATB/utils/env.sh
    ```
    - check the Wine installation
    ```
    wine --version # should be wine-11.0
    ```
    - create the prefix
    ```
    WINEDLLOVERRIDES="mscoree,mshtml=" wineboot -u
    ```
    - *optional but recommended* remove the documents symlink to not interfere with the steam version's save
    ```
    docs="$WINEPREFIX/drive_c/users/$USER/Documents"
    [ -L "$docs" ] && rm "$docs" && mkdir "$docs"
    ```
    - get our dkvk version
    ```
    winetricks -q dxvk2071
    ```
    - install the game
    ```
    wine tmnationsforever_setup.exe
    # you can now check if there is TmNationForever folder in $WINEPREFIX/drive_c/Program Files (x86)/
    ```
    - open the launcher and setup windowed lowest res fastest (get high fps when running multiple instances)
    ```
    wine "$WINEPREFIX/drive_c/Program Files (x86)/TmNationsForever/TmForeverLauncher.exe"
    ```
    - launch the game and check DXVK
    ```
    cd "$WINEPREFIX/drive_c/Program Files (x86)/TmNationsForever"
    DXVK_HUD=version,fps wine TmForever.exe
    # hud in the top left should show DXVK v2.7.1
    ```

3. prepare TMInterface

    **MAKE SURE TO HAVE THE ENV SOURCED**

    - unzip the modloader
    ```
    unzip TMLoader-1.0.3-win32.zip -d TMLoader
    ```
    - launch the modloader
    ```
    cd TMLoader
    wine TMLoader.exe
    ```

        - in the default profile click the diamond next to the TMInterface
        - then in the right panel download 2.1.0 version and click the diamond next to it
        - now click play icon next to the default profile, the modloader will prompt you to launch TMNF
        - in another terminal source the env and launch TMNF
        - press okay, now launching through modloader should work and you should have TMInterface popup visible in TMNF

    - now we will be launching TMNF like so (it works from any dir!):
    ```
    wine ~/tmnf/TMLoader/TMLoader.exe run TmForever "default"
    # check whether ~ opens the TMInterface terminal
    # you can also check if $WINEPREFIX/drive_c/users/$USER/Documents/TMInterface was created
    ```
    you can get additional confirmation by launching
    ```
    DXVK_HUD=version,fps wine ~/tmnf/TMLoader/TMLoader.exe run TmForever "default"
    ```

    - create the bot profile if you don't wan't to use yours

        - choose stay offline
        - create a new **offline** profile (Account: none), any name that you'd like
        - keep it as the **first** profile in the list (set autologin 1 will target it)

4. link the campaign maps

    - TMNF keeps user data in *Documents/TmForever*, but TMI's *map* command loads paths from *Tracks/Challenges*
    ```
    ln -s "$WINEPREFIX/drive_c/Program Files (x86)/TmNationsForever/GameData/Tracks/Campaigns/Nations/White" "$WINEPREFIX/drive_c/users/$USER/Documents/TmForever/Tracks/Challenges/"
    ```

    - check if you can select a map - in TMI's console (will only work **after** logging in)
    ```
    map White/A01-Race.Challenge.Gbx 
    ```

5. now you're ready to cook

    - add the JATB Link plugin
    ```
    cd "$WINEPREFIX/drive_c/users/$USER/Documents/TMInterface/Plugins/"
    ln -s ~/.../JATB/utils/jatb_link.as jatb_link.as
    # or copy it - you will have to update it by yourself
    ```

    - launch trackmania (should automatically log you in)
    ```
    wine ~/tmnf/TMLoader/TMLoader.exe run TmForever "default" /configstring="set autologin 1; set jatb_port 8450"
    ```

    - check the connection with CommManager (will also load the A01 map)
    ```
    py JATB/jatb/trackmania_interface/test.py
    ```

6. FAQ / Troubleshooting

    Q: there's no lighting in my game
    A: you're probably missing d3dx9 dlls, try running ```winetricks -q d3dx9``` with sourced env
