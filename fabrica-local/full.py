import json,time,urllib.request as u,hashlib,sys
B="http://127.0.0.1:8001"
letra="""[Intro]
Ooh-oh, ooh-oh

[Verse 1]
Sale el sol sobre la isla
el mar nos llama a volar
la arena guarda tus pasos
y el viento sabe cantar

[Pre-Chorus]
Sube, sube, ya se siente
todo el cielo en la mirada

[Chorus]
La isla es nuestra, la isla es de todos
Island Crew, vamos a cantar
La isla es nuestra, la isla es de todos
conmigo, con el mar

[Verse 2]
Tablas, risas y café
la tarde pinta de oro
no hay prisa en este lugar
somos un solo coro

[Pre-Chorus]
Sube, sube, ya se siente
todo el cielo en la mirada

[Chorus]
La isla es nuestra, la isla es de todos
Island Crew, vamos a cantar
La isla es nuestra, la isla es de todos
conmigo, con el mar

[Bridge]
Y si la ola se rompe
volvemos a empezar
juntos somos más fuertes
que cualquier tempestad

[Final Chorus]
La isla es nuestra, la isla es de todos
Island Crew, vamos a cantar
La isla es nuestra, la isla es de todos
conmigo, con el mar

[Outro]
Island Crew, ooh-oh
conmigo, con el mar"""
p={"prompt":"Canción pop tropical alegre de verano, 108 BPM, guitarra limpia, bajo, batería, palmas, sintetizador brillante, voz cantada en español, espíritu de isla, libertad, surf y amistad, estructura completa con intro, estrofas, estribillo pegadizo, puente y final","lyrics":letra,"vocal_language":"es","audio_duration":170,"bpm":108,"thinking":False,"audio_format":"wav","batch_size":1,"seed":7,"use_random_seed":False}
r=json.load(u.urlopen(u.Request(B+"/release_task",json.dumps(p).encode(),{"Content-Type":"application/json"})))
print(r,flush=True); tid=r["data"]["task_id"]
while True:
    time.sleep(10)
    q=json.load(u.urlopen(u.Request(B+"/query_result",json.dumps({"task_id_list":[tid]}).encode(),{"Content-Type":"application/json"})))
    d=q["data"][0]; print(d.get("status"),flush=True)
    if d.get("status")==1:
        res=json.loads(d["result"])[0]; f=res["file"]; print(f,flush=True)
        data=u.urlopen(B+f).read(); out="/Volumes/T5 EVO/IslandCrewAI/musica/SONG_002_completa_v1.wav"
        open(out,"wb").write(data); print("OK",out,len(data),hashlib.sha256(data).hexdigest(),flush=True); break
    if d.get("status")==2: print("FALLO",d,flush=True); break
