param(
    [string]$Python = "C:\Users\Microsoft\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ToolPath = Join-Path $ProjectRoot ".build_tools"
$ReleaseRoot = Join-Path $ProjectRoot "发布版本"
$BuildRoot = Join-Path $ProjectRoot "build"
$IconPath = Join-Path $ProjectRoot "assets\ui\linked_ops_logo.ico"
$VersionPath = Join-Path $ProjectRoot "version_info.txt"
$EntryPath = Join-Path $ProjectRoot "app.py"
$PlayerVersionPath = Join-Path $ProjectRoot "player_version_info.txt"
$PlayerEntryPath = Join-Path $ProjectRoot "player_bp_app.py"

if (-not (Test-Path -LiteralPath $Python)) {
    $PythonCommand = Get-Command python -ErrorAction Stop
    $Python = $PythonCommand.Source
}
if (-not (Test-Path -LiteralPath (Join-Path $ToolPath "PyInstaller"))) {
    throw "未找到本地 PyInstaller。请先将 PyInstaller 安装到 .build_tools。"
}

$env:PYTHONPATH = $ToolPath
New-Item -ItemType Directory -Force -Path $ReleaseRoot | Out-Null
New-Item -ItemType Directory -Force -Path $BuildRoot | Out-Null

$CommonArgs = @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--windowed",
    "--icon", $IconPath,
    "--version-file", $VersionPath,
    "--add-data", "$ProjectRoot\data;data",
    "--add-data", "$ProjectRoot\assets;assets",
    "--specpath", (Join-Path $BuildRoot "spec")
)

& $Python @CommonArgs `
    "--name" "联锁对抗BP助手" `
    "--onefile" `
    "--distpath" (Join-Path $ReleaseRoot "单文件版") `
    "--workpath" (Join-Path $BuildRoot "onefile") `
    $EntryPath

& $Python @CommonArgs `
    "--name" "联锁对抗BP助手_文件夹版" `
    "--onedir" `
    "--distpath" (Join-Path $ReleaseRoot "绿色文件夹版") `
    "--workpath" (Join-Path $BuildRoot "onedir") `
    $EntryPath

$PlayerArgs = @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--windowed",
    "--icon", $IconPath,
    "--version-file", $PlayerVersionPath,
    "--add-data", "$ProjectRoot\data;data",
    "--add-data", "$ProjectRoot\assets;assets",
    "--specpath", (Join-Path $BuildRoot "spec")
)

& $Python @PlayerArgs `
    "--name" "联锁对抗选手赛前BP" `
    "--onefile" `
    "--distpath" (Join-Path $ReleaseRoot "选手赛前BP版") `
    "--workpath" (Join-Path $BuildRoot "player_onefile") `
    $PlayerEntryPath

$SingleReadme = @"
联锁对抗 BP 助手（单文件版）

直接双击“联锁对抗BP助手.exe”即可启动，不需要安装 Python。
首次启动需要释放内置资源，可能比文件夹版稍慢。
如果 Windows SmartScreen 提示未知发布者，请选择“更多信息”后确认运行。
若启动失败，同目录会生成“启动错误.log”。
"@
$FolderReadme = @"
联锁对抗 BP 助手（绿色文件夹版）

请保持整个“联锁对抗BP助手_文件夹版”文件夹完整，
双击文件夹内的“联锁对抗BP助手_文件夹版.exe”启动。
不需要安装 Python，启动速度通常快于单文件版。
若启动失败，程序目录会生成“启动错误.log”。
"@
$PlayerReadme = @"
联锁对抗 · 选手赛前 BP（独立单文件版）

直接双击“联锁对抗选手赛前BP.exe”即可启动，不需要安装 Python。
本版本仅包含选手赛前 BP 界面，红蓝双方可在同一界面即时 Ban / Pick，
数量不设上限。可通过顶部按钮导入主办方此前导出的 .bpmatch 比赛配置。

导入后：
1. 全局 Ban 会在左侧干员卡片上标记，不会计入右侧“选手 BAN”。
2. 主持人 Ban 会恢复到右侧“选手 BAN”。
3. 配置内分支 Ban 与双方选手名称会同时恢复。

若启动失败，同目录会生成“选手赛前BP_启动错误.log”。
"@
Set-Content -LiteralPath (Join-Path $ReleaseRoot "单文件版\使用说明.txt") -Value $SingleReadme -Encoding UTF8
Set-Content -LiteralPath (Join-Path $ReleaseRoot "绿色文件夹版\使用说明.txt") -Value $FolderReadme -Encoding UTF8
Set-Content -LiteralPath (Join-Path $ReleaseRoot "选手赛前BP版\使用说明.txt") -Value $PlayerReadme -Encoding UTF8

Write-Host "发布版本已生成：$ReleaseRoot"

