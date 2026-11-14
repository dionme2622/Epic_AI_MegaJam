from pathlib import Path
p=Path("tmp/Stage4RgbRoom/build.py")
s=p.read_text(encoding="utf-8-sig")
head=s[:s.index("# Ceiling")]
floor=s[s.index("# The gallery floor"):s.index("# Proscenium")]
gate=s[s.index("# The locked passage"):s.index("for y in range(-69")]
Path("tmp/Stage4RgbRoom/revise.py").write_text(head+floor+gate,encoding="utf-8")
