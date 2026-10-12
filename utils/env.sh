export TMNF_ROOT="$HOME/tmnf"
export PATH="$TMNF_ROOT/wine-11.0-amd64-wow64/bin:$PATH"
export WINE="$TMNF_ROOT/wine-11.0-amd64-wow64/bin/wine"
mkdir -p "$TMNF_ROOT/prefix"
export WINEPREFIX="$TMNF_ROOT/prefix"
export WINEDEBUG=-all
