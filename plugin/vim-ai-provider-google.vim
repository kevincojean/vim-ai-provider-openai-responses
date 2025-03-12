let g:vim_ai_google_config = {
\  "model": "gemini-2.0-flash",
\  "endpoint_url": "https://generativelanguage.googleapis.com/v1beta/models",
\  "request_timeout": 20,
"\ optional fields:
"\  "token_file_path": "~/.config/gemini.token",
"\  "temperature": 1.0,
"\  "max_output_tokens": 800,
"\  "top_p": 0.8,
"\  "top_k": 10,
\}

let s:plugin_root = expand('<sfile>:p:h:h')

cal vim_ai_provider#Register('google', {
\  'script_path': s:plugin_root . '/py/google.py',
\  'class_name': 'GoogleAIProvider',
\})
