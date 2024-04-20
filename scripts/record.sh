#!/bin/bash

# Log file path
LOG_FILE="motion_log.txt"
# Variable to track recording status
RECORDING=false
# Variable to track last motion time
LAST_MOTION_TIME=0
# Timeout for no motion (in seconds)
NO_MOTION_TIMEOUT=5

if [ -z "$CUSTOM_USER"]; then
    user="$USER"
else
    user="$CUSTOM_USER"
fi

# Function to start recording and log
start_recording() {
    if [ ! -d "/config/Videos/$user" ]; then
        mkdir "/config/Videos/$user"
        echo "Directory '/config/Videos/$user' created."
    else
        echo "Directory '/config/$user' already exists."
    fi
    local filename="/config/Videos/${user}/out_$(date +%Y%m%d_%H%M%S).avi"
    echo "$(date +"%Y-%m-%d %H:%M:%S"): Recording started" >> "$LOG_FILE"
    ffmpeg -f x11grab -y -r 30 -s 1280x814 -i $DISPLAY -vcodec libx264 "$filename" &
    RECORDING=true
}

# Function to stop recording and log
stop_recording() {
    echo "$(date +"%Y-%m-%d %H:%M:%S"): Recording stopped" >> "$LOG_FILE"
    pkill ffmpeg
    RECORDING=false
}

# Main loop
while true; do
    # Check if mouse motion is detected
    current_pos=$(xdotool getmouselocation)
    sleep 0.1
    new_pos=$(xdotool getmouselocation)
   if [ "$current_pos" != "$new_pos" ]; then
        # Get the current time
        CURRENT_MOTION_TIME=$(date +%s)
        # If last motion time is not set or if the current motion time is different from the last motion time, start recording
        if [ "$RECORDING" = false ] && [ "$CURRENT_MOTION_TIME" -ne "$LAST_MOTION_TIME" ]; then
            start_recording
        fi
        # Update last motion time
        LAST_MOTION_TIME=$CURRENT_MOTION_TIME
    else
        echo "running else statement" >> "$LOG_FILE"
        if [ "$RECORDING" = true ]; then
        # If currently recording and no motion for NO_MOTION_TIMEOUT seconds, stop recording
            if [ $(($(date +%s) - LAST_MOTION_TIME)) -ge $NO_MOTION_TIMEOUT ]; then
                stop_recording
            fi
        fi
    fi
    # Sleep for 1 second before checking again
    sleep 1
done
