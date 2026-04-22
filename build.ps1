# Docker 이미지 빌드 및 배포 스크립트 (PowerShell)

param(
    [string]$ImageTag = "latest",
    [switch]$Test,
    [switch]$Push
)

$ErrorActionPreference = "Stop"

# 환경 변수 설정
$ProjectId = $env:GCP_PROJECT_ID ?? "your-project-id"
$Region = $env:GCP_REGION ?? "asia-northeast1"
$ImageName = "architect-chatbot"
$Registry = "gcr.io"
$FullImageName = "${Registry}/${ProjectId}/${ImageName}:${ImageTag}"

Write-Host "=========================================="
Write-Host "Docker 이미지 빌드 시작" -ForegroundColor Green
Write-Host "=========================================="
Write-Host "이미지명: $FullImageName"
Write-Host ""

# Docker 이미지 빌드
Write-Host "[1/3] Docker 이미지 빌드 중..." -ForegroundColor Cyan
docker build -t $FullImageName -f Dockerfile .

# 로컬 테스트
if ($Test) {
    Write-Host "[2/3] 로컬 테스트 중... (http://localhost:7860)" -ForegroundColor Cyan
    $container = docker run -d -p 7860:7860 $FullImageName
    Start-Sleep -Seconds 10
    docker stop $container | Out-Null
    docker rm $container | Out-Null
}
else {
    Write-Host "[2/3] 테스트 스킵 (-Test 옵션 추가로 로컬 테스트 가능)" -ForegroundColor Yellow
}

# GCR에 푸시
if ($Push) {
    Write-Host "[3/3] GCR에 이미지 푸시 중..." -ForegroundColor Cyan
    docker push $FullImageName
    Write-Host "✓ 이미지가 성공적으로 푸시되었습니다." -ForegroundColor Green
}
else {
    Write-Host "[3/3] 푸시 스킵 (-Push 옵션 추가로 GCR에 푸시 가능)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=========================================="
Write-Host "✓ Docker 이미지 빌드 완료!" -ForegroundColor Green
Write-Host "=========================================="
Write-Host ""
Write-Host "사용 가능한 명령어:" -ForegroundColor Cyan
Write-Host "  로컬 실행:        docker run -p 7860:7860 $FullImageName"
Write-Host "  GCR 푸시:        ./build.ps1 -ImageTag $ImageTag -Push"
Write-Host "  빌드 및 테스트:  ./build.ps1 -ImageTag $ImageTag -Test"
Write-Host ""
