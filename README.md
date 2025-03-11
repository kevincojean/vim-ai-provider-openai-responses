# vim-ai provider google

[vim-ai](https://github.com/madox2/vim-ai) provider plugin for Google's Gemini models.

## Installation

`vim-ai-provider-google` extension have to be installed after `vim-ai`

```vim
" this feature is still in development
Plug 'madox2/vim-ai', { 'branch': 'provider-extensions' }
Plug 'madox2/vim-ai-provider-google'
```

### API key

Export API key as an environment variable:

```sh
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

or using `token_file_path` configuration:

```ini
options.token_file_path = ~/.config/gemini.token
```

## Configuration

You can configure a custom role or use vim-ai's configuration variables `g:vim_ai_complete`, `g:vim_ai_edit`, `g:vim_ai_chat`.

```ini
[gemini]
provider = google
# default fields
options.model = gemini-2.0-flash
options.endpoint_url = https://generativelanguage.googleapis.com/v1beta/models
options.request_timeout = 20
# optional fields
options.token_file_path = ~/.config/gemini.token
options.temperature = 1.0
options.max_output_tokens = 800
options.top_p = 0.8
options.top_k = 10
# inherited options from vim-ai
options.selection_boundary = ...
options.initial_prompt = ...
```

## License

[MIT License](https://github.com/madox2/vim-ai-google-provider/blob/main/LICENSE)
