# 실시간 인체 포즈 추정 시스템

이 프로젝트는 MediaPipe 기반으로 실시간으로 인체의 포즈를 감지하고 분석하는 시스템입니다. 33개의 신체 랜드마크를 정확하게 추적하며, 웹캠을 통한 실시간 분석과 비디오 파일 처리 모두 지원합니다.

## 주요 기능

- **실시간 포즈 추정**: 웹캠을 통해 사용자의 동작을 실시간으로 감지하고 33개의 신체 랜드마크를 추적
- **자세 교정 피드백**: 올바른 자세 기준과 비교하여 실시간으로 피드백 제공
- **운동 카운팅**: 스쿼트, 푸시업, 런지 등 다양한 운동 동작 인식 및 자동 카운팅
- **동작 분류**: 사용자의 움직임 패턴을 분석하여 운동 종류 자동 분류
- **웹 인터페이스**: Flask 기반 웹 서버를 통해 사용자 친화적인 인터페이스 제공

## 설치 방법

### 요구 사항
- Python 3.7 이상
- 웹캠

### 설치

1. 저장소 클론
```bash
git clone https://github.com/yourusername/realtime-pose-estimation.git
cd realtime_pose_estimation
```

2. 가상 환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

## 사용 방법

1. 웹 서버 실행
```bash
python app.py
```

2. 웹 브라우저에서 `http://localhost:5000` 접속

3. 웹캠이 자동으로 활성화되어 실시간 포즈 추정 시작

4. 운동 종류 선택 드롭다운 메뉴에서 분석하고자 하는 운동 선택

## 커스터마이징

### 새로운 운동 추가
`app.py` 파일에서 새로운 운동 카운팅 함수를 추가할 수 있습니다:

```python
def count_pushups(landmarks):
    # 푸시업 동작 감지 및 카운팅 로직
    pass
```

### 자세 정확도 기준 수정
`calculate_posture_score` 함수에서 자세 평가 기준을 수정할 수 있습니다:

```python
def calculate_posture_score(landmarks):
    # 자세 점수 계산 로직 수정
    pass
```

## 기술 스택

- **Python**: 핵심 로직 및 서버 개발
- **MediaPipe**: 인체 포즈 추정 ML 모델
- **OpenCV**: 컴퓨터 비전 및 이미지 처리
- **Flask**: 웹 서버 및 API 제공
- **HTML/CSS/JavaScript**: 웹 인터페이스

## 한국인 체형 최적화

자체 데이터셋을 구축하여 한국인의 체형에 맞는 모델 최적화를 진행했습니다. 이를 통해 다양한 체형과 동작 패턴에 대해서도 높은 정확도의 포즈 추정이 가능합니다.

## 응용 분야

- 스포츠 코칭 및 분석
- 피트니스 모니터링
- 물리치료 및 재활
- 동작 분석 연구
