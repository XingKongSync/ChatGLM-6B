from fastapi import FastAPI, Request
from transformers import AutoTokenizer, AutoModel
import uvicorn, json, datetime
from options import parser
from starlette.responses import StreamingResponse

cmd_opts = parser.parse_args()

app = FastAPI()


@app.post("/")
async def create_item(request: Request):
    global model, tokenizer
    json_post_raw = await request.json()
    json_post = json.dumps(json_post_raw)
    json_post_list = json.loads(json_post)
    prompt = json_post_list.get('prompt')
    history = json_post_list.get('history')
    response, history = model.chat(tokenizer, prompt, history=history)
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    answer = {
        "response": response,
        "history": history,
        "status": 200,
        "time": time
    }
    log = "[" + time + "] " + '", prompt:"' + prompt + '", response:"' + repr(response) + '"'
    print(log)
    return answer


@app.post("/stream")
async def stream(request: Request):
    global model, tokenizer
    json_post_raw = await request.json()
    json_post = json.dumps(json_post_raw)
    json_post_list = json.loads(json_post)
    prompt = json_post_list.get('prompt')
    history = json_post_list.get('history')
    def event_stream():
        nonlocal history  # 将外层函数的 history 变量声明为 nonlocal，使其可以在内层函数中修改
        for response, new_history in model.stream_chat(tokenizer, prompt, history=history):
            history = new_history  # 将新的 history 变量值赋给外层的 history 变量
            query, response = history[-1]
            jsonResponse = {'message': response}
            jsonResponse = json.dumps(jsonResponse)
            # 生成 SSE 格式的响应
            event = f"data: {jsonResponse}\n\n"
            # 发送事件响应
            yield event

    # 返回 StreamingResponse 类型的响应
    return StreamingResponse(event_stream(), media_type="text/event-stream")


if __name__ == '__main__':
    uvicorn.run('api:app', host='0.0.0.0', port=8000, workers=1)

tokenizer = AutoTokenizer.from_pretrained(cmd_opts.model_path, trust_remote_code=True)
model = AutoModel.from_pretrained(cmd_opts.model_path, trust_remote_code=True)

def prepare_model():
    global model
    if cmd_opts.cpu:
        model = model.float()
    else:
        if cmd_opts.precision == "fp16":
            model = model.half().cuda()
        elif cmd_opts.precision == "int4":
            model = model.half().quantize(4).cuda()
        elif cmd_opts.precision == "int8":
            model = model.half().quantize(8).cuda()

    model = model.eval()

prepare_model()


def test():
    try:
        global model, tokenizer
        model.chat(tokenizer, "1+1=?", [])
    except Exception as e:
        print(e)

test()
