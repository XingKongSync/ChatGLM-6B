# ChatGLM-6B


## 介绍

ChatGLM-6B 是一个开源的、支持中英双语的对话语言模型，详情请参见[原代码仓库](https://github.com/THUDM/ChatGLM-6B)。

在此仓库的代码中，我对原来的`api.py`进行了修改，参考了官方的`web_demo2.py`，新增了 StreamChat 接口，方便在前端实现打字机效果

## 接口调用示例

```go
const (
	STREAM_API_URL = "http://127.0.0.1:8000/stream"
)

type ChatGLM struct {
	History   [][]string
	Timestamp time.Time
}

type ApiStreamPromptResponse struct {
	Message string `json:message`
}

func (glm *ChatGLM) createRequestJson(prompt string) ([]byte, error) {
	request := ApiPromptRequest{
		Prompt:  prompt,
		History: glm.History,
	}
	jsonData, err := json.Marshal(request)

	if err != nil {
		return nil, err
	}

	return jsonData, nil
}

func (glm *ChatGLM) StremPrompt(prompt string) {
	//构造请求
	jsonData, err := glm.createRequestJson(prompt)

	if err != nil {
		handleErr(err, "创建 JSON 失败：")
		return
	}

	//发送请求
	resp, err := http.Post(STREAM_API_URL, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		handleErr(err, "请求 ChatGLM 时发生错误：")
		return
	}
	defer resp.Body.Close()

	//读取响应
	if resp.StatusCode != http.StatusOK {
		errMsg := "请求 ChatGLM 时发生错误：" + resp.Status
		fmt.Println(errMsg)
	}
    
    historyBuff := new(bytes.Buffer)
	buffer := make([]byte, 1024)
	for {
		n, err := resp.Body.Read(buffer)
		if err == nil {
			slice := buffer[:n]
			historyBuff.Write(slice)
             fmt.Println(slice)
		} else {
			break
		}
	}
}
```

