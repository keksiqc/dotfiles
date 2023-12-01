function which ($command) {
  Get-Command -Name $command -ErrorAction SilentlyContinue |
  Select-Object -ExpandProperty Path -ErrorAction SilentlyContinue
}

function ll {
  eza --long --icons --git $args
}

function la {
  eza --long --icons --git --all $args
}

function .. {
  Set-Location ..
}

function ... {
  Set-Location ..\..
}

function .... {
  Set-Location ..\..\..
}

function home {
  Set-Location ~
}
