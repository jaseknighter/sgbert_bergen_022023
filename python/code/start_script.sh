sudo pkill -f t10.py

#INSTRUCTIONS
#  Remove this code to stop messages from being saved to file:
#     `>> ~/touched/sgbert_bergen_022023/code/bergen_script.log`
#  Use the second line of code that contains `--skipMidiSequence True`
#    for the two Raspberrys that shouldn't auto-sequence notes
#    Note: make sure the first line is commented out when doing this!

cd /home/pi/touched/sgbert_bergen_022023/code/ && python t10.py >> ~/touched/sgbert_bergen_022023/code/bergen_script.log
# cd /home/pi/touched/sgbert_bergen_022023/code/ && python t10.py --skipMidiSequence True >> ~/touched/sgbert_bergen_022023/code/bergen_script.log

