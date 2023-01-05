source /opt/conda/etc/profile.d/conda.sh
conda activate ./whisper_env
whisper --language en --model large --beam_size 3 --best_of 3 -o data/seenunseen_transcripts_raw/ $1 