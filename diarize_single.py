import sys
from pyannote.audio import Pipeline
import sys
from tqdm import tqdm

access_token = "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"
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization",
                                    use_auth_token=access_token)

fname = sys.argv[1]
print('Doing file', fname)
diarization = pipeline(fname)
out_fname = fname.replace('.wav', '.rttm').replace('seenunseen_wav', 'seenunseen_rttm_raw')
with open(out_fname, "w") as rttm:
    diarization.write_rttm(rttm)
 