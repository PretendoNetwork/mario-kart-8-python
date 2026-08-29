FROM python:3.11-slim

# Build tools for the few deps without prebuilt wheels (netifaces, cffi, ...).
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies into a dedicated virtualenv rather than the system
# interpreter's site-packages.
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install "setuptools<81" wheel && \
    pip install -r requirements.txt

COPY . .

# Generate the gRPC stubs (amkj_service_pb2*.py) that main.py imports.
RUN python -m grpc_tools.protoc \
        --proto_path=grpc \
        --python_out=. \
        --grpc_python_out=. \
        grpc/amkj_service.proto

CMD ["python", "main.py"]
