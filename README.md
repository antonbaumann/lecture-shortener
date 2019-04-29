### installation:
1. install `ffmpeg` if not already installed
2. clone repository: `git clone https://github.com/antonbaumann/lecture-shortener.git`
3. `cd lecture-shortener`
4. run `pip3 install -r requirements.txt`

### usage:
```bash
python3 lecture_shortener.py [-h] -i INFILE -o OUTFILE
                            [--speed-sound SPEED_SOUND]
                            [--speed-silence SPEED_SILENCE]
                            [--min-silence-len MIN_SILENCE_LEN]
                            [--silence-threshold SILENCE_THRESHOLD]
                            [--step-duration STEP_DURATION]

Speed up lectures

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE             input file path
  -o OUTFILE            output file path
  --speed-sound SPEED_SOUND
                        general video speed
  --speed-silence SPEED_SILENCE
                        video speed during silence
  --min-silence-len MIN_SILENCE_LEN
                        section will be labeled as `silent` if silence is
                        longer than `min-silence-len` in ms
  --silence-threshold SILENCE_THRESHOLD
                        frame is `silent` if volume is smaller than `silence-
                        threshold`
  --step-duration STEP_DURATION
                        check every n milliseconds for silence
```
