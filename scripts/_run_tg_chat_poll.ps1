$ErrorActionPreference="Continue"
$root="C:\Users\HP\OneDrive\The Vault\Africa Season 1"
$log="$root\renders\quality\telegram_chat_poll.log"
$tok=[Environment]::GetEnvironmentVariable("TELEGRAM_BOT_TOKEN","User")
function W($m){ $l="[{0}] {1}" -f (Get-Date -Format "s"),$m; Add-Content $log $l }
W "START poll chat_id"
for($i=0;$i -lt 240;$i++){ # ~2h at 30s
  if(-not $tok){ $tok=[Environment]::GetEnvironmentVariable("TELEGRAM_BOT_TOKEN","User") }
  if($tok){
    try{
      $upd=Invoke-RestMethod -Uri "https://api.telegram.org/bot$tok/getUpdates?limit=20&timeout=20" -Method Get
      foreach($u in $upd.result){
        $m=$u.message; if(-not $m){$m=$u.edited_message}
        if($m -and $m.chat){
          $cid=[string]$m.chat.id
          Set-Content "$root\renders\quality\TELEGRAM_CHAT_ID.txt" $cid -Encoding ASCII
          [Environment]::SetEnvironmentVariable("AFRICA_TELEGRAM_CHAT_ID",$cid,"User")
          W "GOT chat_id=$cid text=$($m.text)"
          # ack
          $body=@{chat_id=$cid;text="Africa S1 bot linked. Will ping when Scene 01 Cold Open HQ finishes."}|ConvertTo-Json -Compress
          Invoke-RestMethod -Uri "https://api.telegram.org/bot$tok/sendMessage" -Method Post -Body $body -ContentType "application/json; charset=utf-8" | Out-Null
          # if pending S01, send it
          $pend="$root\renders\quality\TELEGRAM_S01_PENDING.txt"
          if(Test-Path $pend){
            $msg=Get-Content $pend -Raw
            $body2=@{chat_id=$cid;text=$msg}|ConvertTo-Json -Compress
            Invoke-RestMethod -Uri "https://api.telegram.org/bot$tok/sendMessage" -Method Post -Body $body2 -ContentType "application/json; charset=utf-8" | Out-Null
            W "sent PENDING"
          }
          exit 0
        }
      }
    } catch { W "err $($_.Exception.Message)" }
  }
  Start-Sleep -Seconds 30
}
W "END timeout"
