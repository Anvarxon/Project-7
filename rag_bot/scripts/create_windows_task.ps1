param(
    [string]$ProjectDir = "C:\quantumforge-rag\rag_bot",
    [string]$Python = "python"
)

$action = New-ScheduledTaskAction -Execute $Python -Argument "scripts/update_index.py" -WorkingDirectory $ProjectDir
$trigger = New-ScheduledTaskTrigger -Daily -At 06:00
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -RestartCount 2 -RestartInterval (New-TimeSpan -Minutes 10)
Register-ScheduledTask -TaskName "QuantumForgeRagIndexUpdate" -Action $action -Trigger $trigger -Settings $settings -Description "Daily FAISS index update for QuantumForge RAG bot"

