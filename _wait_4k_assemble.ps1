$Project = "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
$Log = Join-Path $Project "workflow_1080_then_4k_log.txt"
$Scenes = @("01_ColdOpen","02_Context2007","03_Beat1_Hubs","04_Beat1_Phone","05_Beat2_Money","06_Beat2_Solar","07_Beat3_Gap","08_Beat3_SecondaryCity","09_Closer","10_EndCard")
$Clips4K = Join-Path $Project "renders\video_clips_4k"
function W($m){ $l="[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $m; Add-Content $Log $l }
W "PHASE B: waiting for 4K clips..."
while ($true) {
  $n=0; foreach($s in $Scenes){ $p=Join-Path $Clips4K ($s+".mp4"); if((Test-Path $p) -and ((Get-Item $p).Length -gt 1.5MB)){$n++} }
  W ("  4K clips: {0}/10" -f $n)
  if($n -eq 10){ break }
  Start-Sleep 180
}
W "Assembling 4K master..."
python (Join-Path $Project "assemble_final_video.py") --dir $Clips4K --output (Join-Path $Project "Africa_S1_Silicon_Savannah_7min_4K.mp4") --master (Join-Path $Project "Africa_S1_Silicon_Savannah_7min_4K_MASTER.mp4")
W "PHASE B COMPLETE"
