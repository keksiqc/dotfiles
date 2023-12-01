# set PowerShell to UTF-8
[console]::InputEncoding = [console]::OutputEncoding = New-Object System.Text.UTF8Encoding

# git
Import-Module posh-git

# oh-my-posh
# Import-Module oh-my-posh
# $THEMEPATH = "C:\Users\marlo\AppData\Local\oh-my-posh\themes"
# oh-my-posh --init --shell pwsh --config $THEMEPATH\zash.omp.json | Invoke-Expression

# Starship
Invoke-Expression (&starship init powershell)

Import-Module -Name Terminal-Icons

# PSReadLine
Set-PSReadLineOption -EditMode Emacs
Set-PSReadLineOption -BellStyle None
Set-PSReadLineKeyHandler -Chord 'Ctrl+d' -Function DeleteChar
Set-PSReadLineKeyHandler -Key UpArrow -Function HistorySearchBackward
Set-PSReadLineKeyHandler -Key DownArrow -Function HistorySearchForward
Set-PSReadLineOption -PredictionSource History

# Fzf
Import-Module PSFzf
Set-PsFzfOption -PSReadlineChordProvider 'Ctrl+f' -PSReadlineChordReverseHistory 'Ctrl+r'

# Env
$ENV:GIT_SSH = "C:\Windows\system32\OpenSSH\ssh.exe"

# Remove Alias
if (-not (Test-Path $profile)) {
  New-Item -ItemType File -Path (Split-Path $profile) -Force -Name (Split-Path $profile -Leaf)
}

$profileEntry = 'Remove-Item Alias:ni -Force -ErrorAction Ignore'
$profileContent = Get-Content $profile
if ($profileContent -notcontains $profileEntry) {
  $profileEntry | Out-File $profile -Append -Force
}

# Functions
. "$PSScriptRoot\functions.ps1"

# Aliases
. "$PSScriptRoot\aliases.ps1"
