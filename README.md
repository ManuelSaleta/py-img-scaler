# Project:
A python application that uses GenAI for image upscaling.

## Structure:
```text
PyImgScaler/
│
├── pyimgscaler/               # Source root package
│   ├── __init__.py            # Exposes package version and metadata
│   ├── config/
│   │   ├── __init__.py
│   │   └── logging_config.py  # Structured log formatting
│   └── core/
│       ├── __init__.py
│       └── upscaler.py        # The AI processing engine
│
├── tests/                     # Unit test files
│   └── __init__.py
│
├── main.py                    # Application Entrypoint
├── requirements.txt           # Dependency management
├── upscaler.log               # Generated application logs
└── README.md                  # Project documentation
```