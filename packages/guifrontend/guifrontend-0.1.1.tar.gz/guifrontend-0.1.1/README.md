# GUI数据采集框架 - 前端

## 功能
- 连接后端WebSocket服务
- 定期截图并发送给后端  
- 执行后端返回的PyAutoGUI代码

## 安装
```bash
pip install -r requirements.txt
```

## 配置
编辑 `config/config.yaml`:
```yaml
backend:
  host: "127.0.0.1"  # 后端IP地址
  port: 8000
frontend:
  id: "frontend_001"
  screenshot_interval: 2.0
```

## 运行
```bash
python run_frontend.py --config config/config.yaml
```

## 通信协议

发送给后端:
```json
{"type": "screenshot", "screenshot": "base64_image"}
```

接收自后端:
```json
{"type": "execute_action", "pyautogui_code": "pyautogui.click(100, 200)"}
``` 