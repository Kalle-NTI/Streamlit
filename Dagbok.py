import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import streamlit_authenticator as stauth
import whisper
from pydub import AudioSegment
import os
from audio_recorder_streamlit import audio_recorder


TEXT_HEIGHT = 300

st.set_page_config(
    page_title = "Mitt Dagbok",
    page_icon = ":)"
)

upload_path = "uploads/"
download_path = "downloads/"
uploaded_file = "audiofile.wav"

audio_tags = {'comments': 'konveterat genom pydub'}


try:
    os.mkdir(upload_path)
except:
    pass
try:
    os.mkdir(download_path)
except:
    pass

def to_fil(audio_file, output_audio_file, upload_path, download_path):
    if audio_file.split('.')[-1].lower()=="wav":
       audio_data = AudioSegment.from_wav(os.path.join(upload_path,audio_file))
       audio_data.export(os.path.join(download_path,output_audio_file), format ="mp3", tags=audio_tags) 
       
    
    elif audio_file.split('.')[-1].lower()=="mp3":
        audio_data = AudioSegment.from_mp3(os.path.join(upload_path,audio_file))
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3", tags=audio_tags)

    elif audio_file.split('.')[-1].lower()=="ogg":
        audio_data = AudioSegment.from_ogg(os.path.join(upload_path,audio_file))
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3", tags=audio_tags)

    elif audio_file.split('.')[-1].lower()=="wma":
        audio_data = AudioSegment.from_file(os.path.join(upload_path,audio_file),"wma")
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3", tags=audio_tags)

    elif audio_file.split('.')[-1].lower()=="aac":
        audio_data = AudioSegment.from_file(os.path.join(upload_path,audio_file),"aac")
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3", tags=audio_tags)

    elif audio_file.split('.')[-1].lower()=="flac":
        audio_data = AudioSegment.from_file(os.path.join(upload_path,audio_file),"flac")
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3", tags=audio_tags)

    elif audio_file.split('.')[-1].lower()=="flv":
        audio_data = AudioSegment.from_flv(os.path.join(upload_path,audio_file))
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3", tags=audio_tags)

    elif audio_file.split('.')[-1].lower()=="mp4":
        audio_data = AudioSegment.from_file(os.path.join(upload_path,audio_file),"mp4")
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3", tags=audio_tags)
    return output_audio_file
st.cache_data()
def process_audio(filename):
    with open(os.path.join(upload_path, uploaded_file), "wb") as f:
        f.write(audio_bytes)
    with st.spinner(f"Konventerar Ljud...."):
        output_audio_file = uploaded_file.split('.')[0] + '.mp3'
        output_audio_file = to_fil(uploaded_file, output_audio_file, uploaded_file, download_path)
    with st.spinner(f"Generating Transcript.."):
        filename = str(os.path.abspath(os.path.join(download_path, output_audio_file)))
        model = whisper.load_model("base")
        result = model.transcribe(filename)
    return result["text"]

def reset_modifying():
    st.session_state["modifying"] = False

authenticator = stauth.Authenticate(
    dict(st.secrets['credentials']).copy(),
    st.secrets['cookie']['name'],
    st.secrets['cookie']['key'],
    st.secrets['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    authenticator.logout('logut', 'sidebar')


    st.cache_resource
    def init_connection():
        uri = st.secrets["mongo"].uri
        return MongoClient(uri, server_api=ServerApi('1'))
    

client = init_connection()

@st.cache_data(ttl=600)

def get_data(num_enteries, start_datum, slut_datum):
    start_datum = datetime.combine(start_datum, datetime.max.time())
    slut_datum = datetime.combine(slut_datum, datetime.min.time())
    try:
        items = client.Dagbok.entries.find(
            {"Datum": {"$gte": slut_datum, "$lte": start_datum}},
            limit=num_enteries,
        )
        items = list(items)
    
    except Exception as e:
        st.warning("Misslyckades load från MonoDB Data")
        st.error(repr(e))
        items = []
    return items

if not st.session_state.get("modifierar", False):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader('Nyt Dagbok')
    with col2:
        audio_bytes = audio_recorder(
            text="",
            icon_size="3",
        )
    if audio_bytes is not None:
        try:
            transcript = process_audio(audio_bytes)
        
        except Exception as e:
            st.warning('Det finns ett fel med ljudet processen')
            transcript = None
            print(e)
    
    else:
        transcript = None
    
    entry = entry = st.text_area(label="Entry", height=TEXT_HEIGHT, label_visibility="hidden", value=transcript)
    submit = st.button("lägg entry", use_container_width=True)

    st.divider()

    if submit and entry:
        date = datetime.now()
        client.Dagbok.entries.insert_one({"date": date, "entre": entry})
        get_data.clear()
        st.experimental_rerun()

    st.sidebar.subheader('Välj Datum')
    idag = datetime.now()
    start_Datum = st.sidebar.date_input('Start Datum', idag)
    ettårsen = idag.replace(år=idag.år - 1)
    slut_datum = st.sidebar.date_input('Slut Datum', ettårsen)

    st.sidebar.subheader('Antal styckna')
    num_entries = st.sidebar.slider(
        'välj antal entries', 1, 10, 3
    )


    st.subheader('Gamla entries')
    items = get_data(num_entries, start_Datum, slut_datum)
    for item in items:
        date = item["date"].strftime("%b %d, %Y")
        st.markdown(f"**{date} -** {item['entry']}")
        modify = st.button("Modify", key="modify_"+repr(item["_id"]),
                            use_container_width=True)
        
        if modify:
                st.session_state["modifierar"] = True
                st.session_state["entry"] = item["entry"]
                st.session_state["date"] = item["date"]
                st.session_state["id"] = item["_id"]
                st.experimental_rerun()
else:

    header_columns = st.columns(3)

    header_columns[0].subheader("Modifiera Entry")
    header_columns[2].button("Return", key="come_back", use_container_width=True,
                             on_click = reset_modifying)
    id = st.session_state["id"]
    date = st.session_state["date"]
    entry = st.text_area("Entry", st.session_state["entry"], height=TEXT_HEIGHT,
                         label_visibility="hidden")
    
    col1, col2 = st.columns(2)

    delete = col1.button('Ta bort entry', use_container_width=True)
    if delete:
        client.Dagbok.entries.delete_one(
            {"_id": id},
        )
        st.session_state['modifierar'] = False
        get_data.clear()
        st.experimental_rerun()

    sumbit = col2.button('Modifera entry', use_container_width=True)
    if sumbit:
        client.Dagbok.entries.update_one(
            {"id": id},
            {"$set": {"entry": entry}},
        )
        st.session_state['modifierar']=False
        get_data.clear()
        st.experimental_rerun()
    elif authentication_status == False:
        st.error('Namn/Lösenord är fel')
    elif authentication_status == None:
        st.warning('Lägg in ditt Namn och Lösenord')
    



