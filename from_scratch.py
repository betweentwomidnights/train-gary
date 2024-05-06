import os
import random
import json
from tqdm import tqdm
import librosa
import numpy as np
from essentia.standard import MonoLoader, TensorflowPredictEffnetDiscogs, TensorflowPredict2D
import requests
from numba import cuda
from pydub import AudioSegment
import subprocess

# Function to install system packages
def install_system_packages():
    with open("packages.txt", "r") as file:
        packages = file.read().strip().split("\n")

    for package in packages:
        try:
            subprocess.check_call(["dpkg", "-s", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"{package} is already installed.")
        except subprocess.CalledProcessError:
            print(f"Installing {package}...")
            subprocess.check_call(["sudo", "apt-get", "install", "-y", package])
            print(f"{package} installed successfully.")

# Call the function to install system packages
install_system_packages()

# Function to download model weights
def download_model_weights():
    model_files = [
        ("genre_discogs400-discogs-effnet-1.pb", "https://essentia.upf.edu/models/classification-heads/genre_discogs400/genre_discogs400-discogs-effnet-1.pb"),
        ("discogs-effnet-bs64-1.pb", "https://essentia.upf.edu/models/feature-extractors/discogs-effnet/discogs-effnet-bs64-1.pb"),
        ("mtg_jamendo_moodtheme-discogs-effnet-1.pb", "https://essentia.upf.edu/models/classification-heads/mtg_jamendo_moodtheme/mtg_jamendo_moodtheme-discogs-effnet-1.pb"),
        ("mtg_jamendo_instrument-discogs-effnet-1.pb", "https://essentia.upf.edu/models/classification-heads/mtg_jamendo_instrument/mtg_jamendo_instrument-discogs-effnet-1.pb")
    ]

    for file_name, url in model_files:
        if not os.path.exists(file_name):
            print(f"Downloading {file_name}...")
            response = requests.get(url)
            with open(file_name, "wb") as file:
                file.write(response.content)
            print(f"Downloaded {file_name} successfully.")
        else:
            print(f"{file_name} already exists. Skipping download.")

# Call the function to download model weights
download_model_weights()

# Function to slice and resample audio files
def slice_and_resample_audio(dataset_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    original_dir = os.path.join(output_dir, "original")
    os.makedirs(original_dir, exist_ok=True)

    for filename in os.listdir(dataset_path):
        if filename.endswith(('.mp3', '.wav', '.flac')):
            os.rename(os.path.join(dataset_path, filename), os.path.join(original_dir, filename))
            audio = AudioSegment.from_file(os.path.join(original_dir, filename))

            audio = audio.set_frame_rate(44100)

            for i in range(0, len(audio), 30000):
                chunk = audio[i:i+30000]
                chunk_filename = f"{os.path.splitext(filename)[0]}_chunk{i//1000}.wav"
                chunk.export(os.path.join(output_dir, chunk_filename), format="wav")

    print("Audio files sliced and resampled successfully.")

# Example usage of slice_and_resample_audio function
dataset_path = "./dataset/gary"
output_dir = "./dataset/gary/split"
slice_and_resample_audio(dataset_path, output_dir)


# @title metadata (labels) for essentia - LONG CELL DONT OPEN
genre_labels = [
    "Blues---Boogie Woogie",
    "Blues---Chicago Blues",
    "Blues---Country Blues",
    "Blues---Delta Blues",
    "Blues---Electric Blues",
    "Blues---Harmonica Blues",
    "Blues---Jump Blues",
    "Blues---Louisiana Blues",
    "Blues---Modern Electric Blues",
    "Blues---Piano Blues",
    "Blues---Rhythm & Blues",
    "Blues---Texas Blues",
    "Brass & Military---Brass Band",
    "Brass & Military---Marches",
    "Brass & Military---Military",
    "Children's---Educational",
    "Children's---Nursery Rhymes",
    "Children's---Story",
    "Classical---Baroque",
    "Classical---Choral",
    "Classical---Classical",
    "Classical---Contemporary",
    "Classical---Impressionist",
    "Classical---Medieval",
    "Classical---Modern",
    "Classical---Neo-Classical",
    "Classical---Neo-Romantic",
    "Classical---Opera",
    "Classical---Post-Modern",
    "Classical---Renaissance",
    "Classical---Romantic",
    "Electronic---Abstract",
    "Electronic---Acid",
    "Electronic---Acid House",
    "Electronic---Acid Jazz",
    "Electronic---Ambient",
    "Electronic---Bassline",
    "Electronic---Beatdown",
    "Electronic---Berlin-School",
    "Electronic---Big Beat",
    "Electronic---Bleep",
    "Electronic---Breakbeat",
    "Electronic---Breakcore",
    "Electronic---Breaks",
    "Electronic---Broken Beat",
    "Electronic---Chillwave",
    "Electronic---Chiptune",
    "Electronic---Dance-pop",
    "Electronic---Dark Ambient",
    "Electronic---Darkwave",
    "Electronic---Deep House",
    "Electronic---Deep Techno",
    "Electronic---Disco",
    "Electronic---Disco Polo",
    "Electronic---Donk",
    "Electronic---Downtempo",
    "Electronic---Drone",
    "Electronic---Drum n Bass",
    "Electronic---Dub",
    "Electronic---Dub Techno",
    "Electronic---Dubstep",
    "Electronic---Dungeon Synth",
    "Electronic---EBM",
    "Electronic---Electro",
    "Electronic---Electro House",
    "Electronic---Electroclash",
    "Electronic---Euro House",
    "Electronic---Euro-Disco",
    "Electronic---Eurobeat",
    "Electronic---Eurodance",
    "Electronic---Experimental",
    "Electronic---Freestyle",
    "Electronic---Future Jazz",
    "Electronic---Gabber",
    "Electronic---Garage House",
    "Electronic---Ghetto",
    "Electronic---Ghetto House",
    "Electronic---Glitch",
    "Electronic---Goa Trance",
    "Electronic---Grime",
    "Electronic---Halftime",
    "Electronic---Hands Up",
    "Electronic---Happy Hardcore",
    "Electronic---Hard House",
    "Electronic---Hard Techno",
    "Electronic---Hard Trance",
    "Electronic---Hardcore",
    "Electronic---Hardstyle",
    "Electronic---Hi NRG",
    "Electronic---Hip Hop",
    "Electronic---Hip-House",
    "Electronic---House",
    "Electronic---IDM",
    "Electronic---Illbient",
    "Electronic---Industrial",
    "Electronic---Italo House",
    "Electronic---Italo-Disco",
    "Electronic---Italodance",
    "Electronic---Jazzdance",
    "Electronic---Juke",
    "Electronic---Jumpstyle",
    "Electronic---Jungle",
    "Electronic---Latin",
    "Electronic---Leftfield",
    "Electronic---Makina",
    "Electronic---Minimal",
    "Electronic---Minimal Techno",
    "Electronic---Modern Classical",
    "Electronic---Musique Concrète",
    "Electronic---Neofolk",
    "Electronic---New Age",
    "Electronic---New Beat",
    "Electronic---New Wave",
    "Electronic---Noise",
    "Electronic---Nu-Disco",
    "Electronic---Power Electronics",
    "Electronic---Progressive Breaks",
    "Electronic---Progressive House",
    "Electronic---Progressive Trance",
    "Electronic---Psy-Trance",
    "Electronic---Rhythmic Noise",
    "Electronic---Schranz",
    "Electronic---Sound Collage",
    "Electronic---Speed Garage",
    "Electronic---Speedcore",
    "Electronic---Synth-pop",
    "Electronic---Synthwave",
    "Electronic---Tech House",
    "Electronic---Tech Trance",
    "Electronic---Techno",
    "Electronic---Trance",
    "Electronic---Tribal",
    "Electronic---Tribal House",
    "Electronic---Trip Hop",
    "Electronic---Tropical House",
    "Electronic---UK Garage",
    "Electronic---Vaporwave",
    "Folk, World, & Country---African",
    "Folk, World, & Country---Bluegrass",
    "Folk, World, & Country---Cajun",
    "Folk, World, & Country---Canzone Napoletana",
    "Folk, World, & Country---Catalan Music",
    "Folk, World, & Country---Celtic",
    "Folk, World, & Country---Country",
    "Folk, World, & Country---Fado",
    "Folk, World, & Country---Flamenco",
    "Folk, World, & Country---Folk",
    "Folk, World, & Country---Gospel",
    "Folk, World, & Country---Highlife",
    "Folk, World, & Country---Hillbilly",
    "Folk, World, & Country---Hindustani",
    "Folk, World, & Country---Honky Tonk",
    "Folk, World, & Country---Indian Classical",
    "Folk, World, & Country---Laïkó",
    "Folk, World, & Country---Nordic",
    "Folk, World, & Country---Pacific",
    "Folk, World, & Country---Polka",
    "Folk, World, & Country---Raï",
    "Folk, World, & Country---Romani",
    "Folk, World, & Country---Soukous",
    "Folk, World, & Country---Séga",
    "Folk, World, & Country---Volksmusik",
    "Folk, World, & Country---Zouk",
    "Folk, World, & Country---Éntekhno",
    "Funk / Soul---Afrobeat",
    "Funk / Soul---Boogie",
    "Funk / Soul---Contemporary R&B",
    "Funk / Soul---Disco",
    "Funk / Soul---Free Funk",
    "Funk / Soul---Funk",
    "Funk / Soul---Gospel",
    "Funk / Soul---Neo Soul",
    "Funk / Soul---New Jack Swing",
    "Funk / Soul---P.Funk",
    "Funk / Soul---Psychedelic",
    "Funk / Soul---Rhythm & Blues",
    "Funk / Soul---Soul",
    "Funk / Soul---Swingbeat",
    "Funk / Soul---UK Street Soul",
    "Hip Hop---Bass Music",
    "Hip Hop---Boom Bap",
    "Hip Hop---Bounce",
    "Hip Hop---Britcore",
    "Hip Hop---Cloud Rap",
    "Hip Hop---Conscious",
    "Hip Hop---Crunk",
    "Hip Hop---Cut-up/DJ",
    "Hip Hop---DJ Battle Tool",
    "Hip Hop---Electro",
    "Hip Hop---G-Funk",
    "Hip Hop---Gangsta",
    "Hip Hop---Grime",
    "Hip Hop---Hardcore Hip-Hop",
    "Hip Hop---Horrorcore",
    "Hip Hop---Instrumental",
    "Hip Hop---Jazzy Hip-Hop",
    "Hip Hop---Miami Bass",
    "Hip Hop---Pop Rap",
    "Hip Hop---Ragga HipHop",
    "Hip Hop---RnB/Swing",
    "Hip Hop---Screw",
    "Hip Hop---Thug Rap",
    "Hip Hop---Trap",
    "Hip Hop---Trip Hop",
    "Hip Hop---Turntablism",
    "Jazz---Afro-Cuban Jazz",
    "Jazz---Afrobeat",
    "Jazz---Avant-garde Jazz",
    "Jazz---Big Band",
    "Jazz---Bop",
    "Jazz---Bossa Nova",
    "Jazz---Contemporary Jazz",
    "Jazz---Cool Jazz",
    "Jazz---Dixieland",
    "Jazz---Easy Listening",
    "Jazz---Free Improvisation",
    "Jazz---Free Jazz",
    "Jazz---Fusion",
    "Jazz---Gypsy Jazz",
    "Jazz---Hard Bop",
    "Jazz---Jazz-Funk",
    "Jazz---Jazz-Rock",
    "Jazz---Latin Jazz",
    "Jazz---Modal",
    "Jazz---Post Bop",
    "Jazz---Ragtime",
    "Jazz---Smooth Jazz",
    "Jazz---Soul-Jazz",
    "Jazz---Space-Age",
    "Jazz---Swing",
    "Latin---Afro-Cuban",
    "Latin---Baião",
    "Latin---Batucada",
    "Latin---Beguine",
    "Latin---Bolero",
    "Latin---Boogaloo",
    "Latin---Bossanova",
    "Latin---Cha-Cha",
    "Latin---Charanga",
    "Latin---Compas",
    "Latin---Cubano",
    "Latin---Cumbia",
    "Latin---Descarga",
    "Latin---Forró",
    "Latin---Guaguancó",
    "Latin---Guajira",
    "Latin---Guaracha",
    "Latin---MPB",
    "Latin---Mambo",
    "Latin---Mariachi",
    "Latin---Merengue",
    "Latin---Norteño",
    "Latin---Nueva Cancion",
    "Latin---Pachanga",
    "Latin---Porro",
    "Latin---Ranchera",
    "Latin---Reggaeton",
    "Latin---Rumba",
    "Latin---Salsa",
    "Latin---Samba",
    "Latin---Son",
    "Latin---Son Montuno",
    "Latin---Tango",
    "Latin---Tejano",
    "Latin---Vallenato",
    "Non-Music---Audiobook",
    "Non-Music---Comedy",
    "Non-Music---Dialogue",
    "Non-Music---Education",
    "Non-Music---Field Recording",
    "Non-Music---Interview",
    "Non-Music---Monolog",
    "Non-Music---Poetry",
    "Non-Music---Political",
    "Non-Music---Promotional",
    "Non-Music---Radioplay",
    "Non-Music---Religious",
    "Non-Music---Spoken Word",
    "Pop---Ballad",
    "Pop---Bollywood",
    "Pop---Bubblegum",
    "Pop---Chanson",
    "Pop---City Pop",
    "Pop---Europop",
    "Pop---Indie Pop",
    "Pop---J-pop",
    "Pop---K-pop",
    "Pop---Kayōkyoku",
    "Pop---Light Music",
    "Pop---Music Hall",
    "Pop---Novelty",
    "Pop---Parody",
    "Pop---Schlager",
    "Pop---Vocal",
    "Reggae---Calypso",
    "Reggae---Dancehall",
    "Reggae---Dub",
    "Reggae---Lovers Rock",
    "Reggae---Ragga",
    "Reggae---Reggae",
    "Reggae---Reggae-Pop",
    "Reggae---Rocksteady",
    "Reggae---Roots Reggae",
    "Reggae---Ska",
    "Reggae---Soca",
    "Rock---AOR",
    "Rock---Acid Rock",
    "Rock---Acoustic",
    "Rock---Alternative Rock",
    "Rock---Arena Rock",
    "Rock---Art Rock",
    "Rock---Atmospheric Black Metal",
    "Rock---Avantgarde",
    "Rock---Beat",
    "Rock---Black Metal",
    "Rock---Blues Rock",
    "Rock---Brit Pop",
    "Rock---Classic Rock",
    "Rock---Coldwave",
    "Rock---Country Rock",
    "Rock---Crust",
    "Rock---Death Metal",
    "Rock---Deathcore",
    "Rock---Deathrock",
    "Rock---Depressive Black Metal",
    "Rock---Doo Wop",
    "Rock---Doom Metal",
    "Rock---Dream Pop",
    "Rock---Emo",
    "Rock---Ethereal",
    "Rock---Experimental",
    "Rock---Folk Metal",
    "Rock---Folk Rock",
    "Rock---Funeral Doom Metal",
    "Rock---Funk Metal",
    "Rock---Garage Rock",
    "Rock---Glam",
    "Rock---Goregrind",
    "Rock---Goth Rock",
    "Rock---Gothic Metal",
    "Rock---Grindcore",
    "Rock---Grunge",
    "Rock---Hard Rock",
    "Rock---Hardcore",
    "Rock---Heavy Metal",
    "Rock---Indie Rock",
    "Rock---Industrial",
    "Rock---Krautrock",
    "Rock---Lo-Fi",
    "Rock---Lounge",
    "Rock---Math Rock",
    "Rock---Melodic Death Metal",
    "Rock---Melodic Hardcore",
    "Rock---Metalcore",
    "Rock---Mod",
    "Rock---Neofolk",
    "Rock---New Wave",
    "Rock---No Wave",
    "Rock---Noise",
    "Rock---Noisecore",
    "Rock---Nu Metal",
    "Rock---Oi",
    "Rock---Parody",
    "Rock---Pop Punk",
    "Rock---Pop Rock",
    "Rock---Pornogrind",
    "Rock---Post Rock",
    "Rock---Post-Hardcore",
    "Rock---Post-Metal",
    "Rock---Post-Punk",
    "Rock---Power Metal",
    "Rock---Power Pop",
    "Rock---Power Violence",
    "Rock---Prog Rock",
    "Rock---Progressive Metal",
    "Rock---Psychedelic Rock",
    "Rock---Psychobilly",
    "Rock---Pub Rock",
    "Rock---Punk",
    "Rock---Rock & Roll",
    "Rock---Rockabilly",
    "Rock---Shoegaze",
    "Rock---Ska",
    "Rock---Sludge Metal",
    "Rock---Soft Rock",
    "Rock---Southern Rock",
    "Rock---Space Rock",
    "Rock---Speed Metal",
    "Rock---Stoner Rock",
    "Rock---Surf",
    "Rock---Symphonic Rock",
    "Rock---Technical Death Metal",
    "Rock---Thrash",
    "Rock---Twist",
    "Rock---Viking Metal",
    "Rock---Yé-Yé",
    "Stage & Screen---Musical",
    "Stage & Screen---Score",
    "Stage & Screen---Soundtrack",
    "Stage & Screen---Theme",
]
mood_theme_classes = [
    "action",
    "adventure",
    "advertising",
    "background",
    "ballad",
    "calm",
    "children",
    "christmas",
    "commercial",
    "cool",
    "corporate",
    "dark",
    "deep",
    "documentary",
    "drama",
    "dramatic",
    "dream",
    "emotional",
    "energetic",
    "epic",
    "fast",
    "film",
    "fun",
    "funny",
    "game",
    "groovy",
    "happy",
    "heavy",
    "holiday",
    "hopeful",
    "inspiring",
    "love",
    "meditative",
    "melancholic",
    "melodic",
    "motivational",
    "movie",
    "nature",
    "party",
    "positive",
    "powerful",
    "relaxing",
    "retro",
    "romantic",
    "sad",
    "sexy",
    "slow",
    "soft",
    "soundscape",
    "space",
    "sport",
    "summer",
    "trailer",
    "travel",
    "upbeat",
    "uplifting"
]
instrument_classes = [
    "accordion",
    "acousticbassguitar",
    "acousticguitar",
    "bass",
    "beat",
    "bell",
    "bongo",
    "brass",
    "cello",
    "clarinet",
    "classicalguitar",
    "computer",
    "doublebass",
    "drummachine",
    "drums",
    "electricguitar",
    "electricpiano",
    "flute",
    "guitar",
    "harmonica",
    "harp",
    "horn",
    "keyboard",
    "oboe",
    "orchestra",
    "organ",
    "pad",
    "percussion",
    "piano",
    "pipeorgan",
    "rhodes",
    "sampler",
    "saxophone",
    "strings",
    "synthesizer",
    "trombone",
    "trumpet",
    "viola",
    "violin",
    "voice"
]

# Function to filter predictions based on threshold
def filter_predictions(predictions, class_list, threshold=0.1):
    predictions_mean = np.mean(predictions, axis=0)
    sorted_indices = np.argsort(predictions_mean)[::-1]
    filtered_indices = [i for i in sorted_indices if predictions_mean[i] > threshold]
    filtered_labels = [class_list[i] for i in filtered_indices]
    filtered_values = [predictions_mean[i] for i in filtered_indices]
    return filtered_labels, filtered_values

# Function to create comma-separated unique tags
def make_comma_separated_unique(tags):
    seen_tags = set()
    result = []
    for tag in ', '.join(tags).split(', '):
        if tag not in seen_tags:
            result.append(tag)
            seen_tags.add(tag)
    return ', '.join(result)

# Function to get audio features using Essentia
def get_audio_features(audio_filename):
    audio = MonoLoader(filename=audio_filename, sampleRate=16000, resampleQuality=4)()
    embedding_model = TensorflowPredictEffnetDiscogs(graphFilename="discogs-effnet-bs64-1.pb", output="PartitionedCall:1")
    embeddings = embedding_model(audio)

    result_dict = {}

    genre_model = TensorflowPredict2D(graphFilename="genre_discogs400-discogs-effnet-1.pb", input="serving_default_model_Placeholder", output="PartitionedCall:0")
    predictions = genre_model(embeddings)
    filtered_labels, _ = filter_predictions(predictions, genre_labels)
    filtered_labels = ', '.join(filtered_labels).replace("---", ", ").split(', ')
    result_dict['genres'] = make_comma_separated_unique(filtered_labels)

    mood_model = TensorflowPredict2D(graphFilename="mtg_jamendo_moodtheme-discogs-effnet-1.pb")
    predictions = mood_model(embeddings)
    filtered_labels, _ = filter_predictions(predictions, mood_theme_classes, threshold=0.05)
    result_dict['moods'] = make_comma_separated_unique(filtered_labels)

    instrument_model = TensorflowPredict2D(graphFilename="mtg_jamendo_instrument-discogs-effnet-1.pb")
    predictions = instrument_model(embeddings)
    filtered_labels, _ = filter_predictions(predictions, instrument_classes)
    result_dict['instruments'] = filtered_labels

    return result_dict

# Autolabelling and creating train/test split
print('Autolabelling...')
dataset_path = "./dataset/gary/split"
folder_to_save_dataset_in = "./dataset/gary"

# This only works if we have audio filenames like 'artist_name_chunk_XX.wav'. We don't really need artist names in our prompts
# and it's debatable whether a continuations model needs prompts. it will be fine-tuned and overfit to produce certain qualities from input audio.
def extract_artist_from_filename(filename):
    match = re.search(r'(.+?)\s\d+_chunk\d+\.wav', filename)
    artist = match.group(1) if match else ""
    return artist.replace("mix", "").strip() if "mix" in artist else artist

with open(os.path.join(folder_to_save_dataset_in, "train.jsonl"), "w") as train_file, \
     open(os.path.join(folder_to_save_dataset_in, "test.jsonl"), "w") as eval_file:
    dset = os.listdir(dataset_path)
    random.shuffle(dset)
    for filename in tqdm(dset):
        try:
            result = get_audio_features(os.path.join(dataset_path, filename))
        except:
            result = {"genres": [], "moods": [], "instruments": []}
        y, sr = librosa.load(os.path.join(dataset_path, filename))
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        tempo = round(tempo)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        key = np.argmax(np.sum(chroma, axis=1))
        key = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][key]
        length = librosa.get_duration(y=y, sr=sr)
        artist_name = extract_artist_from_filename(filename)
        entry = {
            "key": f"{key}",
            "artist": artist_name,
            "sample_rate": 44100,
            "file_extension": "wav",
            "description": "",
            "keywords": "",
            "duration": length,
            "bpm": tempo,
            "genre": result.get('genres', ""),
            "title": filename,
            "name": "",
            "instrument": result.get('instruments', ""),
            "moods": result.get('moods', []),
            "path": os.path.join(dataset_path, filename)
        }
        if random.random() < 0.85:
            train_file.write(json.dumps(entry) + '\n')
        else:
            eval_file.write(json.dumps(entry) + '\n')

# Clear CUDA memory for fine-tuning
device = cuda.get_current_device()
device.reset()

# Create YAML configuration file
config_path = os.path.join(folder_to_save_dataset_in, "train.yaml")
package_str = "package"
yaml_contents = f"""#@{package_str} __global__

datasource:
  max_channels: 2
  max_sample_rate: 44100

  evaluate: egs/eval
  generate: egs/train
  train: egs/train
  valid: egs/eval
"""
with open(config_path, 'w') as yaml_file:
    yaml_file.write(yaml_contents)