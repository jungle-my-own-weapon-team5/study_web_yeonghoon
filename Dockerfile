FROM --platform=linux/amd64 ubuntu:24.04

ENV TZ=Asia/Seoul LANG=ko_KR.UTF-8 LANGUAGE=ko_KR.UTF-8

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV LANG=ko_KR.UTF-8
ENV LANGUAGE=ko_KR:ko
ENV LC_ALL=ko_KR.UTF-8

WORKDIR /app

# 기본 패키지 + PostgreSQL + Python + 한글 + vim 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gnupg \
    git \
    bash \
    vim \
    build-essential \
    gcc \
    make \
    python3 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    postgresql-server-dev-16 \
    locales \
    language-pack-ko \
    fonts-noto-cjk \
    dos2unix \
    && locale-gen ko_KR.UTF-8 \
    && update-locale LANG=ko_KR.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

# Node.js 24 + yarn 설치
RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get update \
    && apt-get install -y nodejs \
    && corepack enable \
    && corepack prepare yarn@stable --activate \
    && node -v \
    && npm -v \
    && yarn -v \
    && rm -rf /var/lib/apt/lists/*

# pgvector 설치
RUN git clone --depth 1 https://github.com/pgvector/pgvector.git /tmp/pgvector \
    && cd /tmp/pgvector \
    && make \
    && make install \
    && rm -rf /tmp/pgvector

# Python 가상환경
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 백엔드 의존성 설치
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/backend/requirements.txt

# 프론트 의존성 설치
COPY frontend/package*.json /app/frontend/
WORKDIR /app/frontend
RUN npm install

# 소스 복사
WORKDIR /app
COPY backend /app/backend
COPY frontend /app/frontend
COPY db /app/db
COPY start.sh /app/start.sh

# Windows 줄바꿈 방지 + 실행권한
RUN dos2unix /app/start.sh \
    && chmod +x /app/start.sh

EXPOSE 5173
EXPOSE 8000
EXPOSE 5432
EXPOSE 6274
EXPOSE 6277

CMD ["bash", "/app/start.sh"]