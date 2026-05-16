# tools/sign_release.ps1
# Authenticode-signs Vibrante-Node.exe to remove "Unknown publisher" from Windows security dialogs.
#
# Prerequisites:
#   signtool.exe  - from Windows SDK (auto-detected)
#   A code signing certificate in Cert:\CurrentUser\My or Cert:\LocalMachine\My
#
# Certificate options:
#   Self-signed (dev/testing - does NOT satisfy SmartScreen):
#     powershell -ExecutionPolicy Bypass -File tools\create_dev_cert.ps1
#   Commercial OV cert (~$100-200/yr, removes Unknown publisher after ~100 clean downloads):
#     https://www.digicert.com/signing/code-signing-certificates
#   Commercial EV cert (~$300-500/yr, removes Unknown publisher immediately):
#     https://www.digicert.com/signing/ev-code-signing-certificates
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File tools\sign_release.ps1
#   powershell -ExecutionPolicy Bypass -File tools\sign_release.ps1 -Thumbprint "ABCDEF..."
#   powershell -ExecutionPolicy Bypass -File tools\sign_release.ps1 -ExePath "path\to\exe"

param(
    [string]$Thumbprint   = "",
    [string]$ExePath      = "dist\Vibrante-Node\Vibrante-Node.exe",
    [string]$TimestampUrl = "http://timestamp.digicert.com"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# --- Locate signtool.exe ---------------------------------------------------
function Find-Signtool {
    $candidates = @(
        "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\signtool.exe",
        "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe",
        "C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\signtool.exe",
        "C:\Program Files (x86)\Windows Kits\10\bin\x64\signtool.exe",
        "C:\Program Files (x86)\Windows Kits\8.1\bin\x64\signtool.exe"
    )
    foreach ($p in $candidates) {
        if (Test-Path $p) { return $p }
    }
    $found = Get-ChildItem "C:\Program Files (x86)\Windows Kits" `
                -Recurse -Filter "signtool.exe" -ErrorAction SilentlyContinue |
             Where-Object { $_.FullName -like "*\x64\*" } |
             Select-Object -First 1
    if ($found) { return $found.FullName }
    return $null
}

$signtool = Find-Signtool
if (-not $signtool) {
    Write-Host "signtool.exe not found." -ForegroundColor Red
    Write-Host "Install the Windows SDK: https://developer.microsoft.com/windows/downloads/windows-sdk/"
    exit 1
}
Write-Host "signtool : $signtool"

# --- Locate certificate ----------------------------------------------------
if ($Thumbprint -ne "") {
    $cert = Get-Item "Cert:\CurrentUser\My\$Thumbprint" -ErrorAction SilentlyContinue
    if (-not $cert) {
        $cert = Get-Item "Cert:\LocalMachine\My\$Thumbprint" -ErrorAction SilentlyContinue
    }
    if (-not $cert) {
        Write-Host "Certificate '$Thumbprint' not found in CurrentUser\My or LocalMachine\My." -ForegroundColor Red
        exit 1
    }
} else {
    $userCerts    = @(Get-ChildItem Cert:\CurrentUser\My    -CodeSigningCert -ErrorAction SilentlyContinue)
    $machineCerts = @(Get-ChildItem Cert:\LocalMachine\My   -CodeSigningCert -ErrorAction SilentlyContinue)
    $certs = $userCerts + $machineCerts

    if ($certs.Count -eq 0) {
        Write-Host ""
        Write-Host "No code signing certificate found." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Dev/testing (self-signed, NOT trusted by SmartScreen):"
        Write-Host "  powershell -ExecutionPolicy Bypass -File tools\create_dev_cert.ps1"
        Write-Host ""
        Write-Host "Release (removes Unknown publisher from SmartScreen):"
        Write-Host "  Purchase an OV or EV certificate, install it, then re-run this script."
        exit 1
    }

    # Prefer CA-issued certs (issuer != subject); pick latest expiry as tiebreaker
    $caCerts = $certs | Where-Object { $_.Issuer -ne $_.Subject }
    if ($caCerts) {
        $cert = $caCerts | Sort-Object NotAfter -Descending | Select-Object -First 1
        $certType = "CA-issued"
    } else {
        $cert = $certs | Sort-Object NotAfter -Descending | Select-Object -First 1
        $certType = "self-signed (dev only)"
    }
    Write-Host "certificate: $($cert.Subject) [$($cert.Thumbprint)] ($certType)"
}

# --- Verify exe exists -----------------------------------------------------
if (-not (Test-Path $ExePath)) {
    Write-Host "Exe not found: $ExePath" -ForegroundColor Red
    Write-Host "Run PyInstaller first: pyinstaller vibrante_node.spec"
    exit 1
}

# --- Sign ------------------------------------------------------------------
Write-Host "signing  : $ExePath"
Write-Host "timestamp: $TimestampUrl"
Write-Host ""

$signArgs = @(
    "sign",
    "/sha1", $cert.Thumbprint,
    "/fd",   "sha256",
    "/tr",   $TimestampUrl,
    "/td",   "sha256",
    "/d",    "Vibrante-Node Pipeline Editor",
    "/du",   "https://vibrante-node.com",
    $ExePath
)
& $signtool @signArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host "signtool sign failed (exit $LASTEXITCODE)." -ForegroundColor Red
    exit 1
}

# --- Verify ----------------------------------------------------------------
Write-Host ""
& $signtool verify /pa /v $ExePath

# --- Summary ---------------------------------------------------------------
$sig = Get-AuthenticodeSignature $ExePath
Write-Host ""

if ($sig.Status -eq "Valid") {
    Write-Host "Result: $($sig.Status)" -ForegroundColor Green
} else {
    Write-Host "Result: $($sig.Status)" -ForegroundColor Yellow
}
Write-Host "Signer  : $($sig.SignerCertificate.Subject)"
Write-Host "Issuer  : $($sig.SignerCertificate.Issuer)"
Write-Host ""

if ($sig.SignerCertificate.Issuer -eq $sig.SignerCertificate.Subject) {
    Write-Host "NOTE: Signed with a self-signed certificate." -ForegroundColor Yellow
    Write-Host "      SmartScreen still blocks this exe for other users." -ForegroundColor Yellow
    Write-Host "      For public releases use a commercial OV or EV certificate." -ForegroundColor Yellow
} else {
    Write-Host "Signed with a CA certificate." -ForegroundColor Green
    Write-Host "SmartScreen trust builds with download reputation (OV) or is immediate (EV)." -ForegroundColor Green
}
