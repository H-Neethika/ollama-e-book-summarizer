param(
  [Parameter(Mandatory=$true)][string]$InputFile,
  [string]$Model,
  [string]$Prompt
)

$argsList = @($InputFile)
if ($Model) { $argsList += @("--model", $Model) }
if ($Prompt) { $argsList += @("--prompt", $Prompt) }

python -m src.cli.pipeline_cli @argsList

