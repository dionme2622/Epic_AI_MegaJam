"""Prepare chronological user-supplied clips; run --import inside Unreal Python."""
from pathlib import Path
import csv, json, shutil, subprocess, wave, sys

root = Path(__file__).resolve().parents[2]
folder = root/'SourceAssets/GameplayVoice'
folder.mkdir(exist_ok=True)
manifest_path = folder/'manifest.json'
if '--import' not in sys.argv:
    with (root/'SourceAssets/VoicePrompts/Inworld_All_Dialogue_Prompts_KO_EN.csv').open(encoding='utf-8-sig') as f:
        cues = {r['id']:r for r in csv.DictReader(f)}
    ids = ['CastleResolve','CastleChair','CastleWorkshop','WorkshopArrival','WorkshopLift','WorkshopLegs','EditingArrival','EditingCrate','StorageLog','VaultArrival','VaultExhibit','FinalTake']
    files = sorted((Path.home()/'Downloads').glob('inworld-tts-2_Hades_English_11-15-2026 22-0*.mp3'))
    assert len(files)==len(ids)==12
    rows=[]
    for file,id in zip(files,ids):
        shutil.copy2(file,folder/(id+'.mp3'))
        wav=folder/(id+'.wav')
        subprocess.run(['D:/ffmpeg-8.0.1-full_build/bin/ffmpeg.exe','-v','error','-y','-i',str(file),'-ar','48000','-ac','1','-c:a','pcm_s16le',str(wav)],check=True)
        with wave.open(str(wav),'rb') as w:
            duration=w.getnframes()/w.getframerate()
            import array
            pcm=array.array('h',w.readframes(w.getnframes()))
            peak=max(abs(v) for v in pcm)
        assert duration>0 and peak>0
        rows.append(dict(id=id,source=file.name,english=cues[id]['en'],duration=duration,peak=peak,asset='/Game/DirectorCut/GameplayVoice/S_'+id))
    manifest_path.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    # Exact English subtitle lookup keeps all twelve callers on a single playback path.
    header=['// Generated from GameplayVoice/manifest.json.\n#pragma once\n',
            'inline const TCHAR* FindDirectorCutVoice(const FString& English)\n{']
    for r in rows:
        if r['id'] == 'StorageLog':
            continue  # Retired HUD notice: now an in-world paper note.
        text=r['english']
        if r['id'] not in ('StorageLog',): text='Dragon: '+text
        text=text.replace('\\','\\\\').replace('"','\\"')
        header.append(f'    if (English == TEXT("{text}")) return TEXT("{r["asset"]}.S_{r["id"]}");')
    header.append('    return nullptr;\n}\n')
    (root/'Source/MegaJam/DirectorCutVoiceLookup.h').write_text('\n'.join(header),encoding='utf-8')
    print(json.dumps(rows,ensure_ascii=False,indent=2))
else:
    import unreal
    rows=json.loads(manifest_path.read_text(encoding='utf-8'))
    for r in rows:
        task=unreal.AssetImportTask()
        task.filename=str(folder/(r['id']+'.wav'))
        task.destination_path='/Game/DirectorCut/GameplayVoice'
        task.destination_name='S_'+r['id']
        task.automated=True;task.replace_existing=True;task.save=True
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        sound=unreal.load_asset(r['asset'])
        assert sound, r['asset']
        r['imported_duration']=sound.get_editor_property('duration')
        assert abs(r['duration']-r['imported_duration'])<0.1
    audit=[]
    paths=['/Game/DirectorCut/Prologue/LS_BossPrologue_Cinematic']+['/Game/DirectorCut/Ending/'+n for n in ['LS_BossEnding_Dialogue','LS_BossEnding_Cart','LS_BossEnding_HeroLegs','LS_BossEnding_OriginalLegs']]
    for path in paths:
        seq=unreal.load_asset(path)
        assert seq,path
        sounds=[]
        for track in seq.get_tracks():
            if isinstance(track,unreal.MovieSceneAudioTrack):
                for section in track.get_sections():
                    sound=section.get_sound()
                    assert sound, path
                    sounds.append(dict(sound=sound.get_path_name(),duration=sound.get_editor_property('duration'),start=section.get_start_frame(),end=section.get_end_frame()))
        audit.append(dict(sequence=path,audio=sounds))
    (folder/'asset_audit.json').write_text(json.dumps(dict(gameplay=rows,cinematics=audit),ensure_ascii=False,indent=2),encoding='utf-8')
    print('GAMEPLAY_VOICE_IMPORT_AND_AUDIT_COMPLETE')
