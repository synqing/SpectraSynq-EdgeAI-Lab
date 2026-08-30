# RUHMI/MERA compiler image. linux/amd64 + CPython 3.10.
# Pin: ruhmi-framework-mcu 6c5aad9 (Release-2026-06-19) / MERA 2.6.0+pkg.4815
# GLIBCXX: follow Renesas Ubuntu recipe (toolchain-r/test + gcc-13).
FROM --platform=linux/amd64 ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    RUHMI_REF=6c5aad9

RUN apt-get update && apt-get install -y --no-install-recommends \
        software-properties-common ca-certificates \
    && add-apt-repository -y ppa:ubuntu-toolchain-r/test \
    && apt-get update \
    && apt-get install -q -y --only-upgrade libstdc++6 libgcc-s1 \
    && apt-get install -y --no-install-recommends \
        python3.10 python3.10-venv python3.10-dev python3-pip \
        build-essential cmake git wget gcc-13 g++-13 \
    && rm -rf /var/lib/apt/lists/*

RUN python3.10 -m venv /opt/mera-env
ENV PATH=/opt/mera-env/bin:$PATH

RUN pip install --upgrade pip \
 && pip install decorator typing_extensions psutil attrs pybind11 cmake junitparser \
        numpy onnx==1.17.0 tflite==2.18.0

ARG MERA_WHEEL=mera-2.6.0+pkg.4815-cp310-cp310-manylinux_2_27_x86_64.whl
RUN wget -q "https://github.com/renesas/ruhmi-framework-mcu/raw/${RUHMI_REF}/install/${MERA_WHEEL}" \
 && pip install "${MERA_WHEEL}" \
 && rm "${MERA_WHEEL}" \
 && python -c "import mera; print('mera', mera.__version__)"

RUN git clone https://github.com/renesas/ruhmi-framework-mcu.git /opt/ruhmi-framework-mcu \
 && git -C /opt/ruhmi-framework-mcu checkout --detach ${RUHMI_REF}

WORKDIR /work
COPY compile_entrypoint.py /opt/compile_entrypoint.py
ENTRYPOINT ["/opt/mera-env/bin/python", "/opt/compile_entrypoint.py"]
