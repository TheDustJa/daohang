param(
    [string]$PackageName = "nav-stack-release"
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$ReleaseRoot = Join-Path $Root "release"
$BundleDir = Join-Path $ReleaseRoot $PackageName
$ImageDir = Join-Path $BundleDir "images"
$DeployDir = Join-Path $BundleDir "deploy"
$ArchivePath = Join-Path $ReleaseRoot "$PackageName.zip"

New-Item -ItemType Directory -Force -Path $ReleaseRoot | Out-Null
if (Test-Path $BundleDir) {
    Remove-Item -Recurse -Force $BundleDir
}
New-Item -ItemType Directory -Force -Path $ImageDir | Out-Null
New-Item -ItemType Directory -Force -Path $DeployDir | Out-Null

Push-Location $Root
try {
    docker build -t nav-backend:release .\pybackground
    docker build -t nav-frontend:release .\web

    docker save -o (Join-Path $ImageDir "nav-backend-release.tar") nav-backend:release
    docker save -o (Join-Path $ImageDir "nav-frontend-release.tar") nav-frontend:release

    Copy-Item .\deploy\compose.prod.yml $DeployDir
    Copy-Item .\deploy\.env.prod.example $DeployDir
    Copy-Item .\deploy\server-deploy.sh $DeployDir
    Copy-Item .\deploy\install.sh $BundleDir
    Copy-Item .\deploy\README.md $DeployDir

    if (Test-Path $ArchivePath) {
        Remove-Item -Force $ArchivePath
    }
    tar.exe -a -c -f $ArchivePath -C $ReleaseRoot $PackageName
}
finally {
    Pop-Location
}

Write-Host "Release package created:"
Write-Host $ArchivePath
