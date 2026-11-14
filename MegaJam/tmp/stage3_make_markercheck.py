from pathlib import Path
p=Path("tmp/stage3_resolution_playcheck.py")
s=p.read_text(encoding="utf-8")
begin=s.index('                await asyncio.sleep(7)')
end=s.index('                await move(origin + 210)',begin)
s=s[:begin]+s[end:]
Path("tmp/stage3_resolution_markers_check.py").write_text(s,encoding="utf-8")
