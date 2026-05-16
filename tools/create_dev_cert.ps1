# tools/create_dev_cert.ps1
# Creates a self-signed code signing certificate for LOCAL DEVELOPMENT / TESTING ONLY.
#
# What this fixes:
#   - Windows Security Warning dialog: "Unknown publisher" -> "Vibrante-Node Dev"
#   - File Properties > Digital Signatures: shows the certificate
#
# What this does NOT fix:
#   - Windows SmartScreen ("Windows protected your PC") for other users
#     => Requires a commercial OV or EV certificate: tools\sign_release.ps1
#
# Usage (run as current user, no elevation required):
#   powershell -ExecutionPolicy Bypass -File tools\create_dev_cert.ps1

$subjectCN  = "Vibrante-Node Dev"
$validYears = 3

# Check for existing dev cert to avoid duplicates
$existing = Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert |
    Where-Object { $_.Subject -eq "CN=$subjectCN, O=Vibrante-Node, C=US" } |
    Select-Object -First 1

if ($existing) {
    Write-Host "Dev certificate already exists."
    Write-Host "  Subject:    $($existing.Subject)"
    Write-Host "  Thumbprint: $($existing.Thumbprint)"
    Write-Host "  Expires:    $($existing.NotAfter)"
    Write-Host ""
    Write-Host "To sign: powershell -ExecutionPolicy Bypass -File tools\sign_release.ps1 -Thumbprint $($existing.Thumbprint)"
    exit 0
}

# Create the cert
$cert = New-SelfSignedCertificate `
    -Subject            "CN=$subjectCN, O=Vibrante-Node, C=US" `
    -Type               CodeSigningCert `
    -CertStoreLocation  Cert:\CurrentUser\My `
    -HashAlgorithm      SHA256 `
    -KeyUsage           DigitalSignature `
    -KeyLength          2048 `
    -NotAfter           (Get-Date).AddYears($validYears)

Write-Host "Created self-signed code signing certificate:"
Write-Host "  Subject:    $($cert.Subject)"
Write-Host "  Thumbprint: $($cert.Thumbprint)"
Write-Host "  Expires:    $($cert.NotAfter)"
Write-Host ""

# Add to Trusted Root so the local machine trusts it
# This makes Windows show "Vibrante-Node Dev" instead of "Unknown publisher" locally.
# Scoped to CurrentUser only -- does not affect other users on this machine.
$rootStore = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root", "CurrentUser")
$rootStore.Open("ReadWrite")
$rootStore.Add($cert)
$rootStore.Close()
Write-Host "Added to CurrentUser\Trusted Root CA for local trust."
Write-Host ""
Write-Host "To sign the exe:"
Write-Host "  powershell -ExecutionPolicy Bypass -File tools\sign_release.ps1 -Thumbprint $($cert.Thumbprint)"
Write-Host ""
Write-Host "NOTE: Self-signed certs do NOT satisfy Windows SmartScreen for other users."
Write-Host "      For public releases use a commercial OV or EV certificate."
