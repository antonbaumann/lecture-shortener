### usage:
```bash
lecture_shortener.py [-h] -i INFILE -o OUTFILE
                            [--speed-sound SPEED_SOUND]
                            [--speed-silence SPEED_SILENCE]
                            [--silence-threshold SILENCE_THRESHOLD]

Speed up lectures

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE             input file path
  -o OUTFILE            output file path
  --speed-sound SPEED_SOUND
                        general video speed
  --speed-silence SPEED_SILENCE
                        video speed during silence
  --silence-threshold SILENCE_THRESHOLD
                        section will be labeled as `silent` if silence is
                        longer than `silence_threshold` in seconds
```
