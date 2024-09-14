```bash
#!/bin/bash

# check for the OS type to determine commands to use
os_type() {
    case "$(uname -s)" in
        Darwin)
            os_type="macos"
        ;;
        Linux)
            os_type="linux"
        ;;
        CYGWIN*|MINGW32*|MSYS*|MINGW*)
            os_type="windows"
        ;;
        *)
            echo "Unsupported OS type, exiting"
            exit 1
        ;;
    esac
}

# function to start spotify
start_spotify() {
    if [[ $os_type == "macos" ]]; then
        osascript -e 'tell application "Spotify" to activate'
    elif [[ $os_type == "linux" ]]; then
        spotify &> /dev/null &
    elif [[ $os_type == "windows" ]]; then
        wsl.exe powershell -c "Start-Process -NoNewWindow spotify"
    fi
}

# function to play music
play_music() {
    if [[ $os_type == "macos" ]]; then
        osascript -e 'tell application "Spotify" to play'
    elif [[ $os_type == "linux" ]]; then
        dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.PlayPause
    elif [[ $os_type == "windows" ]]; then
        echo "Play not supported in Windows"
    fi
}

# function to pause music
pause_music() {
    if [[ $os_type == "macos" ]]; then
        osascript -e 'tell application "Spotify" to pause'
    elif [[ $os_type == "linux" ]]; then
        dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.PlayPause
    elif [[ $os_type == "windows" ]]; then
        echo "Pause not supported in Windows"
    fi
}

# function to stop music
stop_music() {
    if [[ $os_type == "macos" ]]; then
        osascript -e 'tell application "Spotify" to pause'
    elif [[ $os_type == "linux" ]]; then
        dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.Stop
    elif [[ $os_type == "windows" ]]; then
        echo "stop not supported in Windows"
    fi
}

control_spotify() {
    ps aux | grep -i "[s]potify" > /dev/null

    if [[ $? -eq 0 ]]; then
        echo "Spotify is running."
    else
        echo "Spotify isn't running."
        echo -n "Would you like to open it? (y/n): "
        read -r answer

        if [[ ${answer,,} = "y" ]]; then
            start_spotify
        fi
    fi

    while true; do
        echo "Controls:"
        echo -e "1. Play\n2. Pause\n3. Stop\n4. Exit"
        echo -n "Choose a number: "
        read -r answer

        case $answer in
            1)
                play_music
                ;;
            2)
                pause_music
                ;;
            3)
                stop_music
                ;;
            4)
                echo "Exiting..."
                break
                ;;
            *)
                echo "Invalid option, try again..."
        esac
    done
}

# Set OS type
os_type

# Start spotify control loop
control_spotify
```