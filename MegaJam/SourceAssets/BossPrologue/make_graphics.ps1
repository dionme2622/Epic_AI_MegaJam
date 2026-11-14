Add-Type -AssemblyName System.Drawing
$root = Join-Path $PSScriptRoot 'Graphics'
New-Item -ItemType Directory -Force -Path $root | Out-Null
$captions = @(
    @('01_Hero','용사: "각오해라, 드래곤!!!"','Hero: "Prepare yourself, dragon!"'),
    @('02_Dragon','드래곤: "크하하!! 통구이로 만들어주지!!!!!!"','Dragon: "Ha ha ha! I''ll roast you alive!"'),
    @('03_Missing','드래곤: "잠깐… 내 다리는 어디 갔지?"','Dragon: "Wait... Where did my legs go?"'),
    @('04_Protest','드래곤: "화면에 안 나온다고 다리를 떼어 가?"','Dragon: "You took my legs because they were off camera?"')
)
$koFont = New-Object System.Drawing.Font('Malgun Gothic',44,[System.Drawing.FontStyle]::Bold)
$enFont = New-Object System.Drawing.Font('Arial',34,[System.Drawing.FontStyle]::Regular)
function New-Canvas([int]$w,[int]$h) {
    $bmp = New-Object System.Drawing.Bitmap($w,$h,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    return @($bmp,$g)
}
foreach ($row in $captions) {
    $canvas = New-Canvas 1920 220; $bmp=$canvas[0]; $g=$canvas[1]
    $bg = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(205,6,9,18))
    $white = [System.Drawing.Brushes]::White
    $g.FillRectangle($bg,50,5,1820,205)
    $sf = New-Object System.Drawing.StringFormat
    $sf.Alignment = [System.Drawing.StringAlignment]::Center
    $g.DrawString($row[1],$koFont,$white,[System.Drawing.RectangleF]::new(80,22,1760,82),$sf)
    $g.DrawString($row[2],$enFont,$white,[System.Drawing.RectangleF]::new(80,114,1760,72),$sf)
    $bmp.Save((Join-Path $root ($row[0]+'.png')),[System.Drawing.Imaging.ImageFormat]::Png)
    $sf.Dispose();$bg.Dispose();$g.Dispose();$bmp.Dispose()
}
function Make-Card([string]$name,[string[]]$lines,[int]$w,[int]$h,[int]$fontSize) {
    $canvas=New-Canvas $w $h; $bmp=$canvas[0]; $g=$canvas[1]
    $paper=New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255,247,219,126))
    $ink=New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255,38,28,22))
    $g.FillRectangle($paper,0,0,$w,$h)
    $font=New-Object System.Drawing.Font('Malgun Gothic',$fontSize,[System.Drawing.FontStyle]::Bold)
    $y=24
    foreach ($line in $lines) {$g.DrawString($line,$font,$ink,28,$y);$y+=$fontSize*1.6}
    $bmp.Save((Join-Path $root ($name+'.png')),[System.Drawing.Imaging.ImageFormat]::Png)
    $font.Dispose();$paper.Dispose();$ink.Dispose();$g.Dispose();$bmp.Dispose()
}
Make-Card '05_DevNote' @('개발 메모','최종 보스 하체 — 테스트 구역으로 이동.','현재 카메라에 잡히지 않으므로 임시 제거.') 1024 370 37

$canvas=New-Canvas 1024 512; $bmp=$canvas[0]; $g=$canvas[1]
$outer=New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(170,255,69,10))
$middle=New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(220,255,158,16))
$core=New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(245,255,234,104))
$g.FillPolygon($outer,[System.Drawing.Point[]]@(
    [System.Drawing.Point]::new(20,250),[System.Drawing.Point]::new(235,190),
    [System.Drawing.Point]::new(160,95),[System.Drawing.Point]::new(450,160),
    [System.Drawing.Point]::new(405,35),[System.Drawing.Point]::new(705,165),
    [System.Drawing.Point]::new(1020,170),[System.Drawing.Point]::new(1020,365),
    [System.Drawing.Point]::new(720,350),[System.Drawing.Point]::new(430,490),
    [System.Drawing.Point]::new(450,355),[System.Drawing.Point]::new(160,430),
    [System.Drawing.Point]::new(235,315)))
$g.FillPolygon($middle,[System.Drawing.Point[]]@(
    [System.Drawing.Point]::new(125,255),[System.Drawing.Point]::new(390,205),
    [System.Drawing.Point]::new(325,145),[System.Drawing.Point]::new(620,205),
    [System.Drawing.Point]::new(885,205),[System.Drawing.Point]::new(1015,215),
    [System.Drawing.Point]::new(1015,335),[System.Drawing.Point]::new(785,330),
    [System.Drawing.Point]::new(445,400),[System.Drawing.Point]::new(410,325)))
$g.FillPolygon($core,[System.Drawing.Point[]]@(
    [System.Drawing.Point]::new(280,260),[System.Drawing.Point]::new(535,228),
    [System.Drawing.Point]::new(780,235),[System.Drawing.Point]::new(1010,245),
    [System.Drawing.Point]::new(1010,310),[System.Drawing.Point]::new(750,307),
    [System.Drawing.Point]::new(535,325)))
$bmp.Save((Join-Path $root '07_Fire.png'),[System.Drawing.Imaging.ImageFormat]::Png)
$outer.Dispose();$middle.Dispose();$core.Dispose();$g.Dispose();$bmp.Dispose()
$koFont.Dispose();$enFont.Dispose()
