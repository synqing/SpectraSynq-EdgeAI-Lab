# RUHMI/MERA compiler image. linux/amd64 + CPython 3.10 only.
# Build: docker build --platform linux/amd64 -t spectrasynq-ruhmi:2.6.0 deployment/ra8p1
FROM --platform=linux/amd64 ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.10 python3.10-venv python3.10-dev python3-pip \
        build-essential cmake git wget ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN python3.10 -m venv /opt/mera-env
ENV PATH=/opt/mera-env/bin:$PATH

RUN pip install --upgrade pip \
 && pip install decorator typing_extensions psutil attrs pybind11 cmake junitparser \
        numpy onnx==1.17.0 tflite==2.18.0

# Pinned to the wheel named in ruhmi-framework-mcu/install/README.md (2026-08).
ARG MERA_WHEEL=mera-2.6.0+pkg.4815-cp310-cp310-manylinux_2_27_x86_64.whl
RUN wget -q "https://github.com/renesas/ruhmi-framework-mcu/raw/main/install/${MERA_WHEEL}" \
 && pip install "${MERA_WHEEL}" \
 && rm "${MERA_WHEEL}" \
 && python -c "import mera; print('mera', mera.__version__)"

RUN git clone --depth 1 https://github.com/renesas/ruhmi-framework-mcu.git /opt/ruhmi-framework-mcu

WORKDIR /work
COPY compile_entrypoint.py /opt/compile_entrypoint.py
ENTRYPOINT ["/opt/mera-env/bin/python", "/opt/compile_entrypoint.py"]
