@echo off

set GIT=git\\cmd\\git.exe
set PYTHON=py310\\python.exe
set PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128

%PYTHON% api.py --precision fp16 --model-path "./model/chatglm-6b-int4-qe"

pause
exit /b