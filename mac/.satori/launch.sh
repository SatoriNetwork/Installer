#!/bin/bash
# This script launches the Python script in a new Terminal window

# Path to the Python script inside the app bundle
PYTHON_SCRIPT_PATH="$(dirname "$0")/Satori"

# Command to open the browser
#open "http://127.0.0.1:24601"

# HTML content
HTML_CONTENT='<!DOCTYPE html><html><head><title>Starting Satori Neuron</title><script type="text/javascript">setTimeout(function(){window.location.href = "http://127.0.0.1:24601";}, 1000 * 60);</script></head><body><p>Please wait a few minutes while the Satori Neuron boots up. <a href="http://127.0.0.1:24601">Refresh</a></p></body></html>'

# URL encode the HTML content
#URL_ENCODED_HTML=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''$HTML_CONTENT'''))")
# Create a data URL
#DATA_URL="data:text/html,$URL_ENCODED_HTML"
# Command to open the data URL in the browser
#open "$DATA_URL"

# Create a temporary file
TEMP_HTML_FILE=$(mktemp /tmp/temp_html.Satori.html)

# Write the HTML content to the temporary file
echo "$HTML_CONTENT" > "$TEMP_HTML_FILE"

# Command to open the temporary HTML file in the browser
open "$TEMP_HTML_FILE"


# Command to open Terminal and run the Python script
osascript -e "tell application \"Terminal\" to do script \"$PYTHON_SCRIPT_PATH\""



